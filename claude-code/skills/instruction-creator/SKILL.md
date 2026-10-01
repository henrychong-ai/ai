---
name: instruction-creator
description: "Architect for Claude instruction ecosystems (agents, skills, slash commands, MCP servers, project instructions) with Claude Code best practices — skill templates, 5-step workflow, cache-safe model/effort config and routing (Sonnet 5.5 at medium by default, Opus 5.5 to step up), fork subagents (conversation forks vs context: fork), packaging scripts, model compatibility audits (Sonnet 5.5, Opus 5.5, Fable 5.1, Opus 5, Opus 4.8). Use for creating/updating agents/skills/commands, MCP setup guides, team distribution sanitisation."
---

# Instruction Creator Skill

This skill provides complete guidance for creating and reviewing Claude instruction files across the entire instruction ecosystem.

**Updated:** 2026-09-29 — Sonnet 5.5 (rel. 2026-09-28, the `sonnet` alias on the Anthropic API from CC 2.1.284) delta pass: `references/claude-sonnet-5-5-compatibility.md` added (standalone Sonnet chain: `between_tools` and account-bound thinking, seven official snippets scoped by effort, model-conditional add-backs that run against removal-first, system-card authoring findings, fallback to Sonnet 5); **recommended routing ladder** — Sonnet 5.5 at `medium` by default (agents and forked skills pin `model: sonnet` + `effort: medium`, replacing the 2026-09-24/24b `model: opus`, effort-omitted default), step up to Opus 5.5 at `medium` or `high`, Opus 5.5 at `xhigh` normally only for a main thread overseeing large runs with pinned Opus workers; Opus 5.5 file amended from its system card (safeguards and fallback, authorisation carve-out for keep-going rules, pasted-text hardening, reporting discipline); agent contract names what a brief cannot authorise; effort-change cache exception now covers Sonnet 5.5; `claude plugin eval` and `/claude-api prompt-audit` added to the prompt-debt audit; CLAUDE.md size guidance aligned with the official under-200-lines recommendation. 2026-09-24d — Opus 5.5 harness injection firmed up: the silence nudge is confirmed on 2.1.280–2.1.281; the Fable 5.1 finish-the-task blocks were absent in an Opus 5.5 session, so a CLAUDE.md continuation rule naming the specific stops adds behaviour there (Opus 5.5 file Part 3). 2026-09-24b — Agent template now matches Model Configuration (`model: opus`, `effort` omitted, leaf-worker `disallowedTools`) with a lean role + contract body; TodoWrite references corrected to the Task* tools (off by default on current models) and dropped as an agent-vs-skill differentiator; example Codex model name updated to `gpt-6-astra`. 2026-09-24 — Opus 5.5 (rel. 2026-09-22, now the `opus` alias) delta pass: `references/claude-opus-5-5-compatibility.md` added (API breaks, effort recalibration to a `medium` default, thinking-line removal, unattended early stops, Claude Code harness split); new `references/model-compatibility-index.md` takes the model catalogue, delta chain, per-model headline deltas, and routing out of SKILL.md; effort-change cache exception on Opus 5.5 / Fable 5.1; recommended `model: opus` default for agents and forked skills, stated separately from the harness default; built-in agent model tables corrected. 2026-09-14 — Instruction size limits by surface: the account-level Claude Desktop / claude.ai "Instructions for Claude" field is capped at 32,768 Unicode code points and *blocks* the whole instruction set when exceeded (server-side, undocumented; observed on Desktop 1.52386.6). New limits table + paste-field derivation rule (SKILL.md § Platform Considerations; conversion guide § "Instruction Size Limits by Surface"). 2026-09-01 — Fable 5.1 (rel. 2026-09-01) delta pass: `references/claude-fable-5-1-compatibility.md` added (9 behavioural deltas, harness-injected vs author-owned rule, effort/cost calculus, safeguards/fallback, system-card authoring findings); models table, effort ladder (`max` added), cache math, and checklists refreshed. 2026-08-14 — Fork subagents: "Forking — Two Distinct Mechanisms" disambiguation (conversation forks `subagent_type: "fork"`/`/subtask` vs `context: fork` frontmatter), fork delegation calculus (forks cannot be model/effort-pinned), `background:` frontmatter field, cache-reference correction (`context: fork` skills receive NO conversation history), Fable 5 fork-economics delta, CC→Codex fork mapping. 2026-08-03 — Opus 5 compatibility reference added (`references/claude-opus-5-compatibility.md`): removal-first reaches the Opus tier (verification scaffolds, self-correction nudges, review severity pre-filters now hurt), effort↮length decoupling, thinking-on-by-default mechanics, behavioural A/B prompt-debt audit. 2026-06-16 — CC→Codex conversion guide added (`references/cc-to-codex-conversion-guide.md` + `templates/cc-to-codex-assessment-template.md`): mechanic map, T1/T2/T3 tiers, Tier-A/B distribution decision, data + harness-tool gates. 2026-06-10 — Fable 5 (released 2026-06-09; **new tier above Opus**, not an Opus replacement) multi-model restructure; per-model deltas now live in `references/claude-<model>-compatibility.md` (supersedes the single-model 4.8 pass, 2026-05-30). Same day: cache-safety & token-efficiency rules — the CC prompt cache is keyed by (model, effort), so model/effort pins belong in subagent contexts only (`references/cache-and-token-efficiency.md`).

## ⚠️ Model-Aware Instruction Authoring (MANDATORY)

Frontier Claude models follow instructions literally and strongly — and each release shifts *how* to author for them. The 8 Core Rules below are **durable**: they originated with Opus 4.7 and apply unchanged through Opus 4.8, Opus 5, Opus 5.5, Sonnet 5.5, Fable 5, and Fable 5.1. Per-model behavioural deltas live in the compatibility references; for instructions consumed by mixed/unknown models, author to the Core Rules + the brevity-first/removal-first principle (established by Fable 5, extended to the Opus tier by Opus 5).

**Precedence for model-specific snippets:** a snippet from a compatibility file applies only when the instruction pins that model (and, where the file says so, that effort). Sonnet 5.5's official guidance adds back lines and tools that removal-first cuts on Opus and Fable (the full list and conditions: Sonnet file Part 2B), so keep them out of Opus-targeted, Fable-targeted, and mixed-target instructions.

**Model catalogue and routing: `references/model-compatibility-index.md`** — current models (Sonnet 5.5 = `sonnet` on the Anthropic API, Opus 5.5 = `opus`, Fable 5.1 = `fable`), alias targets per provider, the delta chains (Opus 4.8 → 5 → 5.5; Fable 5 → 5.1; Sonnet 5.5 standalone), per-model headline deltas, the recommended routing ladder, and which compatibility file to load when. **Load it, then the matching compatibility file, whenever auditing or authoring for a specific model.**

### Core Rules (durable across Opus 4.7 → 5.5, Sonnet 5.5, and Fable 5.x)

| Rule | One-liner |
|------|-----------|
| **1. Positive over negative** | Rewrite "No X" / "Don't Y" as "Do positive equivalent" |
| **2. State scope explicitly** | "Apply to all items" — not "apply this pattern" |
| **3. Resolve conflicts with precedence** | When two rules could clash, state which wins under what conditions |
| **4. Mark illustrative lists** | Add "(illustrative — not required outputs)" to example lists |
| **5. Skip motivational framing** | "Do your best", "maximise value" are no-ops; use `effort:` YAML instead |
| **6. Scope rhetorical language** | Mark self-talk and user-aspirational language so Claude doesn't echo it |
| **7. Calibrate length to task** | Replace "< N lines" caps with "match length to task complexity" |
| **8. Specify tone positively** | If you want warmth, say "respond in a friendly, encouraging tone" |

