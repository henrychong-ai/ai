---
name: instruction-creator
description: "Architect for Claude instruction ecosystems (agents, skills, slash commands, MCP servers, project instructions) with Claude Code best practices — skill templates, 5-step workflow, cache-safe model/effort config, fork subagents (conversation forks vs context: fork), packaging scripts, model compatibility audits (Fable 5, Opus 5, Opus 4.8). Use for creating/updating agents/skills/commands, MCP setup guides, team distribution sanitisation."
---

# Instruction Creator Skill

This skill provides complete guidance for creating and reviewing Claude instruction files across the entire instruction ecosystem.

**Updated:** 2026-09-01 — Fable 5.1 (rel. 2026-09-01) delta pass: `references/claude-fable-5-1-compatibility.md` added (9 behavioural deltas, harness-injected vs author-owned rule, effort/cost calculus, safeguards/fallback, system-card authoring findings); models table, effort ladder (`max` added), cache math, and checklists refreshed. 2026-08-14 — Fork subagents: "Forking — Two Distinct Mechanisms" disambiguation (conversation forks `subagent_type: "fork"`/`/subtask` vs `context: fork` frontmatter), fork delegation calculus (forks cannot be model/effort-pinned), `background:` frontmatter field, cache-reference correction (`context: fork` skills receive NO conversation history), Fable 5 fork-economics delta, CC→Codex fork mapping. 2026-08-03 — Opus 5 compatibility reference added (`references/claude-opus-5-compatibility.md`): removal-first reaches the Opus tier (verification scaffolds, self-correction nudges, review severity pre-filters now hurt), effort↮length decoupling, thinking-on-by-default mechanics, behavioural A/B prompt-debt audit. 2026-06-16 — CC→Codex conversion guide added (`references/cc-to-codex-conversion-guide.md` + `templates/cc-to-codex-assessment-template.md`): mechanic map, T1/T2/T3 tiers, Tier-A/B distribution decision, data + harness-tool gates. 2026-06-10 — Fable 5 (released 2026-06-09; **new tier above Opus**, not an Opus replacement) multi-model restructure; per-model deltas now live in `references/claude-<model>-compatibility.md` (supersedes the single-model 4.8 pass, 2026-05-30). Same day: cache-safety & token-efficiency rules — the CC prompt cache is keyed by (model, effort), so model/effort pins belong in subagent contexts only (`references/cache-and-token-efficiency.md`).

## ⚠️ Model-Aware Instruction Authoring (MANDATORY)

Frontier Claude models follow instructions literally and strongly — and each release shifts *how* to author for them. The 8 Core Rules below are **durable**: they originated with Opus 4.7 and apply unchanged through Opus 4.8, Fable 5, and Fable 5.1. Per-model behavioural deltas live in the compatibility references — **load the matching file whenever auditing or authoring for a specific model**; for instructions consumed by mixed/unknown models, author to the Core Rules + the brevity-first/removal-first principle (established by Fable 5, extended to the Opus tier by Opus 5).

### Current Models → Compatibility References

| Model | Role | CC alias | Reference |
|---|---|---|---|
| **Fable 5.1** (`claude-fable-5-1`, rel. 2026-09-01) | Frontier tier above Opus — hard, long-horizon work; $10/$50 per MTok (2× Opus), cache reads $0.25/MTok | `fable` | `references/claude-fable-5-1-compatibility.md` (layered on the Fable 5 file) |
| Fable 5 (`claude-fable-5`, rel. 2026-06-09) | Superseded — Fable 5.1 is drop-in; Fable 5 file retained as the base (Parts 1–3) that the 5.1 file extends | — | `references/claude-fable-5-compatibility.md` |
| **Opus 5** (`claude-opus-5`, rel. July 2026) | Opus-tier workhorse — step-change over 4.8; agentic coding, review, routine traffic; $5/$25 per MTok (unchanged) | `opus` | `references/claude-opus-5-compatibility.md` |
| Opus 4.8 (`claude-opus-4-8`) and earlier | Superseded — migrate using the Opus 5 file; 4.8 file retained for Core Rules rationale (Part 1) | — | `references/claude-opus-4-8-compatibility.md` |

### Core Rules (durable across Opus 4.7/4.8, Fable 5.x, and Opus 5)

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

### Fable 5 Headline Deltas (vs Opus 4.8) — base, still apply on Fable 5.1

