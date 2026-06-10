# Cache Safety & Token Efficiency (Claude Code)

*How instruction-file design decisions interact with Claude Code's prompt cache. Verified 2026-06-10 against the official CC docs (code.claude.com: prompt-caching, model-config, skills frontmatter reference), the platform API caching docs, and the CC v2.1.170 binary.*

## The cache model in one paragraph

Every CC turn re-sends the full context (system prompt → project context → conversation); the API caches by **exact prefix match**, so on a normal turn only the newest exchange is processed. Two settings sit outside the prompt text but ARE part of the cache key: **model** ("each model has its own cache") and **effort** ("each effort level has its own cache for the same model"). Changing either mid-session recomputes the entire request — this is why `/model` and `/effort` show confirmation dialogs once a conversation has prior output. TTL: **1 hour** on the main thread under a Claude subscription (5 minutes on API keys / third-party providers); **subagents always use the 5-minute TTL** and build their own cache.

## Main-thread model/effort pins: the double cache-bust

A skill's or command's `model:` / `effort:` frontmatter overrides the **main conversation** for the rest of the current turn, then reverts on the next user prompt (CC skills frontmatter reference). With C tokens of accumulated history:

| Step | What happens | Cost shape |
|---|---|---|
| Skill activates | the (pinned model, pinned effort) cache key is cold → **full C-token uncached re-read** at the pinned model's input rate, then a cache write | the slow, expensive turn |
| Remaining requests in the turn | read the fresh cache under the pinned key | cheap |
| Next user prompt (revert) | the old (session model, session effort) entry is still warm within TTL → old prefix reads at 0.1×; **the skill-era turns are new uncached content** at session-model rates | second, smaller hit |

**Worked example** (200K-token history, Fable 5 session, a skill pinned `opus` + `low`, API rates): entry ≈ 200K × $5/M = **$1.00** uncached plus the cache-write premium; exit ≈ 200K × $1/M cache read plus the skill-era turns at $10/M. The pin saves only the skill's own marginal work — typically $0.10–0.20. **Net loss in any long session.** A main-thread pin pays off only when the conversation is short or the skill itself processes very large volume on the cheaper model — measure before assuming.

Nuances:

- **Effort-only pins are not the cheap version** — same double bust, and the entry re-read bills at the *active* model's rate (in a Fable 5 session, an `effort: low`-only pin re-reads at $10/M — twice what the opus-pin's entry costs for the same mistake).
- **A pin that resolves to the already-active level keeps the cache** (documented no-op) — e.g. `effort: high` in a session already at the default.
- **Fable 5's automatic safety fallback to Opus is also a model switch** (full re-read) — outside the author's control, but it explains surprise slow turns in security-/bio-adjacent sessions.

## The safe patterns

| Pattern | Cache impact | Use |
|---|---|---|
| **No pin (inherit)** | none — skill invocation appends a user message; nothing earlier changes | DEFAULT for every main-thread skill/command |
| **Pin on an AGENT** (`agents/*.md`) | none on the main thread — agents always execute as subagents with their own conversation and own cache (5m TTL) | the natural home for model/effort pins |
| **Pinned skill forced into a subagent** (`context: fork` + `agent:`) | parent cache untouched; the fork inherits the full history, so a pinned fork pays ONE cold re-read inside the fork — no exit re-read, no parent pollution | a pinned skill that needs conversation context |
| **Pinned skill/command on the main thread** | double cache-bust per invocation (table above) | the anti-pattern — avoid |

**Rule: a skill or command with a hardcoded `model:` or `effort:` must always run as a subagent.** Either author it as an agent, or set `context: fork` (+ `agent:`) in the same frontmatter so the pin can never touch the main conversation's cache. A main-thread pin is never "free": it taxes the entire session to discount one skill.

(`CLAUDE_CODE_SUBAGENT_MODEL` is the operator-side equivalent — it overrides all subagent models without touching the main thread.)

## Other authoring decisions with cache consequences

All verified against the CC prompt-caching doc:

- **Skill body size.** Invocation appends the body as a user message — cache-safe, but the body then rides in the prefix and is paid for (at 0.1× when cached) on every subsequent turn of the session. Progressive disclosure — lean SKILL.md, load-on-demand `references/` — is a token-efficiency rule, not just a style rule.
- **Hooks, commands, agents, and plugin-provided skills** never invalidate — anything they add is appended after the existing conversation.
- **MCP servers** a skill depends on: deferred tools (the default via tool search) append safely; tools loaded **into the prefix** (`alwaysLoad`, tool-search unavailable/disabled) invalidate the entire cache whenever the server connects, disconnects, or changes its tool list mid-session. Prefer deferred loading in skill designs.
- **CLAUDE.md edits mid-session** don't invalidate the cache — but also don't apply until `/clear`, `/compact`, or restart. Never author instructions that assume mid-session CLAUDE.md reloads.
- **`/compact`** rebuilds the conversation layer by design. Long-running autonomous skills should checkpoint durable state to disk rather than rely on chat history, which bounds what compaction can cost them.

## Sources

- code.claude.com/docs/en/prompt-caching — the (model, effort) cache keys, full invalidation/keep lists, TTL policy (1h subscription main thread / 5m subagents), subagent-vs-fork cache behaviour
- code.claude.com/docs/en/skills — frontmatter reference: `model:` override is turn-scoped on the main thread, reverts next prompt
- code.claude.com/docs/en/model-config — `/model` picker warning ("the next response re-reads the full history without cached context"); `/effort` confirmation dialog; automatic Fable→Opus fallback is a model switch
- platform.claude.com/docs/en/build-with-claude/prompt-caching — prefix matching, model-bound cache, 1.25×/2× write and 0.1× read multipliers
- CC v2.1.170 binary — `"ttl": "1h"` cache_control; "cache_control changed (scope or TTL)" miss reason