### Harness-Injected on Claude Code — Do Not Duplicate

Claude Code 2.1.257 already injects, verbatim, the over-planning block, the progress-updates line, both finish-the-task blocks (autonomy and "Delivering work"), the state-change caution, the terminal-output note, and the per-turn batching nudge (observed in a Fable 5.1 session). Opus 5.5 sessions get a different set: 2.1.280 and 2.1.281 injected the "user hasn't heard from you in a while" silence nudge as a mid-turn system message, and a 2.1.281 Opus 5.5 session carried the over-planning block but **not** the finish-the-task blocks. On Opus 5.5, nothing in the harness counters early stops, so a CLAUDE.md continuation rule adds behaviour rather than duplicating it. What Claude Code injects in Sonnet 5.5 sessions is unverified; Sonnet 5.5's official silence snippet is the same text as the injected Opus 5.5 nudge, so it belongs only in custom harnesses. **Do not duplicate any injected block in CLAUDE.md, rules, skills, or agents.** Duplication is a token tax on every turn and over-steers a model already carrying the instruction. Skills shipped to other surfaces (Claude Desktop and Team zips, Codex, Gemini, ChatGPT) receive none of them and must embed what they depend on. The Opus 5.5 named-stop ("keep going") instruction is for unattended API/SDK harnesses; in Claude Code it belongs in a CLAUDE.md rule chosen per working style, never in a skill; an agent definition may carry it with the authorisation boundary. Full split and the author-owned lists: Part 2A of `references/claude-fable-5-1-compatibility.md` and Part 3 of `references/claude-opus-5-5-compatibility.md`.

### Prompt-Debt A/B Audit (cross-model)

Before rewriting any instruction file for a new model, isolate the failure behaviourally: pick one repeatable task with clear success criteria; run it twice in fresh sessions, identical except for the skill's presence; compare to determine whether the skill or the model causes the failure; then cut the specific offending instruction. Cheaper and more decisive than a read-through audit — a single stale line (e.g. a leftover "wait for another agent" handoff) can account for systematic failures.

Tools for the audit (`claude plugin eval` and `/claude-api prompt-audit` run on a Claude subscription as well as an API key):
- **`claude plugin eval`** (Claude Code v2.1.269+) automates the A/B: it runs each case with the plugin and against a no-plugin baseline and reports the difference. A skill must be packaged in a plugin first; for one skill inside a conversation, the skill-creator plugin runs a similar comparison. It uses the session's own authentication, so runs count against plan usage limits; after a limit is hit, later runs score about 0 and the suite still reports complete, which looks like a regression — check the `NOTES` column.
- **`/claude-api prompt-audit`** (Anthropic's `claude-api` skill) reads prompts, tool descriptions, skills, `CLAUDE.md`, rules, commands, and subagents, and returns a report plus a proposed diff; it edits only on request. `/claude-api build-eval` and `/claude-api hillclimb` evaluate apps that call the Claude API (the eval runs make the app's own API calls), so they fit API-app skills rather than Claude Code instruction files.
- **Eval hygiene:** keep a held-out test set and revert a change that improves the training cases while the test cases stall; change one attributable thing per round; never paste failing transcripts into the instruction being tuned; check a judge's grades against a sample of transcripts before trusting it.

Standing grep checks alongside the A/B (current models):
- **All skills:** "think carefully", "think step by step", "think hard", "show/explain your reasoning" — remove; effort is the depth control, and reasoning-reproduction requests can be declined or blocked with no fallback model (Opus 5.5 file 2.2; Sonnet 5.5 file Part 5). Sole exception: Sonnet 5.5's "Think the problem through before you answer." in API prompts for reasoning tasks that return JSON under adaptive thinking (Sonnet file Part 2B).
- **All skills — ritual instructions:** mandatory multi-step procedures, scratchpad rules, verify-twice rules, and instructions that contradict each other — remove; an internal Opus 4.8 → 5.5 migration cut a further 9% of cost by deleting them (Opus 5.5 file Part 7).
- **All skills with a search tool:** "minimise tool calls" / "only use tools when strictly necessary" — remove (Sonnet 5.5 answers from memory; Sonnet file Part 2).
- **Agents and keep-going rules:** a bare "do not ask for clarification", or a continuation rule without an authorisation exception — add an exit ("if the task cannot be done as specified, report what is missing and stop") and state that permission questions go to the user (Opus 5.5 file 2.3).
- **API-targeting skills only:** forced `tool_choice` (`any` / `tool`) — replace with a prose statement of when the tool applies, and have the harness check the call happened; mid-session edits to the system prompt or tool list — replace with appended mid-conversation system messages and tools declared from the first request (Opus 5.5 file Part 1); user text inside a `tool_result` block — append it after the last `tool_result` instead (Sonnet 5.5 flags it as possible injection).

### Effort Is a Harness Parameter, Not Prompt Content

