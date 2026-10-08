# Cache Safety & Token Efficiency (Claude Code)

*How instruction-file design decisions interact with Claude Code's prompt cache. Verified 2026-06-10 against the official CC docs (code.claude.com: prompt-caching, model-config, skills frontmatter reference), the platform API caching docs, and the CC v2.1.170 binary. Fork rows re-verified 2026-08-14 against the current sub-agents / skills / prompt-caching docs plus a live fork test. Effort-key exception and Opus 5.5 notes verified 2026-09-24 against the prompt-caching and model-config docs; Sonnet 5.5 added to the effort-key exception, re-verified 2026-09-29; Haiku 5.5 added, 2026-10-08.*

## The cache model in one paragraph

Every CC turn re-sends the full context (system prompt → project context → conversation); the API caches by **exact prefix match**, so on a normal turn only the newest exchange is processed. Two settings sit outside the prompt text but ARE part of the cache key: **model** ("each model has its own cache") and, **on most models, effort** ("each effort level has its own cache"). Changing either mid-session recomputes the entire request — this is why `/model` and `/effort` show confirmation dialogs once a conversation has prior output. **Exception:** on Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 with an API key or a Claude subscription, changing effort keeps the cache and Claude Code applies it without asking; this does not hold on Amazon Bedrock, Google Cloud's Agent Platform, a Claude apps gateway, with `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`, or under a HIPAA configuration (Fable 5.1 from v2.1.260). A model change always recomputes. TTL: **1 hour** on the main thread under a Claude subscription (5 minutes on API keys / third-party providers); **subagents always use the 5-minute TTL** and build their own cache.

## Main-thread model/effort pins: the double cache-bust

A skill's or command's `model:` / `effort:` frontmatter overrides the **main conversation** for the rest of the current turn, then reverts on the next user prompt (CC skills frontmatter reference). With C tokens of accumulated history:

| Step | What happens | Cost shape |
|---|---|---|
| Skill activates | the (pinned model, pinned effort) cache key is cold → **full C-token uncached re-read** at the pinned model's input rate, then a cache write | the slow, expensive turn |
| Remaining requests in the turn | read the fresh cache under the pinned key | cheap |
| Next user prompt (revert) | the old (session model, session effort) entry is still warm within TTL → old prefix reads at 0.1×; **the skill-era turns are new uncached content** at session-model rates | second, smaller hit |

**Worked example** (200K-token history, Fable 5 session, a skill pinned `opus` + `low`, API rates): entry ≈ 200K × $5/M = **$1.00** uncached plus the cache-write premium; exit ≈ 200K × $0.25/M cache read on Fable 5.1 ($1/M on Fable 5) plus the skill-era turns at $10/M. The pin saves only the skill's own marginal work — typically $0.10–0.20. **Net loss in any long session.** A main-thread pin pays off only when the conversation is short or the skill itself processes very large volume on the cheaper model — measure before assuming.

Nuances:

- **Effort-only pins are not the cheap version** (except on Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 on first-party auth, where an effort change keeps the cache) — elsewhere the same double bust, and the entry re-read bills at the *active* model's rate (in a Fable 5 session, an `effort: low`-only pin re-reads at $10/M — twice what the opus-pin's entry costs for the same mistake).
- **A pin that resolves to the already-active level keeps the cache** (documented no-op) — e.g. `effort: high` in a session already at the default.
- **Fable 5.x's automatic safety fallback (Opus 4.8 for cyber, Opus 5 for bio) is also a model switch** (full re-read) — outside the author's control, but it explains surprise slow turns in security-/bio-adjacent sessions.

## The safe patterns

| Pattern | Cache impact | Use |
|---|---|---|
| **No pin (inherit)** | none — skill invocation appends a user message; nothing earlier changes | DEFAULT for every main-thread skill/command |
| **Pin on an AGENT** (`agents/*.md`) | none on the main thread — agents always execute as subagents with their own conversation and own cache (5m TTL) | the natural home for model/effort pins |
| **Pinned skill forced into a subagent** (`context: fork` + `agent:`) | parent cache untouched; the skill body seeds a FRESH subagent with NO conversation history (official: "It won't have access to your conversation history"), so the pin runs against a short cold prefix — no exit re-read, no parent pollution | the standard home for a pinned skill |
| **Pinned skill/command on the main thread** | double cache-bust per invocation (table above) | the anti-pattern — avoid |

**Rule: a skill or command with a hardcoded `model:` or `effort:` must always run as a subagent.** The effort exception on Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 does not relax this: a skill cannot know its user's model or route, and a `model:` pin busts the cache everywhere. Either author it as an agent, or set `context: fork` (+ `agent:`) in the same frontmatter so the pin can never touch the main conversation's cache. A main-thread pin is never "free": it taxes the entire session to discount one skill.

(`CLAUDE_CODE_SUBAGENT_MODEL` is the operator-side equivalent — it overrides all subagent models without touching the main thread.)