One API break (thinking cannot be disabled — explicit `disabled` 400s; omit the param). The behavioural shifts that change how you author:

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Brevity-first / removal-first** | brief instructions steer most behaviours; legacy prescriptive skills are "often too prescriptive… can degrade output quality" | Collapse don't-lists into one coherent positive instruction; **test default behaviour before keeping any scaffold** |
| **⚠️ Reasoning-extraction refusals** | "show your thinking / repeat your reasoning" instructions trigger `reasoning_extraction` refusals (fallback → Opus 4.8 or Opus 5) | **Audit and remove** from every skill/agent/command — the one refusal authors cause themselves |
| **More proactive / elaborative** | unrequested actions and scope creep without steering | Add one brief boundary instruction where scope discipline matters ("assessment vs fix", "simplest thing that works") |
| **Pauses / checkpoints more often** | checks in early in long sessions; rare text-only early stops | Autonomous skills: explicit autonomy language + positive pause criteria (destructive ops, scope changes, user-only input) |
| **Eager, dependable subagents** | dispatches readily; sustains parallel/long-running subagents | Keep fan-out bounds (caps, dedup, single-writer apply); drop "remember to delegate" reminders |
| **Long runs, evidence-anchored** | minutes–hours at high effort; progress fabrication ~eliminated by an audit instruction | Long-run agents: add audit-claims-against-tool-results + final-message re-grounding; long waits → background tasks |

4.8's deletions stay deleted on Fable 5 (honesty nudges, tool-call reminders, forced progress summaries, manual thinking control) — do not reintroduce.

### Fable 5.1 Headline Deltas (vs Fable 5) — author/audit deltas

Drop-in: Anthropic says Fable 5 prompts "should perform well on Claude Fable 5.1 without changes", and cache reads now cost a quarter of the Fable 5 rate. Two API breaks matter: forced `tool_choice` (`any` / `tool`) now 400s, and thinking blocks are bound to both the producing model and the exact conversation prefix.

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Fewer progress updates** | writes less user-facing text during long tool chains, more so at higher effort | **Remove** "hold all findings for the final response" lines; add the opening-line/updates/recap line only where a human watches |
| **One tool call per turn** | in coding and computer-use loops where the next reads are implied, not requested | Custom loops: append the per-turn batching nudge after each batch of tool results |
| **Less chat formatting** | uses bold, headers, lists, and quotation marks less than earlier models | **Inverts the old anti-formatting doctrine**: remove those rules, add a positive when-to-format rule |
| **Extras beyond the task** | unrequested fixes, adjacent-file edits, surplus test files, and this **rises with effort** (FrontierCode peaks at `medium`) | Coding skills: add the scope-and-test leave-out block plus a brevity line; re-baseline effort pins downward |
| **Whole-file rewrites** | rewrites entire files for small edits more than Fable 5 | File-editing agents: add the surgical-edit line |
| **Answers from memory at `low`** | calls search and retrieval tools less often at low effort | Raise effort for those turns, or add the search-verification nudge |
| **Denser prose, unmarked quotations** | longer sentences, fewer paragraph breaks; reproduces source passages without marking them | Add the mannered-prose line; give summarising skills one complete quotation worked example |

**Harness-injected on Claude Code:** version 2.1.257 already injects, verbatim, the over-planning block, the progress-updates line, both finish-the-task blocks (autonomy and "Delivering work"), the state-change caution, the terminal-output note, and the per-turn batching nudge. **Do not duplicate any of these in CLAUDE.md, rules, skills, or agents.** Duplication is a token tax on every turn and over-steers a model already carrying the instruction. Skills shipped to other surfaces (Claude Desktop and Team zips, Codex, Gemini, ChatGPT) receive none of them and must embed what they depend on. Full split and the author-owned list: Part 2A of `references/claude-fable-5-1-compatibility.md`.

### Opus 5 Headline Deltas (vs Opus 4.8) — author/audit deltas

Runs 4.8 prompts fine out of the box; thinking on by default (disable only at effort ≤ `high` — else 400); effort ladder gains `max`. Removal-first now applies at the Opus tier — three deltas REMOVE instructions, three ADD them:

| Delta | What changed | What to do in instructions |
|---|---|---|
| **⚠️ Over-verification** | verifies its own work unprompted; "final verification step" / "verify with a subagent" scaffolds now cause wasteful re-verification | **Remove** verification scaffolds from every skill/agent/command |
| **Self-correction nudges** | catches and fixes its own mistakes natively | **Remove** "double-check your answer" / "re-verify before responding" |
| **Review severity pre-filters** | "only report high-severity" is followed literally — recall drops | **Remove** pre-filters; ask for everything, filter in a separate pass |
| **Effort↮length decoupling** | effort controls thinking, NOT visible response length; replies and written files run longer by default | **Add** explicit length calibration — separately for chat, narration cadence, and written deliverables |
| **Scope expansion** | widens tasks, adds unrequested steps | **Add** a one-line scope boundary to narrow-task skills |
| **Eager subagent spawning** | delegates more readily; multiplies cost on small tasks | **Add** delegation criteria or deterministic caps |

Prior deletions stay deleted (4.8's honesty/progress scaffolds, Fable 5's reasoning-extraction requests). Full detail, official template snippets, migration checklist, failure modes, and field reports: `references/claude-opus-5-compatibility.md`.

### Prompt-Debt A/B Audit (cross-model)

Before rewriting any instruction file for a new model, isolate the failure behaviourally: pick one repeatable task with clear success criteria; run it twice in fresh sessions, identical except for the skill's presence; compare to determine whether the skill or the model causes the failure; then cut the specific offending instruction. Cheaper and more decisive than a read-through audit — a single stale line (e.g. a leftover "wait for another agent" handoff) can account for systematic failures.

### Effort Is a Harness Parameter, Not Prompt Content

Instruction file prose cannot escalate effort. Do not write "assume high effort" or "think deeply" in CLAUDE.md / SKILL.md body content. Effort is set via (priority order):
- `CLAUDE_CODE_EFFORT_LEVEL` env var (highest priority)
- `effort:` field in YAML frontmatter (per-skill/agent/command)
- `/effort low|medium|high|xhigh|max` (per-session)
- model default — `high` on Fable 5.1, Fable 5, Opus 5, Sonnet 5, and Opus 4.8

Fable 5.x recommendation: start `high` (the default). On Fable 5.1, `medium` roughly matches Fable 5 at lower cost, and `low` is often competitive with Opus and Sonnet on cost per task while scoring higher; `xhigh`/`max` give the largest gains but add thinking time and, on coding, more out-of-scope edits. Re-run the effort sweep on 5.1 even if one was run on Fable 5: level names do not map to the same amount of thinking across models. The 4.8-era "xhigh for coding/agentic" rule does **not** carry over. Opus 5 recommendation: default `high`; use `low`/`medium` liberally as the primary cost/latency control wherever quality holds (Anthropic, official); step up to `xhigh`/`max` (API ladder) for demanding agentic coding. Re-baseline existing `effort:` pins on upgrade — run an effort sweep rather than carrying prior-model pins forward.

### Model × Effort Is ONE Decision (cross-model calculus)

Effort labels are **not comparable across models**: Fable 5.1 at `medium` scores about level with Fable 5 at `xhigh` on FrontierCode at roughly half the cost per task, and Anthropic reported Fable 5 at `medium` outperforming every other model at any effort level. When pinning model+effort for a subagent/skill, decide jointly:

| Dominant constraint | Better pick |
|---|---|
| Capability ceiling, latency-tolerant | **Fable 5.1 at modest effort** — `medium`/`low` can beat Opus-tier `xhigh`, often at less than the 2× sticker cost (fewer tokens at lower effort, and cache reads at a quarter of the Fable 5 rate; measure, don't assume) |
| Latency-sensitive / interactive | **Opus 5 or smaller** — Fable's first token can take ~a minute regardless of effort |
| Routine high-volume | **Opus 5 / Sonnet / Haiku** — official routing: hard, long-horizon jobs → Fable 5.1; routine traffic → Opus-or-smaller. Opus 5 at `low`/`medium` remains a cost-efficient workhorse point, but **Fable 5.1 at `low`/`medium` now belongs in the cost-per-task comparison** — per-task cost can land below Opus 5 at low to high effort |

**Cache safety is the third axis.** The CC prompt cache is keyed by **(model, effort)** jointly — a main-thread pin of *either* forces a full uncached re-read of the conversation at activation and a partial re-read at revert, regardless of which direction you pin. Execute pinned instructions as subagents (see Model Configuration below); full mechanics + cost math: `references/cache-and-token-efficiency.md`.

### Deep Dive

Per-model detail — full delta rationale, scaffolding to remove/add tables, migration audit checklists, failure modes, research sources:
- **Fable 5.1:** `references/claude-fable-5-1-compatibility.md` (CURRENT frontier: the 5.1 deltas, harness-injected vs author-owned split, effort/cost calculus, safeguards and fallback, system-card authoring findings; layered on the Fable 5 file)
- **Fable 5:** `references/claude-fable-5-compatibility.md` (the base the 5.1 file extends: brevity-first authoring, effort calculus, safeguard/refusal mechanics, autonomy patterns)
- **Opus 5:** `references/claude-opus-5-compatibility.md` (incl. removal targets, official template snippets, thinking-disabled artifact mitigations, migration checklist, field reports)
- **Opus 4.8:** `references/claude-opus-4-8-compatibility.md` (incl. the Core Rules rationale in Part 1)

Load the matching reference whenever auditing an existing CLAUDE.md / skill / agent / command for a target model.

---

## Instruction File Types

| Type | Location | Purpose | Loading |
|------|----------|---------|---------|
| **CLAUDE.md** | `~/.claude/` or `./` | User preferences, identity | Always (auto) |
| **Rules** | `~/.claude/rules/` or `./.claude/rules/` | Focused config, patterns | Always (auto) |
| **Agents** | `~/.claude/agents/*.md` | Autonomous domain specialists | On trigger/Task tool |
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

**Token Budget Guidelines:**
| File Type | Recommended | Maximum |
|-----------|-------------|---------|
| Global CLAUDE.md | 800-1200 lines | ~1500 lines |
| Each rules file | 50-200 lines | ~300 lines |
| Project CLAUDE.md | 100-300 lines | ~500 lines |

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
# model: <alias>                    # OMIT by default — inherits session model; pin only when clearly warranted (see Model Configuration)
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

- **Default: OMIT the `model` field entirely** — the agent/skill/command then inherits the session's model. This is the correct choice for almost all instructions: it keeps them forward-compatible as models improve and respects the user's session-level model choice.
- **Pin only when the instruction clearly and unambiguously calls for it** — typically a high-volume mechanical subagent where a smaller/cheaper tier is obviously sufficient (pattern scanning, format conversion, bulk retrieval). Make that judgement per-instruction at creation time; do not pin by habit.
- **Never pin upward to a larger model "for quality"** — that decision belongs to the session, not the instruction file. (Doubly so for `fable` at 2× Opus cost per token, though on Fable 5.1 cache reads bill at a quarter of the Fable 5 rate.)
- **When a pin IS justified, decide model and effort together** (see Model × Effort above): for capability-bound, latency-tolerant subagent work, `fable` at `medium`/`low` effort can dominate `opus` at `xhigh`.
- **Pins are cache-safe only in subagent contexts.** The CC prompt cache is keyed by (model, effort) — a main-thread skill/command pin double cache-busts the session (full uncached re-read at activation, partial re-read at revert). Agents are safe by construction (own subagent conversation, own cache). **A skill/command with a hardcoded `model:`/`effort:` must always run as a subagent — set `context: fork` (+ `agent:`) alongside the pin.** Mechanics + cost math: `references/cache-and-token-efficiency.md`.
- **Conversation forks cannot be pinned.** `subagent_type: "fork"` ignores `model` overrides and has no frontmatter — a fork always bills the session model at session effort. When a pin matters, delegate to a named agent instead of forking (see Forking — Two Distinct Mechanisms).
- **Use aliases, not version-pinned IDs**, on the rare occasions a pin is justified (aliases track the latest model in the tier): `fable`, `opus`, `sonnet`, `haiku`.
- **`inherit`**: explicit equivalent of omitting (agents only).
- **Priority order** (named subagents): Task tool override → Agent YAML → Inherit → System default. Conversation forks bypass this entirely — always the session model.

### Agent Template Structure

```markdown
---
name: agent-name
description: [Specialization]. [Capabilities]. Use PROACTIVELY for [triggers].
---

# **AGENT NAME: SPECIALIZED PURPOSE**

[Agent identity and mission]

## AUTO-ACTIVATION SEQUENCE
1. Load Context: Reference project-instructions.md if applicable
2. Tool Readiness: Prepare TodoWrite and MCP strategies
3. Success Metrics: Define execution excellence standards

## DOMAIN EXPERTISE
[Specialized knowledge and capabilities]

## OPERATIONAL PROTOCOLS
[Workflows, tool usage, MCP token strategies]
```

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
| `Explore` | Haiku | Read-only | Fast analysis, file discovery |
| `Plan` | Sonnet | Read-only | Research before planning |
| `general-purpose` | Sonnet | All | Complex tasks with edits |
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
---
```

| Value | Symbol | Use When |
|-------|--------|----------|
| `low` | ○ | Quick lookups, simple transforms, high-volume tasks |
| `medium` | ◐ | Balanced analysis, most general tasks |
| `high` | ● | Complex reasoning, strategic analysis, deep research |
| `xhigh` | ◉ | Long-horizon, capability-sensitive work (Fable 5.x, Opus 5, Opus 4.8/4.7, Sonnet 5) |
| `max` | ◎ | Absolute ceiling, unconstrained token spend (Fable 5.x, Opus 5, Opus 4.8/4.7/4.6, Sonnet 5/4.6); rarely justified in a pin; on Fable 5.1 `xhigh` matches `max` at 19 to 25% fewer output tokens on knowledge work |
| (omit) | — | Inherit session effort (default, most common) |

**Default: OMIT the `effort` field** — inherit the session's effort. Specify it only when the instruction clearly and unambiguously calls for a different depth (e.g. a trivial high-volume lookup). Do not set higher effort to chase quality — that is the session's decision. Effort values are model-relative (on Fable 5.1, `medium` roughly matches Fable 5 at lower cost — see Model × Effort above); re-baseline pinned values when the model line changes.

**Cache rule:** effort pins share the model pin's cache behaviour — the CC cache is keyed by (model, effort), so a main-thread effort pin double cache-busts the session, with the entry re-read billed at the *active* model's rate. Pin only on agents or `context: fork` skills; a pin resolving to the already-active level keeps the cache. Detail: `references/cache-and-token-efficiency.md`.

**Priority:** `CLAUDE_CODE_EFFORT_LEVEL` env var > frontmatter > session `/effort` > model default

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

Load **`references/skill-content-formats-guide.md`** for the format-by-content-type table (.md / .csv / .tsv / .jsonl / .yaml / Mermaid / etc.), conversion toolbox (`pdftotext`, `tesseract`, `markitdown`, `pandoc`, `whisper`), the SKILL.md pointer pattern, the 11-step migration playbook for skills with existing binaries, and CD-S/CD-T/CD-P implications.

### Visibility Controls

| Field | Effect |
|-------|--------|
| `user-invocable: false` | Hide from /menu, still allows auto-discovery and Skill tool |
| `disable-model-invocation: true` | Block programmatic invocation via Skill tool |

### Repo-Scoped Run Skills → delegate to `/run-skill-generator`

A **run skill** tells an agent how to build, launch, and **drive** one app from a clean machine. It lives in the **target repo** at `<unit>/.claude/skills/run-<unit>/`, not in `~/.claude/skills/`.

- **Authoring:** do **not** hand-roll one with the generic 5-step process — invoke the built-in **`/run-skill-generator`**. It ships per-project-type examples (cli/server/tui/electron/web/library), a canonical template, and a *build-and-drive* definition-of-done (you must actually run + screenshot the app; every code block must be a command that worked this session). Refine an existing run skill rather than rewriting it.
- **Usage / verification:** the built-in **`/run`** consumes it — it matches by `description` across `.claude/skills/*/SKILL.md` up the dir tree (not by name/path), and falls back to per-type patterns if none exists.
- **Deltas vs personal/distributed skills:** (1) **committed to the repo**, shared via **git**, not the skill-zip pipeline; (2) **CD-S/CD-T/CD-P distribution markers and the 30 MB zip cap do NOT apply**; (3) **secrets hygiene still applies** — the committed driver/`SKILL.md` must point at `.env.example` / a secrets manager, never inline real credentials; (4) **the `description` is the trigger** — use the verbs an agent types ("run/start/build/screenshot"); keep `SKILL.md` short, the driver is the deliverable.

## Creating Slash Commands

Slash commands are natural language instruction prompts (NOT executable code).

### Command YAML Frontmatter (All Optional)

```yaml
---
description: Brief command purpose
allowed-tools: Bash(git:*), Read
argument-hint: [pr-number] [priority]
model: sonnet
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
- Multi-step workflows requiring TodoWrite
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
| **TodoWrite** | Yes | No | No |
| **context: fork** | N/A | Yes | Yes |
| **Token Efficiency** | Lower | Higher | Highest |
| **File Structure** | Single | Multi-file | Single |

## YAML Frontmatter Quick Reference

Agent / Skill / Command frontmatter blocks are documented inline under each "Creating ..." section above. For the complete cross-reference of every valid field (required vs optional, defaults, value enums, gotchas), load **`references/yaml-frontmatter-complete-guide.md`**.

## Review Checklist

### For Agents
- [ ] YAML: name, description (omit model/effort unless clearly warranted)
- [ ] Description includes "Use PROACTIVELY" if appropriate
- [ ] model/effort omitted by default; any pin is justified and uses an alias
- [ ] TodoWrite capability for complex operations
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

Skill `.zip` uploads to Claude.ai Settings → Capabilities → Skills go to `~/.claude/skills-claude-desktop/<skill-name>.zip`. Wrapper-folder structure is required; **30 MB hard cap** applies to both CD-S (personal Max/Pro plan) and CD-T (Team plan).

Load **`references/claude-desktop-packaging-guide.md`** for the full skill-zip convention: directory structure, filename patterns, `package_skill.py` / `convert_to_claudeai.py` invocation, size-reduction strategies, pre-upload verification, and real-world examples.

**Tool choice:** `package_skill.py` ships a verbatim wrapper-zip — use it for already-clean sources. `convert_to_claudeai.py` sanitises (strips `allowed-tools`, scrubs prose tool refs, re-serialises frontmatter; preserves fenced code examples) — use it when a skill needs distribution sanitising. The packaging guide's "which to use" subsection has the decision rule.

### Claude Desktop Project Custom Instructions (v3 single-file)

Under the v3 linked-skill pattern (2026-05-19), a skill that backs a Claude Desktop Project emits a **single paste-ready `.md` file** at `~/.claude/skills-claude-desktop/<skill>-project-instructions.md` — side-by-side with the matching `<skill>.zip`. Knowledge files are no longer duplicated into a separate bundle directory; they travel inside the skill `.zip` via Claude.ai's auto-synced skill mount at `/mnt/skills/user/<skill>/` and reach every consumer surface (Desktop, web, iOS, Android).

Each skill that backs a CD-P carries a single recipe file at `references/cd-project-recipe.md` (Custom Instructions section with surface-aware capability matrix + File Manifest + Sync Log). `/instruction-creator` is the engine that emits the paste-ready `.md` from that recipe on demand — the skill never stores the output inside itself.

Load **`references/cd-project-bundle-guide.md`** for the recipe schema, emission procedure, cross-skill invocation pattern, and scaffolding workflow for new Projects.

### Distribution-Marker Compliance (when authoring/editing a skill)

Before finalising any new or modified skill, **check `~/.claude/skills/git/references/distribution-manifest.md`** for the target skill's distribution markers and enforce compliance:

| Marker | Required pattern in the skill |
|---|---|
| **CD-S ✓ / ○** (Skill .zip on a personal plan) | Skill is portable for Claude.ai (no CC-only frontmatter fields like `allowed-tools` / `model` / `context: fork` / `hooks` — strip via `convert_to_claudeai.py`), no personal paths in distributed text, total folder under 30 MB. |
| **CD-T ✓ / ○** (Skill .zip on a Team plan) | Same as CD-S **plus** team-readiness: no personal context bleed-through, appropriate for any teammate to use. |
| **CD-P ✓ / ○** (Linked Skill — paired Claude Desktop Project) | (1) Recipe file present at `references/cd-project-recipe.md` with all three sections (Custom Instructions, File Manifest, Sync Log). (2) **Custom Instructions section MUST contain a per-surface capability matrix** — Desktop / web / iOS / Android rows, with reachability of bundled files, MCP servers, scripts, dashboards, image attachments. (3) Both upload artifacts MUST be co-located at `~/.claude/skills-claude-desktop/`: `<skill>.zip` + `<skill>-project-instructions.md`. (4) Skill must NOT contain a `project-desktop/` subdir or perpetual bundle output directory (legacy v1/v2 patterns — migrate to v3 single-file recipe). (5) SKILL.md carries the one-line activation cue: *"When asked to (re)build the Project Custom Instructions for this skill, load `/instruction-creator` and follow its `cd-project-bundle-guide.md`."* (6) After material edits to skill references that change content reachable from the paired Project, prompt the user to re-emit the `.md` — do NOT auto-overwrite (paste-edits may be in flight). |
| **Content format hygiene** (universal — applies to every skill) | No binary files (PDFs, images, audio, video) loose in `references/` if their content is meant to be Claude-readable. Extract to AI-friendly text formats (`.md` / `.csv` / `.jsonl` / etc. per `references/skill-content-formats-guide.md`) and archive originals to a destination appropriate to the skill (local archive dir / synced vault for personal; cloud object store for team-distributed — see the guide). Skill stays lightweight + searchable; originals stay recoverable. |

When setting up or editing a skill, treat these as **mandatory compliance checks** — if a skill is marked CD-S/CD-T/CD-P in the manifest, the corresponding pattern must exist in the skill, and missing patterns must be scaffolded before the edit is considered complete. The content-format hygiene check applies regardless of distribution markers.

**CD-only Projects (out of scope for /instruction-creator):** Users may have Claude Desktop Projects with NO backing Claude Code skill — these are managed in the Claude Desktop GUI only. They are NOT tracked in `distribution-manifest.md` and /instruction-creator has no responsibility for them. Only Projects with a paired CC skill (CD-P `✓`/`○`) require the recipe pattern + emitted `.md`.

## Execution Model

This skill runs in the **main thread context** with full access to all tools (Read, Write, Edit, Bash, Glob, Grep, etc.). This is optimal because:
- Direct access to the full conversation context
- Can read, create, and modify instruction files inline
- No context isolation overhead for interactive workflows

For complex multi-file operations (e.g., creating an entire instruction ecosystem), this skill can spin up Task tool subagents as needed for parallelised work.

## References

Detailed guides in `references/` subdirectory:
- **claude-fable-5-1-compatibility.md**: Fable 5.1 guide (CURRENT frontier): the 5.1 behavioural deltas with the official snippets (progress updates, per-turn tool batching, finish-the-whole-task, scope and test discipline, chat formatting inversion, prose density, unmarked quotations, whole-file rewrites, low-effort search, long outputs at xhigh/max, compaction summaries, async subagents, vision), the API breaks (forced `tool_choice`, thinking-block binding, per-message effort), the harness-injected vs author-owned split for Claude Code, effort and cost calculus with the 5.1 routing table, safeguards and fallback mechanics, system-card findings that change authoring, remove/add tables, migration audit checklist (steps 14–23), failure modes, research sources
- **claude-fable-5-compatibility.md**: Fable 5 guide (the base the 5.1 file extends): Fable 5 deltas (brevity-first/removal-first authoring, reasoning-extraction refusal trap, proactivity boundaries, autonomy/checkpoint patterns, subagent bounds, progress-audit scaffold) + cross-model effort calculus, safeguard/refusal mechanics, Fable 5 migration audit checklist (steps 8–13), failure modes, research sources
- **claude-opus-5-compatibility.md**: Opus-tier guide (CURRENT) — Opus 5 deltas (three removal targets: verification scaffolds, self-correction nudges, review severity pre-filters; effort↮length decoupling; scope/delegation bounds; thinking-disabled artifact mitigations; effort re-baseline incl. `max` tier) + 9-step migration audit checklist with behavioural A/B prompt-debt method, failure modes, field reports, sources
- **claude-opus-4-8-compatibility.md**: Opus-tier guide (superseded by Opus 5) — 4.8 deltas (effort recalibration, native honesty, tool triggering, dynamic workflows) + the literal-interpretation Core Rules rationale with before/after examples, "scaffolding to remove" table, 7-step migration audit checklist, common failure modes, research sources
- **cache-and-token-efficiency.md**: How instruction design interacts with CC's prompt cache — the (model, effort) cache key, the main-thread pin double cache-bust with cost math, the subagent-only rule for pinned skills, safe-pattern table, conversation-fork vs named-subagent cache economics, and other cache-relevant authoring decisions (skill body size, MCP deferral, CLAUDE.md mid-session edits)
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