Instruction file prose cannot escalate effort. Do not write "assume high effort" or "think deeply" in CLAUDE.md / SKILL.md body content. Effort resolves (highest first):
- `CLAUDE_CODE_EFFORT_LEVEL` env var
- `effort:` field in YAML frontmatter (per-skill/agent/command, while active)
- session choice: `--effort`, `/effort low|medium|high|xhigh|max` (saved per model under `modelSettings`)
- settings: per-model `modelSettings` or `effortLevel` — a top-level `effortLevel` in the **user** settings file is ignored for Opus 5.5 and models released after it, including Sonnet 5.5 (project, local, managed, and `--settings` still apply)
- model default — **`medium` on Opus 5.5 and Sonnet 5.5 in Claude Code** (Sonnet 5.5's API default is `high`); `high` on Fable 5.1, Fable 5, Opus 5, Sonnet 5, and Opus 4.8

Unpinned skills and agents inherit the session level. Main-thread skills and commands carry no pin; any agent or forked skill that pins `model` pins `effort` with it (routing ladder in `references/model-compatibility-index.md`), so a Sonnet worker does not inherit an `xhigh` oversight session. To get less thinking, lower effort; prompt text is the weaker lever, and on Sonnet 5.5 asking for less thinking "doesn't reliably reduce its thinking". Thinking toggles (`alwaysThinkingEnabled`, `MAX_THINKING_TOKENS=0`) do nothing on Opus 5.5, Sonnet 5.5, or Fable; `ultrathink` still adds a one-turn in-context instruction. Re-baseline existing `effort:` pins on every model upgrade with an effort sweep rather than carrying prior-model pins forward — level names do not map to the same amount of thinking across models. Per-model recommendations and the joint model × effort routing table: `references/model-compatibility-index.md`.

**Cache safety is the other axis.** The CC prompt cache is keyed by model and, on most models, by effort — a main-thread pin forces an uncached re-read of the conversation. On Opus 5.5, Sonnet 5.5, and Fable 5.1 with an API key or subscription, an effort change keeps the cache (not on Bedrock, Agent Platform, a Claude apps gateway, `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`, or HIPAA); a model change never does. Execute pinned instructions as subagents (see Model Configuration below); full mechanics + cost math: `references/cache-and-token-efficiency.md`.

---

## Instruction File Types

| Type | Location | Purpose | Loading |
|------|----------|---------|---------|
| **CLAUDE.md** | `~/.claude/` or `./` | User preferences, identity | Always (auto) |
| **Rules** | `~/.claude/rules/` or `./.claude/rules/` | Focused config, patterns | Always (auto) |
| **Agents** | `~/.claude/agents/*.md` | Autonomous domain specialists | On trigger/Agent tool |
| **Skills** | `~/.claude/skills/*/SKILL.md` | Bundled knowledge packages | On `/skill-name` or Skill tool |
| **Run skills (repo-scoped)** | `<repo>/.claude/skills/run-*/` | Build/launch/**drive** one app | Auto-match by description, or `/run`; authored via `/run-skill-generator` |
| **Commands** | `~/.claude/commands/*.md` | Natural language prompts | On `/command-name` |

**Key Distinction:**
- **Auto-loading** (CLAUDE.md, Rules): Always load every session - keep lean
- **On-demand** (Skills, Agents, Commands): Load when invoked - can be larger

## CLAUDE.md and Rules

### Auto-Loading Behavior

**Critical:** CLAUDE.md and rules files **always fully load** every session. There is no lazy loading or incremental loading for these files.

**Loading Order:**
1. Global CLAUDE.md (`~/.claude/CLAUDE.md`)
2. Global rules (`~/.claude/rules/**/*.md`)
3. Project CLAUDE.md (`./CLAUDE.md`)
4. Project rules (`./.claude/rules/**/*.md`)
5. CLAUDE.local.md (`./CLAUDE.local.md`) - gitignored
6. Nested subdirectory CLAUDE.md - only loads when navigated to that dir

**Token Budget Guidelines** (Claude Code's official recommendation is under about 200 lines per file; files load in full up to 4 MiB, so a larger file still costs context on every turn and dilutes adherence):
| File Type | Recommended | When it grows past that |
|-----------|-------------|---------|
| Global CLAUDE.md | under ~200 lines | Move detail into rules files, `paths:`-scoped rules, or skill references; keep only what must apply every session |
| Each rules file | 50-200 lines | Split by topic, or scope with `paths:` frontmatter |
| Project CLAUDE.md | under ~200 lines | Move reference material into skills or docs the file points to |

**Writing Style for CLAUDE.md (MANDATORY):**
All CLAUDE.md content loads into every message context — every token costs context budget. When writing or updating CLAUDE.md files (global or repo-scoped):
- Directive-style, no prose or explanation. Terse.
- Tables/lists over paragraphs
- Optimise for AI comprehension, not human readability (human-readable is a bonus, not a goal)
- No redundant phrasing ("Please note that...", "It is important to...")
- Compress: if 3 words convey the same as 10, use 3
- **Apply the Core Rules** (see Model-Aware Instruction Authoring at the top of this skill): positive framings over negative constraints, explicit scope, resolved precedence for conflicting directives, marked illustrative lists, scoped rhetorical language, task-complexity calibration for length. On Fable 5.x, also brevity-first: one coherent instruction over enumerated don't-lists.

### Rules Directory Patterns

```
~/.claude/rules/
├── environments/       # Cloud accounts, credentials, paths
│   ├── cloudflare.md
│   └── 1password.md
├── languages/          # Language conventions
└── tools/              # Tool-specific configs
```

**Benefits of Rules:**
- Organization by category
- Reusable across projects
- Selective team sharing
- Independent maintenance
- Override hierarchy (project > global)

### Content Placement Quick Guide

| Content | Location |
|---------|----------|
| Core identity/preferences | Global CLAUDE.md |
| Small cross-cutting config | `rules/config/` |
| Large documentation | Skill `references/` |
| Project context | Project CLAUDE.md |
| Personal overrides | CLAUDE.local.md |

See `references/rules-and-content-placement-guide.md` for comprehensive guidance.

## Creating Agents

Agents are autonomous domain specialists with proactive operation capabilities.

### Agent YAML Frontmatter

**Required fields:**
```yaml
---
name: agent-name                    # Required: kebab-case identifier
description: Brief description...   # Required: include "Use PROACTIVELY" for auto-trigger
---
```

**Optional fields:**
```yaml
---
model: sonnet                       # Recommended default for agents (see Model Configuration); harness default when omitted = main session model
effort: medium                      # Pin alongside a model pin so the agent does not inherit the session level
tools: Read, Grep, Glob, Bash       # Tools agent can use (inherits all if omitted)
disallowedTools: Write, Edit        # Tools to explicitly deny
permissionMode: default             # default|acceptEdits|dontAsk|bypassPermissions|plan
skills: pr-review, security-check   # Skills to auto-load into agent context
hooks:                              # Lifecycle hooks (see Hooks section)
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
---
```

### Model Configuration

**Harness default vs recommended default — two different things:**
- **Harness default (what Claude Code does when `model` is omitted):** a subagent resolves per-invocation `model` → frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → **the main conversation's model**; a skill or command without `model` runs on the session model. There is no fixed `sonnet` default.
- **Recommended default for authored agents and `context: fork` skills: `model: sonnet` + `effort: medium`** (routing ladder below). Any agent or forked skill that pins `model` pins `effort` with it: an unpinned agent inherits the session effort, so under an `xhigh` oversight session a Sonnet worker would run at `xhigh`, where Sonnet 5.5 loses its cost advantage. Agent and forked-skill pins are cache-safe.
- **Main-thread skills and commands: omit `model` and `effort`.** A main-thread model pin switches the session model for the turn and re-reads the conversation uncached; put pins only where they run as subagents (below).

**Recommended routing ladder** (summary; canonical: `references/model-compatibility-index.md`, with evidence, sessions, and the provider caveat). Default → step up; change the model before raising Sonnet's effort:

| Rung | Model and effort | Use for |
|---|---|---|
| 1 | **Sonnet 5.5 at `medium`** | The default for almost all work: sessions, authored agents, and forked skills (`model: sonnet` + `effort: medium`) |
| 2 | **Opus 5.5 at `medium`** | Step up when more quality is needed; the default for work that needs Opus, and the best cost/quality balance |
| 3 | **Opus 5.5 at `high`** | In-depth work |
| 4 | **Opus 5.5 at `xhigh`** | Normally only as the main thread or advisor (the API advisor tool — Sonnet file Part 1 — or a main thread reviewing workers' output) overseeing large coding or agentic runs, paired with pinned Opus worker agents for implementation: `model: opus` + `effort: medium` for volume implementation; `model: opus` + `effort: high` for state and concurrency, migrations and backfills, security-sensitive code, or fixes after a failed review round. Use these Opus workers inside runs that already warrant Opus `xhigh` oversight; a standalone implementation agent stays at rung 1 |

- **Why step the model, not Sonnet's effort:** Sonnet 5.5's cost advantage holds at `low` and `medium`; "at higher settings, it can perform comparably at a similar cost" (launch page), and its system card shows `max` scoring below `xhigh` on FrontierCode at roughly 12× the output tokens.
- **Go straight to Opus (skip rung 1) for:** unattended workers with broad permissions (Sonnet 5.5 scores worse than Opus 5.5 on accepting unverifiable authorisation, approval-gate bypass, and misbehaviour in Claude Code sandboxes); long-context codebase work; open-ended work that needs sustained judgement; factual answers that cannot be checked against a search or source.
- **Outside the ladder:** `low` for mechanical, high-volume lookups; `haiku` for the cheapest ones; `max` rarely justified; **Fable 5.1** (`fable`; about 2.5× Opus 5.5 per token, slow first token) is the escalation tier for frontier-hard work — for example when Opus 5.5 at `xhigh` fails the same problem twice, or where the result matters more than the token price.

Rules for any pin:
- **Step up deliberately.** Move up a rung when the task needs it, and say why in the agent's description or brief; decide model and effort together.
- **Provider caveat for `sonnet`:** the alias is Sonnet 5.5 only on the Anthropic API (which includes Claude subscriptions) from Claude Code 2.1.284; on Bedrock, Agent Platform, and Foundry it is Sonnet 4.5, and on Claude Platform on AWS Sonnet 4.6. Keep `model: sonnet`; teams on those providers set `ANTHROPIC_DEFAULT_SONNET_MODEL` to a Sonnet 5.5 ID their provider serves, or treat rung 1 as Opus 5.5 at `medium`.
- **Pins are cache-safe only in subagent contexts.** Agents are safe by construction (own subagent conversation, own cache). **A skill/command with a hardcoded `model:`/`effort:` must always run as a subagent — set `context: fork` (+ `agent:`) alongside the pin.** Mechanics + cost math: `references/cache-and-token-efficiency.md`.
- **Conversation forks cannot be pinned.** `subagent_type: "fork"` ignores `model` overrides and has no frontmatter — a fork always bills the session model at session effort. When a pin matters, delegate to a named agent instead of forking (see Forking — Two Distinct Mechanisms).
- **Use aliases, not version-pinned IDs** (aliases track each provider's target for the family, not always the latest model): `sonnet`, `opus`, `fable`, `haiku`. Pin a full ID such as `claude-opus-5-5` only when a specific version is genuinely required.
- **`inherit`**: explicitly selects the main conversation's model — use it when an agent must follow the session (e.g. it needs the session's exact tier).
- **Priority order** (named subagents): per-invocation `model` → agent frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → main conversation's model. Conversation forks bypass this entirely — always the session model.

### Agent Template Structure

```markdown
---
name: agent-name
description: [Specialisation]. [Capabilities]. Use PROACTIVELY for [triggers].
model: sonnet                   # recommended default (routing ladder above); `opus` to step up
effort: medium                  # pinned with the model so the agent never inherits an xhigh session
disallowedTools: Agent, Task    # leaf worker: no nested fan-out (or list an explicit `tools:` allowlist)
---

[One paragraph: the agent's role, the domain it owns, and the outcome it is accountable for.]

## Contract
- **Inputs:** [what the caller's brief supplies; on a blocking ambiguity, state the assumption and proceed; if the task cannot be done as specified, report what is missing and stop]
- **Does:** [the work, the tools and references it uses, the checks it runs before returning]
- **Boundary:** [destructive, outward-facing, or approval-gated actions it stops and reports instead of performing; what the brief cannot authorise, such as credentials, user consent, or access to external systems; permission questions go back to the user, never answered on the user's behalf]
- **Returns:** [the report to the caller: results, what was verified and how (read in full or sampled), failures, decisions needed]
```

The Boundary line carries the authorisation clause because three current models share the weakness: Fable 5.1 accepts unverifiable authority claims more readily than Opus 5 (Fable 5.1 file Part 2D); Opus 5.5 regressed on the same measure, and one of its lead agents invented a user approval for a subagent (Opus 5.5 file 2.3); Sonnet 5.5 scores worse than Opus 5.5 (2.76 vs 2.39) and treats a task brief as authorisation (Sonnet 5.5 file Part 4). Enforce approval gates mechanically (permissions, hooks); the prose clause states intent, it does not enforce it.

Write the return for the **caller**, not the user: a backgrounded subagent's narration is invisible, so only its final result reaches anyone. For leaf workers, bar `Agent` and `Task` (two names for one spawn tool) with `disallowedTools`, or give a `tools:` allowlist that omits them; nested spawning multiplies token spend. Add domain sections below the contract only when the agent needs knowledge it cannot load from a skill.

## Creating Skills

Skills are specialized knowledge packages with bundled resources using progressive disclosure.

### 5-Step Skill Creation Process

1. **Understand**: Clarify problem, triggers, success criteria, edge cases
2. **Name**: kebab-case, max 64 characters
3. **Description**: Third-person voice, concrete verbs, trigger terms (CRITICAL). **Max 1024 characters** — keep to 1–2 lines of dense content. Claude Desktop upload validation rejects skills with descriptions over 1024 chars with `field 'description' in SKILL.md must be at most 1024 characters`.
4. **Instructions**: Clear hierarchy with examples and error handling
5. **Package/Test**: Use validation scripts

### Always Scaffold a TODO.md (every new skill)

Every new skill gets a `TODO.md` at its root — the single honest record of open items: deferred work, unset placeholders, unverified data, and phased/future work. Create it for **every** skill (even if the only entry is "none open yet") and keep it current as the skill evolves.

- **Why:** open items otherwise scatter across plan files, inline `[SET]`/`[TODO]` markers, and stub scripts, and get lost — one per-skill `TODO.md` is the single place to look.
- **Data-bearing / architecture-first skills:** log **every** placeholder and unverified datum here — never assert unverified data as fact. Group by phase (populate / wire / future) with checkboxes.
- **Mechanism:** `scripts/init_skill.py` scaffolds a `TODO.md` stub automatically, so a fresh skill starts with one.

### Skill YAML Frontmatter

**Required fields:**
```yaml
---
name: skill-name                    # Required: kebab-case, max 64 chars
description: This skill should...   # Required: third-person voice, max 1024 chars
---
```

**Optional fields:**
```yaml
---
allowed-tools: Read, Grep, Glob     # Tools without permission prompts
context: fork                       # Run in isolated sub-agent context
agent: Explore                      # Agent type when context: fork is set
user-invocable: true                # Show in /menu (default: true)
disable-model-invocation: false     # Prevent Skill tool from calling (default: false)
hooks:                              # Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
          once: true                # Run once per session, then removed
---
```

### Forking — Two Distinct Mechanisms (Disambiguation)

Claude Code has two unrelated features that both use the word "fork". Authors (and many blog posts) conflate them — keep them separate:

| | `context: fork` (frontmatter) | Conversation fork (`subagent_type: "fork"` / `/subtask`) |
|---|---|---|
| **What runs** | The skill/command body as the prompt for a **fresh** subagent | A subagent inheriting the **entire conversation** (system prompt, tools, history) |
| **Conversation history** | **None** — official docs: "It won't have access to your conversation history" | Full history at fork moment |
| **Model / effort** | Pinnable via `model:`/`effort:` frontmatter | **Always the session model at session effort — a `model` override is ignored** |
| **Prompt cache** | Own cold cache — the cache-safe home for pins | Shares the parent's cache prefix |
| **Authored where** | SKILL.md / command frontmatter | Nowhere — runtime-only (Agent tool call or user-typed `/subtask`); an on-disk agent definition cannot be a fork |

#### `context: fork` — run a skill in an isolated subagent

Use `context: fork` to run skills in an **isolated sub-agent context**:

```yaml
---
name: code-analyzer
description: Analyze code patterns and generate reports
context: fork          # Isolated execution — fresh context, NO conversation history
agent: Explore         # Use fast read-only agent
background: false      # Optional (default true, v2.1.218+); false blocks the invoking turn
---
```

**When to use `context: fork`:**
- Verbose output (test runs, large file analysis)
- Multi-step operations that would clutter context
- Complex workflows where only the summary matters

**Landmines (official docs):**
- The skill body becomes the subagent's entire prompt. A guidelines-only skill ("use these API conventions") forked this way returns nothing useful — `context: fork` fits only skills that state a **task**.
- **Backgrounded forked skills run with the narrower background-subagent tool set** (the conversation-fork tool exemption does not cover them). If a step needs a tool outside that set, set `background: false`.
- A backgrounded forked skill's edits land outside session checkpoints — `/rewind` cannot undo them; revert via git.
- Model-invoked skills may not honour `context: fork` (github.com/anthropics/claude-code issue #17283) — when isolation is load-bearing, pair it with `disable-model-invocation: true` so only user invocation (which honours the fork) can trigger the skill.

**Agent options for `context: fork`:**
| Agent | Model | Tools | Use Case |
|-------|-------|-------|----------|
| `Explore` | Inherits main model, capped at Opus on the Claude API (Haiku before v2.1.198) | Read-only | Fast analysis, file discovery |
| `Plan` | Inherits main model | Read-only | Research before planning |
| `general-purpose` | `CLAUDE_CODE_SUBAGENT_MODEL` if set, else main model | All | Complex tasks with edits |
| Custom agent | Per config | Per config | Domain-specific work |

#### Conversation forks (`subagent_type: "fork"`, `/subtask`)

A conversation fork inherits the whole conversation and the parent's prompt cache, runs in the background, and returns only its final result. Official heuristic: fork *"when a named subagent would need too much background to be useful, or when you want to try several approaches in parallel from the same starting point."*

Facts that matter when authoring instructions (verified against official docs + a live fork test, 2026-08-14):

- **Model/effort pins are impossible.** A `model` override on a fork is ignored; the fork bills the session model at session effort (under a Fable 5.x main loop, every fork bills Fable, with cache reads at a quarter of the Fable 5 rate on 5.1). The only lever for a cheaper or pinned model is a named subagent — and the trade-offs never combine: cache-sharing requires the parent model, a cheap model requires a cold start.
- **Cost shape:** the fork's first request reads the parent's cache (~0.1× input rate) — officially "cheaper than spawning a fresh subagent for tasks that need the same context" — but the floor cost scales with conversation length at parent-model rates (live measurement: ~151k tokens for a trivial 120-word fork reply in a long session). Reserve forks for context-entangled work; never fork small tasks.
- **Tools:** forks skip the subagent tool-narrowing filters and receive the main conversation's exact tool pool (interactive-only tools such as AskUserQuestion are still stripped from every subagent).
- **Bounds:** a fork cannot spawn another fork; at the subagent depth limit its inherited Agent tool errors instead of spawning. To bar forks, use the permission deny rule `Agent(fork)` — the `CLAUDE_CODE_FORK_SUBAGENT=0` env var does not propagate to subagents (github.com/anthropics/claude-code issue #68619).
- **Mode coupling:** fork mode (default-on in interactive sessions since v2.1.232; off in `-p`/SDK unless `CLAUDE_CODE_FORK_SUBAGENT=1`) also makes **all** Claude-spawned subagents run in the background and removes the Agent tool's `run_in_background` parameter.
- **Related surfaces:** user-typed `/subtask` starts a fork (v2.1.212+); `/branch` copies the transcript into a new session you drive yourself (explore-and-steer, vs a fork you delegate); the Agent SDK equivalent is `forkSession: true` / `fork_session=True`.

Cache/cost detail for both mechanisms: `references/cache-and-token-efficiency.md`. Fork-vs-named-subagent decision guidance: the Agent vs Skill Decision Matrix below.

### Effort Level Override

Use `effort` to control reasoning depth when a skill/command is invoked:

```yaml
---
name: quick-lookup
description: Fast reference lookup
effort: low
context: fork          # an effort pin runs as a subagent (cache rule)
agent: Explore
---
```

| Value | Symbol | Use When |
|-------|--------|----------|
| `low` | ○ | Quick lookups, simple transforms, high-volume tasks |
| `medium` | ◐ | Balanced analysis, most general tasks |
| `high` | ● | Complex reasoning, strategic analysis, deep research |
| `xhigh` | ◉ | Long-horizon, capability-sensitive work (Fable 5.x, Opus 5.5, Sonnet 5.5, Opus 5, Opus 4.8/4.7, Sonnet 5); on Opus 5.5, normally only a main thread overseeing large runs (routing ladder) |
| `max` | ◎ | Absolute ceiling, unconstrained token spend (Fable 5.x, Opus 5.5, Sonnet 5.5, Opus 5, Opus 4.8/4.7/4.6, Sonnet 5/4.6); rarely justified in a pin; on Fable 5.1 `xhigh` matches `max` at 19 to 25% fewer output tokens on knowledge work, and on Sonnet 5.5 `max` scored below `xhigh` on FrontierCode |
| (omit) | — | Inherit session effort (main-thread skills and commands) |

**Main-thread skills and commands: OMIT the `effort` field** — inherit the session's effort. Specify it only when the instruction clearly and unambiguously calls for a different depth (e.g. a trivial high-volume lookup), and then run it with `context: fork`. Do not set higher effort to chase quality — that is the session's decision. **Any agent or forked skill that pins `model` pins `effort` with it** (`sonnet` + `medium` by default; routing ladder in `references/model-compatibility-index.md`). Effort values are model-relative (Opus 5.5 at `medium`, its default, matches or beats Opus 5 at `high`; Fable 5.1 at `medium` roughly matches Fable 5 at lower cost; Sonnet 5.5's levels are recalibrated against Sonnet 5); re-baseline pinned values when the model line changes.

**Cache rule:** on most models an effort pin shares the model pin's cache behaviour — the CC cache is keyed by (model, effort), so a main-thread effort pin double cache-busts the session, with the entry re-read billed at the *active* model's rate. Exception: on Opus 5.5, Sonnet 5.5, and Fable 5.1 with an API key or subscription, an effort change keeps the cache (not on Bedrock, Agent Platform, a Claude apps gateway, disabled experimental betas, or HIPAA). Pin only on agents or `context: fork` skills so the skill stays cache-safe on every model and route; a pin resolving to the already-active level keeps the cache. Detail: `references/cache-and-token-efficiency.md`.

**Priority:** `CLAUDE_CODE_EFFORT_LEVEL` env var > frontmatter > session `/effort` > settings (`modelSettings`, `effortLevel`) > model default (`medium` on Opus 5.5 and Sonnet 5.5 in Claude Code)

**Behaviour:** Overrides session effort while skill/agent/command is active; reverts when complete.

### Skill Directory Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description - required)
│   └── Markdown instructions
├── TODO.md (ALWAYS) - open items, deferred work, placeholders, unverified data
└── Bundled Resources (optional)
    ├── references/ - Documentation loaded as needed (DEFAULT)
    ├── scripts/    - Executable code
    ├── templates/  - Variable substitution files
    └── assets/     - Static files
```

### Content Formats & Source-File Archive

Skills carry content best loaded inline by Claude — `.md` for prose, `.csv` for tabular data, `.jsonl` for record streams, etc. Binary files (PDFs, images, audio, video, scanned documents) are not loadable as context — extract their substance to text, then archive the originals outside the skill so it stays lightweight + searchable while originals remain recoverable.

**Archive destination — pick one appropriate to your setup** (suggestion, not prescription): a local archive directory (e.g. `~/.claude/skill-originals/<skill-name>/...`) or a synced knowledge vault for personal skills; a cloud object store (S3 / R2 / GCS) under a per-skill prefix for team-distributed skills. Use a per-skill root and preserve the original subdir structure. For personal skills, optionally keep both a full-text `.md` (exact recall) and a short summary `.md` (fast overview) inside the skill.

Load **`references/skill-content-formats-guide.md`** for the format-by-content-type table (.md / .csv / .tsv / .jsonl / .yaml / Mermaid / etc.), conversion toolbox (`pdftotext`, `tesseract`, `markitdown`, `pandoc`, `whisper`), the SKILL.md pointer pattern, the 11-step migration playbook for skills with existing binaries, and the implications for skill-zip and Desktop Project distribution.

### Visibility Controls

| Field | Effect |
|-------|--------|
| `user-invocable: false` | Hide from /menu, still allows auto-discovery and Skill tool |
| `disable-model-invocation: true` | Block programmatic invocation via Skill tool |

### Repo-Scoped Run Skills → delegate to `/run-skill-generator`

A **run skill** tells an agent how to build, launch, and **drive** one app from a clean machine. It lives in the **target repo** at `<unit>/.claude/skills/run-<unit>/`, not in `~/.claude/skills/`.

- **Authoring:** do **not** hand-roll one with the generic 5-step process — invoke the built-in **`/run-skill-generator`**. It ships per-project-type examples (cli/server/tui/electron/web/library), a canonical template, and a *build-and-drive* definition-of-done (you must actually run + screenshot the app; every code block must be a command that worked this session). Refine an existing run skill rather than rewriting it.
- **Invocation:** `/run-skill-generator` is user-invoked: the user types it; the agent cannot start it (checked 2026-10-01 against the Claude Code skills docs).
- **Usage / verification:** the built-in **`/run`** and **`/verify`** consume it — it matches by `description` across `.claude/skills/*/SKILL.md` up the dir tree (not by name/path), and falls back to per-type patterns if none exists.
- **Deltas vs personal/distributed skills:** (1) **committed to the repo**, shared via **git**, not the skill-zip pipeline; (2) **Claude Desktop zip/Project distribution tracking and the 30 MB zip cap do NOT apply**; (3) **secrets hygiene still applies** — the committed driver/`SKILL.md` must point at `.env.example` / a secrets manager, never inline real credentials; (4) **the `description` is the trigger** — use the verbs an agent types ("run/start/build/screenshot"); keep `SKILL.md` short, the driver is the deliverable.

## Creating Slash Commands

Slash commands are natural language instruction prompts (NOT executable code).

### Command YAML Frontmatter (All Optional)

```yaml
---
description: Brief command purpose
allowed-tools: Bash(git:*), Read
argument-hint: [pr-number] [priority]
model: sonnet                       # a pin requires context: fork (cache rule)
effort: medium                      # pin with the model
context: fork                       # Run in forked sub-agent context
agent: Explore                      # Agent type when context: fork
disable-model-invocation: false     # Prevent Skill tool from calling
hooks:                              # Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
---
```

### Command Template

```markdown
---
allowed-tools: Tool(specific-commands)
argument-hint: [format]
description: Brief command purpose
---

# Natural Language Instructions for Claude

[Specific behavior description]

## Input Processing
- $ARGUMENTS represents user input (substituted by Claude Code)
- Process $ARGUMENTS as [expected format/type]

## Tool Usage
- Use [specific tools] to [accomplish task]
- Load documentation from [paths] before execution

## Output Requirements
- Provide [specific format] as response
```

## Hooks in Frontmatter

Skills, Agents, and Commands all support lifecycle hooks:

### Supported Events

| Event | Purpose |
|-------|---------|
| `PreToolUse` | Before tool execution, can block or modify |
| `PostToolUse` | After tool completes successfully |
| `Stop` | When component finishes |

**Note:** For agents, `Stop` hooks become `SubagentStop` events.

### Hook Syntax

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"           # Tool pattern (regex supported)
      hooks:
        - type: command
          command: "./script.sh"
          once: true            # Skills/Commands only, not Agents
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./lint.sh"
```

## Agent vs Skill Decision Matrix

### Quick Decision Framework

**Use Agent When:**
- Proactive operation with auto-triggering needed
- Complex autonomous decision-making required
- Long multi-step work that benefits from its own context window
- Domain specialist needing continuous operation

**Use Skill When:**
- Explicit invocation preferred (`/skill-name`)
- Bundled resources needed (references, scripts)
- Progressive disclosure valuable
- Token efficiency through optional resource loading

**Use Command When:**
- Simple, single-step operations
- Natural language instructions sufficient
- Quick user-triggered workflows

**Use `context: fork` When:**
- Skill/command produces verbose output
- Complex multi-step operations
- Want isolated context for cleaner main conversation

**Use a Conversation Fork (`subagent_type: "fork"`) When:**
- The task needs the session's accumulated context and re-briefing would be long or lossy
- Trying several approaches in parallel from the same starting point
- The work needs the full main-session tool pool
- The session model is right for the work anyway (forks cannot be model-pinned)

**Use a Fresh Named Subagent Instead When:**
- A cheaper or effort-pinned model is wanted — the only lever; forks ignore overrides
- A short brief suffices, or tool restriction is a safety property
- The session history is very long (fork read cost scales with it)

### Summary Table

| Feature | Agent | Skill | Command |
|---------|-------|-------|---------|
| **Auto-Trigger** | Yes | Yes | No |
| **Bundled Resources** | No | Yes | No |
| **context: fork** | N/A | Yes | Yes |
| **Token Efficiency** | Lower | Higher | Highest |
| **File Structure** | Single | Multi-file | Single |

**Task tracking is not a differentiator.** Main-thread skills and commands run in the session and can use its task-tracking tools as much as an agent can. Those tools are `TaskCreate`, `TaskGet`, `TaskList`, and `TaskUpdate`; `TodoWrite` is disabled by default in their favour. On current models they are off unless the user opts in (`CLAUDE_CODE_ENABLE_TODO_TOOLS=1`), so write instructions that work without them. Source: code.claude.com/docs/en/tools-reference, checked 2026-09-24.

## YAML Frontmatter Quick Reference

Agent / Skill / Command frontmatter blocks are documented inline under each "Creating ..." section above. For the complete cross-reference of every valid field (required vs optional, defaults, value enums, gotchas), load **`references/yaml-frontmatter-complete-guide.md`**.

## Review Checklist

### For Agents
- [ ] YAML: name, description; `model: sonnet` + `effort: medium` unless the routing ladder calls for a step up (`opus` + `medium`/`high`), with the reason stated
- [ ] Description includes "Use PROACTIVELY" if appropriate
- [ ] any model/effort pin uses an alias; main-thread skills/commands carry no pin (or set `context: fork`)
- [ ] Body is a role paragraph plus a contract: inputs (with an exit when the task cannot be done as specified), approval boundary (including what the brief cannot authorise), and the report returned to the caller
- [ ] Leaf workers bar `Agent`/`Task` (`disallowedTools`) or list an explicit `tools:` allowlist
- [ ] MCP token limit strategies defined

### For Skills
- [ ] YAML: name, description (required)
- [ ] Description uses third-person voice
- [ ] Description includes trigger terms
- [ ] If using `agent` field, ensure `context: fork` is set
- [ ] Bundled resources properly organized
- [ ] MCP tool calls: schema reference table, correct/incorrect examples, parameter nesting documented (see `mcp-tool-documentation-guide.md`)
- [ ] `TODO.md` present at skill root (open items / deferred work / placeholders / unverified data logged; "none open yet" if truly empty)

### For Commands
- [ ] Natural language instructions clear
- [ ] Tool usage patterns specified
- [ ] If using `agent` field, ensure `context: fork` is set

## MCP Token Limits

**Critical Constraint**: All MCP tool responses capped at 25000 tokens maximum.

**Mitigation Strategies**:
- Use pagination and filtering
- Divide and conquer (smaller chunks)
- Smart search over broad retrieval
- Never use full dataset dumps

## Platform Considerations

### Claude Desktop Path Requirements

Claude Desktop requires full executable paths (runs in sandbox):

```bash
which npx        # Returns: /opt/homebrew/bin/npx

# Use in config
"command": "/opt/homebrew/bin/npx"   # Correct
"command": "npx"                      # Will fail
```

### Claude Desktop Skill Zip Packaging

Skill `.zip` uploads to Claude.ai Settings → Capabilities → Skills are built into one output directory of your choosing (`<output-dir>/<skill-name>.zip`, for example `dist/claude-desktop/`). Wrapper-folder structure is required; the **30 MB hard cap** applies on individual plans and Team plans alike.

Load **`references/claude-desktop-packaging-guide.md`** for the full skill-zip convention: directory structure, filename patterns, `package_skill.py` / `convert_to_claudeai.py` invocation, size-reduction strategies, pre-upload verification, and real-world examples.

**Tool choice:** `package_skill.py` ships a verbatim wrapper-zip — use it for already-clean sources. `convert_to_claudeai.py` sanitises (strips `allowed-tools`, scrubs prose tool refs, re-serialises frontmatter; preserves fenced code examples) — use it when a skill needs distribution sanitising. The packaging guide's "which to use" subsection has the decision rule.

### Claude Desktop Project Custom Instructions (v3 single-file)

Under the v3 linked-skill pattern (2026-05-19), a skill that backs a Claude Desktop Project emits a **single paste-ready `.md` file** at `<output-dir>/<skill>-project-instructions.md` — side-by-side with the matching `<skill>.zip`. Knowledge files are no longer duplicated into a separate bundle directory; they travel inside the skill `.zip` via Claude.ai's auto-synced skill mount at `/mnt/skills/user/<skill>/` and reach every consumer surface (Desktop, web, iOS, Android).

Each skill that backs a Desktop Project (a "linked skill") carries a single recipe file at `references/cd-project-recipe.md` (Custom Instructions section with surface-aware capability matrix + File Manifest + Sync Log). `/instruction-creator` is the engine that emits the paste-ready `.md` from that recipe on demand — the skill never stores the output inside itself.

Load **`references/cd-project-bundle-guide.md`** for the recipe schema, emission procedure, cross-skill invocation pattern, and scaffolding workflow for new Projects.

### Instruction Size Limits by Surface (check before pasting or packaging)

| Surface / field | Limit | Behaviour when exceeded | Status |
|---|---|---|---|
| Claude Desktop / claude.ai **Instructions for Claude** — the account-level field (formerly Cowork "Global instructions") applied to cloud-run "Claude sessions": Chat, Cowork, Dispatch | **32,768 characters**, counted as Unicode code points (measure with Python `len()`; UTF-16 `.length` and byte counts both over-count) | **Blocking.** The app shows *"These instructions are N characters, over the 32,768 allowed in Claude sessions. Claude won't use them until they're shorter."* Sessions then run with **no** instructions at all. Enforced server-side; the app's local pre-check is 4,000,000 and gives no protection | Observed 2026-09-14 on Desktop 1.52386.6; not documented by Anthropic |
| Cowork **Global instructions** (Settings → Cowork) | Assume the same 32,768 — same server, same session type | Assume blocking | Unverified (see `TODO.md`) |
| Skill `description` frontmatter | 1,024 characters | Upload rejected | Documented above |
| Skill `.zip` upload | 30 MB | Upload rejected | `references/claude-desktop-packaging-guide.md` |
| Claude Code `CLAUDE.md` / `.claude/rules/*.md` | 4 MiB loaded in full; recommendation under 200 lines per file | A larger file is skipped silently | Official docs |
| Claude Code auto-memory `MEMORY.md` | First 200 lines or 25 KB | Remainder not loaded | Official docs |

**Authoring rule for paste fields:** treat every account-level instruction field as a generated artefact, never a hand paste of a fast-moving master. Derive it by script; move harness-specific mechanics (tool routing, MCP limits, filesystem paths) into that surface's adapter or on-demand pointers first; assert the size at generation time, targeting **at most 90% of the cap** so routine growth does not re-trip it; stamp the version so drift is visible. Fuller table, derivation steps, and the over-limit split rule: `references/cross-platform-conversion-guide.md` § "Instruction Size Limits by Surface".

### Distribution Compliance (when authoring/editing a skill)

If you track where each skill is distributed (for example a manifest recording, per skill, whether it ships as a personal-plan skill zip, a team-plan skill zip, or a linked Desktop Project), check the target skill's entry before finalising any new or modified skill and enforce the matching pattern:

| Distribution target | Required pattern in the skill |
|---|---|
| **Personal-plan skill zip** (individual Pro/Max plan) | Skill is portable for Claude.ai (no CC-only frontmatter fields like `allowed-tools` / `model` / `context: fork` / `hooks` — strip via `convert_to_claudeai.py`), no personal paths in distributed text, total folder under 30 MB. |
| **Team-plan skill zip** (Claude Team or Enterprise organisation) | Same as the personal-plan zip **plus** team-readiness: no personal context bleed-through, appropriate for any teammate to use; build with `--team` so the secret/personal-content scan runs. |
| **Linked Desktop Project** (skill paired with a Claude Desktop Project) | (1) Recipe file present at `references/cd-project-recipe.md` with all three sections (Custom Instructions, File Manifest, Sync Log). (2) **Custom Instructions section MUST contain a per-surface capability matrix** — Desktop / web / iOS / Android rows, with reachability of bundled files, MCP servers, scripts, dashboards, image attachments. (3) Both upload artifacts co-located in `<output-dir>`: `<skill>.zip` + `<skill>-project-instructions.md`. (4) Skill must NOT contain a `project-desktop/` subdir or a perpetual bundle output directory (legacy patterns — migrate to the single-file recipe). (5) SKILL.md carries the one-line activation cue: *"When asked to (re)build the Project Custom Instructions for this skill, load `/instruction-creator` and follow its `cd-project-bundle-guide.md`."* (6) After material edits to skill references that change content reachable from the paired Project, prompt the user to re-emit the `.md` — do NOT auto-overwrite (paste-edits may be in flight). |
| **Content format hygiene** (universal — applies to every skill) | No binary files (PDFs, images, audio, video) loose in `references/` if their content is meant to be Claude-readable. Extract to AI-friendly text formats (`.md` / `.csv` / `.jsonl` / etc. per `references/skill-content-formats-guide.md`) and archive originals to a destination appropriate to the skill (local archive dir / synced vault for personal; cloud object store for team-distributed — see the guide). Skill stays lightweight + searchable; originals stay recoverable. |

When setting up or editing a skill, treat these as **mandatory compliance checks** — if a skill is tracked for one of these targets, the corresponding pattern must exist in the skill, and missing patterns must be scaffolded before the edit is considered complete. The content-format hygiene check applies regardless of distribution target.

**Desktop-only Projects (out of scope for /instruction-creator):** Users may have Claude Desktop Projects with NO backing Claude Code skill — these are managed in the Claude Desktop GUI only, need no distribution-manifest entry, and /instruction-creator has no responsibility for them. Only Projects with a paired CC skill require the recipe pattern + emitted `.md`.

## Execution Model

This skill runs in the **main thread context** with full access to all tools (Read, Write, Edit, Bash, Glob, Grep, etc.). This is optimal because:
- Direct access to the full conversation context
- Can read, create, and modify instruction files inline
- No context isolation overhead for interactive workflows

For complex multi-file operations (e.g., creating an entire instruction ecosystem), this skill can spin up subagents with the Agent tool as needed for parallelised work.

## References

Detailed guides in `references/` subdirectory:
- **model-compatibility-index.md**: START HERE for model work — current models and alias targets per provider, the delta chains, which compatibility file to load when, per-model headline deltas, the recommended routing ladder and joint model × effort routing
- **claude-sonnet-5-5-compatibility.md**: Sonnet 5.5 guide (CURRENT, the recommended default model; the `sonnet` alias on the Anthropic API; standalone file) — API changes beyond Opus 5.5's (`between_tools`, account-bound thinking blocks, advisor and computer-tool versions), behavioural deltas with the seven official snippets scoped by effort, model-conditional add-backs against removal-first, routing ladder and effort evidence, system-card findings (task brief as authorisation, factual error rate, illegible thinking), safeguards and fallback to Sonnet 5, Claude Code harness split, remove/add tables, Sonnet checklist, failure modes, field reports, sources
- **claude-opus-5-5-compatibility.md**: Opus-tier guide (CURRENT step-up tier, the `opus` alias; layered on the Opus 5 file) — API breaks (thinking always on, forced `tool_choice`, thinking-block binding, no prefill), effort recalibration to a `medium` default, thinking-instruction removal, unattended early stops with the authorisation carve-out, progress updates, time signals and team design, vision/frontend/pasted-text hardening, reporting and review discipline, Claude Code harness split and effort/cache mechanics, safeguards and fallback, remove/add tables, checklist steps 10–17, failure modes, field reports, sources
- **claude-fable-5-1-compatibility.md**: Fable 5.1 guide (CURRENT frontier): the 5.1 behavioural deltas with the official snippets (progress updates, per-turn tool batching, finish-the-whole-task, scope and test discipline, chat formatting inversion, prose density, unmarked quotations, whole-file rewrites, low-effort search, long outputs at xhigh/max, compaction summaries, async subagents, vision), the API breaks (forced `tool_choice`, thinking-block binding, per-message effort), the harness-injected vs author-owned split for Claude Code, effort and cost calculus with the 5.1 routing table, safeguards and fallback mechanics, system-card findings that change authoring, remove/add tables, migration audit checklist (steps 14–23), failure modes, research sources
- **claude-fable-5-compatibility.md**: Fable 5 guide (the base the 5.1 file extends): Fable 5 deltas (brevity-first/removal-first authoring, reasoning-extraction refusal trap, proactivity boundaries, autonomy/checkpoint patterns, subagent bounds, progress-audit scaffold) + cross-model effort calculus, safeguard/refusal mechanics, Fable 5 migration audit checklist (steps 8–13), failure modes, research sources
- **claude-opus-5-compatibility.md**: previous Opus model; the base the Opus 5.5 file extends — Opus 5 deltas (three removal targets: verification scaffolds, self-correction nudges, review severity pre-filters; effort↮length decoupling; scope/delegation bounds; thinking-disabled artifact mitigations; effort re-baseline incl. `max` tier) + 9-step migration audit checklist with behavioural A/B prompt-debt method, failure modes, field reports, sources
- **claude-opus-4-8-compatibility.md**: Opus-tier guide (superseded by Opus 5 and 5.5) — 4.8 deltas (effort recalibration, native honesty, tool triggering, dynamic workflows) + the literal-interpretation Core Rules rationale with before/after examples, "scaffolding to remove" table, 7-step migration audit checklist, common failure modes, research sources
- **cache-and-token-efficiency.md**: How instruction design interacts with CC's prompt cache — the (model, effort) cache key and the Opus 5.5 / Sonnet 5.5 / Fable 5.1 effort-change exception, the main-thread pin double cache-bust with cost math, the subagent-only rule for pinned skills, safe-pattern table, conversation-fork vs named-subagent cache economics, and other cache-relevant authoring decisions (skill body size, MCP deferral, CLAUDE.md mid-session edits)
- **yaml-frontmatter-complete-guide.md**: All valid fields and options (COMPREHENSIVE)
- **agent-vs-skill-decision-guide.md**: Complete decision matrix for agents vs skills
- **rules-and-content-placement-guide.md**: CLAUDE.md, rules, skills placement decisions
- **common-instruction-patterns.md**: Proven structures and templates
- **cross-platform-conversion-guide.md**: Claude Code → Claude.ai conversion
- **cc-to-codex-conversion-guide.md**: Claude Code → Codex skill AND agent conversion — mechanic map (AskUserQuestion / Skill tool / context: fork / cloud routines / effort / ToolSearch / mcp__ → Codex equivalents), **Codex subagents & custom agents** (GA ~Mar 2026; TOML spec in `~/.codex/agents/`, built-ins, limits, CC-agent→Codex-agent field map — updated 2026-07-20), T1/T2/T3 effort tiers, Tier-A pipeline vs Tier-B hand-authored decision, sensitive-data + harness-tool gates, Phase-1 assessment template (`templates/cc-to-codex-assessment-template.md`)
- **claude-desktop-packaging-guide.md**: Skill `.zip` packaging — output dir, 30 MB upload cap, size-reduction strategies, `package_skill.py` / `convert_to_claudeai.py` patterns
- **cd-project-bundle-guide.md**: Claude Desktop Project Knowledge bundles (directory format) — recipe schema, generation procedure, cross-skill invocation pattern, scaffolding workflow for new Projects
- **skill-content-formats-guide.md**: Format-by-content-type mapping (`.md` / `.csv` / `.jsonl` / `.yaml` / Mermaid / etc.), conversion toolbox (`pdftotext`, `tesseract`, `markitdown`, `pandoc`, `whisper`), source-file archive convention (destination chosen by setup — local archive dir / synced vault for personal, cloud object store for team-distributed), 11-step migration playbook
- **mcp-setup-guide-framework.md**: MCP server setup guide creation framework, scope decision matrix, credential security
- **mcp-tool-documentation-guide.md**: Best practices for documenting MCP tool calls in skills — `input_examples` API field, parameter nesting, correct/incorrect examples
- **creation-checklists.md**: File type selection matrix, MUST/SHOULD/MAY requirements, model selection, sanitisation

## Scripts

Utility scripts in `scripts/` subdirectory:
- **init_skill.py**: Initialize a new skill directory structure
- **package_skill.py**: Package skill for distribution
- **quick_validate.py**: Validate skill structure and YAML
- **convert_to_claudeai.py**: Convert Claude Code skill to Claude.ai format