**Correction (2026-08-14):** an earlier revision of the table above claimed a `context: fork` skill inherits the full conversation history. Wrong — that behaviour belongs to conversation forks (next section); `context: fork` subagents start fresh, which is precisely why they are the cache-safe home for pins. A pinned forked skill that needs conversation facts must receive them explicitly in its invocation arguments.

## Conversation forks (`subagent_type: "fork"` / `/subtask`) and the cache

A conversation fork inherits the parent's system prompt, tools, and history **byte-identically**, so its first request reads the parent's cache at the 0.1× rate — officially "cheaper than spawning a fresh subagent for tasks that need the same context". A named subagent starts cold on its own cache (5-minute TTL) and never reads the parent's.

- **Floor cost ≈ parent context size at parent-model (cache-read) rates.** Measured live 2026-08-14: a trivial fork in a long session consumed ~151k tokens to return 120 words with zero tool calls. Cheap *relative to* rebuilding equivalent context cold; never cheap in absolute terms — don't fork small tasks.
- **Forks cannot be model- or effort-pinned** — `model` overrides are ignored, and forks are runtime-only (no frontmatter). The cache-sharing and cheap-model levers are mutually exclusive: cache reuse requires a byte-identical prefix on the same model; a cheaper model requires a named subagent's cold start.
- **Fable 5.1 changes the dollars, not the rule.** A fork's cache read bills at $0.25/M on 5.1, so the measured 151k-token trivial fork costs about $0.04 in cache reads rather than $0.15. The token count a subscription plan meters is unchanged, so keep the don't-fork-small-tasks rule in token terms, not dollar terms.
- **Decision rule:** fork when context-transfer cost is the problem being solved (re-briefing would be long or lossy, or several approaches should launch from the same starting point); named pinned subagent when volume or model cost is the constraint.

## Other authoring decisions with cache consequences

All verified against the CC prompt-caching doc:

- **Skill body size.** Invocation appends the body as a user message — cache-safe, but the body then rides in the prefix and is paid for (at 0.1× when cached) on every subsequent turn of the session. Progressive disclosure — lean SKILL.md, load-on-demand `references/` — is a token-efficiency rule, not just a style rule.
- **Hooks, commands, agents, and plugin-provided skills** never invalidate — anything they add is appended after the existing conversation.
- **MCP servers** a skill depends on: deferred tools (the default via tool search) append safely; tools loaded **into the prefix** (`alwaysLoad`, tool-search unavailable/disabled) invalidate the entire cache whenever the server connects, disconnects, or changes its tool list mid-session. Prefer deferred loading in skill designs.
- **CLAUDE.md edits mid-session** don't invalidate the cache — but also don't apply until `/clear`, `/compact`, or restart. Never author instructions that assume mid-session CLAUDE.md reloads.
- **`/compact`** rebuilds the conversation layer by design. Long-running autonomous skills should checkpoint durable state to disk rather than rely on chat history, which bounds what compaction can cost them.

## Fable 5.1 notes (2026-09-01)

