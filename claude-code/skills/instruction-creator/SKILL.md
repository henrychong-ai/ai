---
name: instruction-creator
description: Architect for Claude instruction ecosystems (agents, skills, slash commands, MCP servers, project instructions) with Claude Code best practices — skill templates, 5-step workflow, cache-safe model/effort config, packaging scripts, model compatibility audits (Fable 5, Opus 4.8). Use for creating/updating agents/skills/commands, MCP setup guides, team distribution sanitisation.
---

# Instruction Creator Skill

This skill provides complete guidance for creating and reviewing Claude instruction files across the entire instruction ecosystem.

**Updated:** 2026-06-16 — CC→Codex conversion guide added (`references/cc-to-codex-conversion-guide.md` + `templates/cc-to-codex-assessment-template.md`): mechanic map, T1/T2/T3 tiers, Tier-A/B distribution decision, data + harness-tool gates. 2026-06-10 — Fable 5 (released 2026-06-09; **new tier above Opus**, not an Opus replacement) multi-model restructure; per-model deltas now live in `references/claude-<model>-compatibility.md` (supersedes the single-model 4.8 pass, 2026-05-30). Same day: cache-safety & token-efficiency rules — the CC prompt cache is keyed by (model, effort), so model/effort pins belong in subagent contexts only (`references/cache-and-token-efficiency.md`).

## ⚠️ Model-Aware Instruction Authoring (MANDATORY)

Frontier Claude models follow instructions literally and strongly — and each release shifts *how* to author for them. The 8 Core Rules below are **durable**: they originated with Opus 4.7 and apply unchanged through Opus 4.8 and Fable 5. Per-model behavioural deltas live in the compatibility references — **load the matching file whenever auditing or authoring for a specific model**; for instructions consumed by mixed/unknown models, author to the Core Rules + Fable 5's brevity-first principle.

### Current Models → Compatibility References

| Model | Role | CC alias | Reference |
|---|---|---|---|
| **Fable 5** (`claude-fable-5`, rel. 2026-06-09) | Frontier tier above Opus — hard, long-horizon work; $10/$50 per MTok (2× Opus) | `fable` | `references/claude-fable-5-compatibility.md` |
| **Opus 4.8** (`claude-opus-4-8`, rel. 2026-05-28) | Opus-tier workhorse — routine and latency-sensitive traffic | `opus` | `references/claude-opus-4-8-compatibility.md` |
| Opus 4.7 and earlier | Superseded — migrate using the 4.8 file | — | 4.8 file Part 1 (Core Rules origin + rationale) |

### Core Rules (durable across Opus 4.7/4.8 and Fable 5)

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

### Fable 5 Headline Deltas (vs Opus 4.8) — author/audit deltas

One API break (thinking cannot be disabled — explicit `disabled` 400s; omit the param). The behavioural shifts that change how you author:

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Brevity-first / removal-first** | brief instructions steer most behaviours; legacy prescriptive skills are "often too prescriptive… can degrade output quality" | Collapse don't-lists into one coherent positive instruction; **test default behaviour before keeping any scaffold** |
| **⚠️ Reasoning-extraction refusals** | "show your thinking / repeat your reasoning" instructions trigger `reasoning_extraction` refusals (fallback → Opus 4.8) | **Audit and remove** from every skill/agent/command — the one refusal authors cause themselves |
| **More proactive / elaborative** | unrequested actions and scope creep without steering | Add one brief boundary instruction where scope discipline matters ("assessment vs fix", "simplest thing that works") |
| **Pauses / checkpoints more often** | checks in early in long sessions; rare text-only early stops | Autonomous skills: explicit autonomy language + positive pause criteria (destructive ops, scope changes, user-only input) |
| **Eager, dependable subagents** | dispatches readily; sustains parallel/long-running subagents | Keep fan-out bounds (caps, dedup, single-writer apply); drop "remember to delegate" reminders |
| **Long runs, evidence-anchored** | minutes–hours at high effort; progress fabrication ~eliminated by an audit instruction | Long-run agents: add audit-claims-against-tool-results + final-message re-grounding; long waits → background tasks |

4.8's deletions stay deleted on Fable 5 (honesty nudges, tool-call reminders, forced progress summaries, manual thinking control) — do not reintroduce.

### Effort Is a Harness Parameter, Not Prompt Content

Instruction file prose cannot escalate effort. Do not write "assume high effort" or "think deeply" in CLAUDE.md / SKILL.md body content. Effort is set via (priority order):
- `CLAUDE_CODE_EFFORT_LEVEL` env var (highest priority)
- `effort:` field in YAML frontmatter (per-skill/agent/command)
- `/effort low|medium|high|xhigh` (per-session)
- model default — `high` on Fable 5 and Opus 4.8

Fable 5 recommendation: start `high` (the default), reserve `xhigh` for the most capability-sensitive workloads — the 4.8-era "xhigh for coding/agentic" rule does **not** carry over. Re-baseline existing `effort:` pins on upgrade.

### Model × Effort Is ONE Decision (cross-model calculus)

Effort labels are **not comparable across models**: Fable 5 at `medium` outperforms every other model at any effort level, and even Fable `low` often exceeds prior models' `xhigh` (Anthropic, official). When pinning model+effort for a subagent/skill, decide jointly:

| Dominant constraint | Better pick |
|---|---|
| Capability ceiling, latency-tolerant | **Fable 5 at modest effort** — `medium`/`low` can beat Opus 4.8 at `xhigh`, often at less than the 2× sticker cost (fewer tokens at lower effort; measure, don't assume) |
| Latency-sensitive / interactive | **Opus 4.8 or smaller** — Fable's first token can take ~a minute regardless of effort |
| Routine high-volume | **Opus 4.8 / Sonnet / Haiku** — official routing: hard, long-horizon jobs → Fable 5; routine traffic → Opus-or-smaller |

**Cache safety is the third axis.** The CC prompt cache is keyed by **(model, effort)** jointly — a main-thread pin of *either* forces a full uncached re-read of the conversation at activation and a partial re-read at revert, regardless of which direction you pin. Execute pinned instructions as subagents (see Model Configuration below); full mechanics + cost math: `references/cache-and-token-efficiency.md`.

### Deep Dive

Per-model detail — full delta rationale, scaffolding to remove/add tables, migration audit checklists, failure modes, research sources:
- **Fable 5:** `references/claude-fable-5-compatibility.md` (incl. effort calculus, safeguard/refusal mechanics, autonomy patterns)
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
- **Apply the Core Rules** (see Model-Aware Instruction Authoring at the top of this skill): positive framings over negative constraints, explicit scope, resolved precedence for conflicting directives, marked illustrative lists, scoped rhetorical language, task-complexity calibration for length. On Fable 5, also brevity-first: one coherent instruction over enumerated don't-lists.

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
- **Never pin upward to a larger model "for quality"** — that decision belongs to the session, not the instruction file. (Doubly so for `fable` at 2× Opus cost.)
- **When a pin IS justified, decide model and effort together** (see Model × Effort above): for capability-bound, latency-tolerant subagent work, `fable` at `medium`/`low` effort can dominate `opus` at `xhigh`.
- **Pins are cache-safe only in subagent contexts.** The CC prompt cache is keyed by (model, effort) — a main-thread skill/command pin double cache-busts the session (full uncached re-read at activation, partial re-read at revert). Agents are safe by construction (own subagent conversation, own cache). **A skill/command with a hardcoded `model:`/`effort:` must always run as a subagent — set `context: fork` (+ `agent:`) alongside the pin.** Mechanics + cost math: `references/cache-and-token-efficiency.md`.
- **Use aliases, not version-pinned IDs**, on the rare occasions a pin is justified (aliases track the latest model in the tier): `fable`, `opus`, `sonnet`, `haiku`.
- **`inherit`**: explicit equivalent of omitting (agents only).
- **Priority order**: Task tool override → Agent YAML → Inherit → System default

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

### Context Fork Feature

Use `context: fork` to run skills in an **isolated sub-agent context**:

```yaml
---
name: code-analyzer
description: Analyze code patterns and generate reports
context: fork          # Isolated execution
agent: Explore         # Use fast read-only agent
---
```

**When to use `context: fork`:**
- Verbose output (test runs, large file analysis)
- Multi-step operations that would clutter context
- Complex workflows where only the summary matters

**Agent options for `context: fork`:**
| Agent | Model | Tools | Use Case |
|-------|-------|-------|----------|
| `Explore` | Haiku | Read-only | Fast analysis, file discovery |
| `Plan` | Sonnet | Read-only | Research before planning |
| `general-purpose` | Sonnet | All | Complex tasks with edits |
| Custom agent | Per config | Per config | Domain-specific work |

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
| `xhigh` | ◉ | Most capability-sensitive work (Fable 5, Opus 4.8/4.7 only) |
| (omit) | — | Inherit session effort (default, most common) |

**Default: OMIT the `effort` field** — inherit the session's effort. Specify it only when the instruction clearly and unambiguously calls for a different depth (e.g. a trivial high-volume lookup). Do not set higher effort to chase quality — that is the session's decision. Effort values are model-relative (Fable 5 `medium` outperforms other models at any effort — see Model × Effort above); re-baseline pinned values when the model line changes.

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
- **claude-fable-5-compatibility.md**: Fable 5 deltas (brevity-first/removal-first authoring, reasoning-extraction refusal trap, proactivity boundaries, autonomy/checkpoint patterns, subagent bounds, progress-audit scaffold) + cross-model effort calculus, safeguard/refusal mechanics, Fable 5 migration audit checklist (steps 8–13), failure modes, research sources
- **claude-opus-4-8-compatibility.md**: Opus-tier guide — 4.8 deltas (effort recalibration, native honesty, tool triggering, dynamic workflows) + the literal-interpretation Core Rules rationale with before/after examples, "scaffolding to remove" table, 7-step migration audit checklist, common failure modes, research sources
- **cache-and-token-efficiency.md**: How instruction design interacts with CC's prompt cache — the (model, effort) cache key, the main-thread pin double cache-bust with cost math, the subagent-only rule for pinned skills, safe-pattern table, and other cache-relevant authoring decisions (skill body size, MCP deferral, CLAUDE.md mid-session edits)
- **yaml-frontmatter-complete-guide.md**: All valid fields and options (COMPREHENSIVE)
- **agent-vs-skill-decision-guide.md**: Complete decision matrix for agents vs skills
- **rules-and-content-placement-guide.md**: CLAUDE.md, rules, skills placement decisions
- **common-instruction-patterns.md**: Proven structures and templates
- **cross-platform-conversion-guide.md**: Claude Code → Claude.ai conversion
- **cc-to-codex-conversion-guide.md**: Claude Code → Codex skill conversion — mechanic map (AskUserQuestion / Skill tool / context: fork / cloud routines / effort / ToolSearch / mcp__ → Codex equivalents), T1/T2/T3 effort tiers, Tier-A pipeline vs Tier-B hand-authored decision, sensitive-data + harness-tool gates, Phase-1 assessment template (`templates/cc-to-codex-assessment-template.md`)
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