- **Cache reads are 0.025× base on Fable 5.1** ($0.25/MTok, against $1 on Fable 5 and $0.50 on Opus 5). That changes the dollar figures in the worked example and the fork economics above; it changes none of the doctrine, because the cache-bust still costs a full uncached re-read at the *input* rate and a subscription plan still meters tokens.
- **Claude Code now keeps the cache across effort changes on Fable 5.1** (from v2.1.260, API key or subscription; not on Bedrock, Agent Platform, a Claude apps gateway, disabled experimental betas, or HIPAA). The API equivalent is the per-message effort beta: a `role: "system"` message carrying `output_config.effort` changes effort while preserving the prompt cache on Fable 5.1, Mythos 5.1, Opus 5.5, Opus 5, and Sonnet 5.5 (not with Sonnet 5.5's `between_tools`; 400 on Fable 5). *Superseded 2026-09-24: as of 2.1.257 Claude Code had not adopted it.* The subagent-only rule for pins is unchanged.
- **Hand-built API integrations face a second cache hazard on 5.1.** Editing earlier turns now invalidates the thinking blocks that follow them as well as the cache, and for accounts created on or after 2026-08-31 that is a 400 rather than a silent cost. Keep history append-only; use turn-scoped system messages for per-turn reminders. Mechanics: the Fable 5.1 migration guide, https://platform.claude.com/docs/en/models/fable-5-1/migration-guide.

## Opus 5.5 notes (2026-09-24)

- **Cache reads are $0.20/MTok on Opus 5.5** (0.05× its $4 input; 5-minute write $5, 1-hour write $8), against $0.50 on Opus 5 and $0.25 on Fable 5.1. On the worked example above, an `opus` pin now resolves to Opus 5.5 and its entry re-read costs about 200K × $4/M = $0.80 rather than $1.00; the doctrine is unchanged.
- **Effort changes keep the cache** on first-party auth (see the cache model above). Unpinned skills and agents inherit the session effort, which defaults to `medium` on Opus 5.5, Sonnet 5.5, and Haiku 5.5. Main-thread skills and commands carry no pin; any agent or forked skill that pins `model` pins `effort` with it (routing ladder in `model-compatibility-index.md`), or it inherits the session's level, `xhigh` under an Opus oversight session.
- **Subagent `opus` under an Opus-family session** resolves to the main model's exact ID, including `[1m]`, so the subagent keeps the 1M window; it still builds its own cold cache.
- **Cache minimum is 512 tokens** (API; relevant to short system prompts in hand-built integrations).

## Haiku 5.5 notes (2026-10-08)

- **Prices depend on prompt length.** For prompts up to 100,000 tokens: input $0.10/MTok, cache reads $0.01 (the standard 0.1x multiplier; Opus 5.5 and Sonnet 5.5 use 0.05x), 5-minute write $0.125, 1-hour write $0.20. For prompts over 100,000 tokens every rate is 5x higher (input $0.50, cache reads $0.05, writes $0.625 and $1). Anthropic's sources do not say whether cached tokens count towards the 100,000.
- **Give a pinned Haiku agent a bounded input.** A subagent starts on its own cold cache and loads the user's instruction files into every prompt, so a large brief or read sweep can cross the threshold and pay the higher rate on the whole request (Haiku 5.5 file Part 3).
- **Effort changes keep the cache** on Haiku 5.5 with an API key or a Claude subscription, as on Opus 5.5, Sonnet 5.5, and Fable 5.1 (see the cache model above). The `haiku` alias is Haiku 5.5 only on the Anthropic API, so the exception never applies to a `haiku` pin on other providers.
- **Cache minimum is 512 tokens.** `DISABLE_PROMPT_CACHING_HAIKU` "applies to the default Haiku model, the model the `haiku` alias resolves to".

## Cache economics (Opus 5.5, claude.dev cost post)

Figures from "What a task costs on Opus 5.5" (claude.dev, 2026-09-25, https://claude.dev/blog/what-a-task-costs-on-opus-5-5/; Anthropic-staff byline, domain ownership not independently verified), at Opus 5.5 API rates:

- **"One write costs as much as 25 reads."** A read is 5% of input and a 5-minute write 1.25× input (1-hour 2×); at 120K tokens a 5-minute write is about $0.60 and a read about $0.02. So one avoidable cache-bust costs roughly as much as 25 cached turns (inference from the post's figures).
- **Compaction at 150K pays back in about ten turns.** It costs about $0.25, and each later turn saves about $0.025 in reads.
- **Agent teams in plan mode use "about seven times the tokens of a standard session".**
- **Sonnet 5.5 cache reads cost $0.10/MTok, half of Opus 5.5's $0.20** (lowered from $0.20 on 2026-10-07; 0.05× its $2 input, the same multiplier as Opus 5.5). Every Sonnet 5.5 rate is now half the Opus 5.5 rate, so switching a cache-read-dominated loop to Sonnet 5.5 halves the cached-input cost as well as output ($10 vs $20) and cache writes ($2.50 vs $5 for 5 minutes, $4 vs $8 for 1 hour). Re-reading a 200K-token cached history costs about $0.02 a turn on Sonnet 5.5 against $0.04 on Opus 5.5.

## Sources

- code.claude.com/docs/en/prompt-caching (re-verified 2026-09-29; effort-change exception on Opus 5.5, Sonnet 5.5, and Fable 5.1; Haiku 5.5 added to it, checked 2026-10-08) — the (model, effort) cache keys, full invalidation/keep lists, TTL policy (1h subscription main thread / 5m subagents), subagent-vs-fork cache behaviour
- code.claude.com/docs/en/sub-agents — conversation-fork definition ("inherits the entire conversation so far"), fork-vs-named comparison table, "cheaper than spawning a fresh subagent for tasks that need the same context", fork-mode defaults + `Agent(fork)` deny rule
- code.claude.com/docs/en/skills — `context: fork` runs the skill body in a fresh subagent with no conversation history; `background:` field (v2.1.218+)
- code.claude.com/docs/en/skills — frontmatter reference: `model:` override is turn-scoped on the main thread, reverts next prompt
- code.claude.com/docs/en/model-config — `/model` picker warning ("the next response re-reads the full history without cached context"); `/effort` confirmation dialog; automatic Fable→Opus fallback is a model switch
- platform.claude.com/docs/en/build-with-claude/prompt-caching — prefix matching, model-bound cache, 1.25×/2× write and 0.1× read multipliers
- CC v2.1.170 binary — `"ttl": "1h"` cache_control; "cache_control changed (scope or TTL)" miss reason
- claude.dev/blog/what-a-task-costs-on-opus-5-5 (2026-09-25) — Opus 5.5 write-vs-read and compaction arithmetic, agent-team token multiple
- platform.claude.com/docs/en/about-claude/pricing (checked 2026-10-08) — Haiku 5.5 prices by prompt length and its 0.1x cache-read multiplier
- platform.claude.com/docs/en/models/sonnet-5-5/overview — Sonnet 5.5 cache pricing ($2.50 5-minute write, $4 1-hour write)
- platform.claude.com/docs/en/release-notes/overview — 2026-10-07: Sonnet 5.5 cache reads lowered from $0.20 to $0.10 per MTok
