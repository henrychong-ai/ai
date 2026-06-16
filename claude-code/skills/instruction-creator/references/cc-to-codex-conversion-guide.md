# Claude Code → Codex Skill Conversion Guide

Convert a Claude Code (CC) skill into a Codex skill: the mechanic map, the T1/T2/T3 effort tiers, the Tier-A/Tier-B distribution decision, and the two orthogonal gates (sensitive-data, harness-tool availability).

> **Companion guide:** `cross-platform-conversion-guide.md` covers CC → **Claude.ai** (Desktop/iOS/Android/web — a sandboxed, tool-less ecosystem). This guide covers CC → **Codex** (a *different filesystem+shell harness* with its own mechanics). Different target, different rules — don't cross them.
>
> **Methodology vs machinery.** This file is the **methodology** (decide *what* a skill becomes). The executable **machinery** is your own Codex deploy pipeline + allowlist. Author here, ship there.

---

## Overview

### Two runtimes, one SKILL.md format

```
┌──────────────────────────────┐        ┌──────────────────────────────┐
│        CLAUDE CODE           │        │           CODEX              │
│   ~/.claude/skills/<name>/   │        │   ~/.codex/skills/<name>/    │
│                              │        │                              │
│ • Skill tool / /name invoke  │  ───►  │ • SKILL.md read as a skill   │
│ • AskUserQuestion gates      │        │ • on-request approval prompt │
│ • subagents / context: fork  │        │ • single agent (no fork)     │
│ • Workflow / Agent fan-out   │        │ • Automations for scheduled  │
│ • mcp__* tool tokens         │        │ • MCP via config.toml        │
│ • /effort, ToolSearch        │        │ • reasoning_effort (harness) │
└──────────────────────────────┘        └──────────────────────────────┘
         CC-mechanic surface                  Codex-mechanic surface
                         └──── CONVERSION GAP ────┘
```

**What's the same:** Codex 0.139+ reads the **same `SKILL.md` markdown+frontmatter format**. Knowledge, process, reference data, templates, and deterministic scripts port directly.

**What's different:** every CC *harness mechanic* (the Skill tool, AskUserQuestion, subagents, `context: fork`, `mcp__*` tokens, `/effort`, ToolSearch, plan mode, scheduled cloud routines) has no literal Codex equivalent — it must be **mapped, generalised, or re-architected**. The mechanic map below is the core of the conversion.

**Canonical skill dir:** `~/.codex/skills/` (global skills); repo-scoped skills go in `<project>/.agents/skills/`.

---

## Step 1 — Effort tier (how much work to convert)

| Tier | Name | Condition | Distribution | Examples |
|:---:|---|---|---|---|
| **T1** | **Reformat** | Clean framework; only CC-mechanic *phrasing* to strip. Knowledge/process/reference skills. | **Tier-A pipeline** if zero behavioural CC tokens survive a strip+transform; else Tier-B. | cloud/infra knowledge, domain manuals, methodology skills |
| **T2** | **Convert** | Has CC-*interactive* mechanics (AskUserQuestion decision flows, interactive document generation) → rewrite as a parameterised, non-interactive process. | **Tier-B** (hand-authored) | legal/document-generation skills, incident-report skills |
| **T3** | **Re-architect** | A **load-bearing CC-only mechanism** (scheduled cloud routines, multi-agent `Workflow`, subagent fan-out) is the skill's spine → rebuild on a Codex equivalent (usually a **Codex Automation**). | **Tier-B** (hand-authored) | a scheduled-scan skill (cloud routine → Codex Automation) |

**Decision question:** *"What in this skill only works because of a Claude Code harness feature?"* — nothing structural → T1; an interactive prompt loop → T2; a whole orchestration/scheduling mechanism → T3.

---

## Step 2 — Two orthogonal gates (overlay on any tier)

A skill can be T1 **and** 🔒 **and** 🔌 at once — these are independent of the effort tier.

### 🔒 Sensitive / regulated-data gate (HARD)

Client/member or otherwise regulated PII (identity, financial, account data) must live in the **system of record only** — never in skill text. Before converting a data-bearing skill: **extract at source** (the data stays in the platform; the skill keeps *process + pointers*). Any sensitive data found in the source skill is a pre-existing policy violation to fix regardless of the conversion. **BLOCKING** for any client-facing / regulated-data skill.

> **Scope:** this gate is **sensitive/regulated data only**. Keep internal-sensitive figures (e.g. staff compensation) in their system of record (e.g. an HR platform); the skill carries process, not values. An author's own non-regulated data in a private skill is their call.

### 🔌 Harness-tool availability

A skill only *functions* in Codex where its tool/data source exists. Add a **dependency note** to the converted skill; if the dependency is absent, ship it as **knowledge-only**.

| Dependency in CC | Available in Codex? | Note to add |
|---|---|---|
| MCP server (your configured servers — e.g. knowledge-graph, calendar, automation, docker) | ✅ if in `~/.codex/config.toml` `[mcp_servers]` | "Requires the `<name>` MCP server" |
| Plugin (gmail, slack, github, google-drive, zoom, browser, computer-use, documents, spreadsheets, presentations) | ✅ Codex plugins | "Requires the `<name>` plugin" |
| Local desktop app (calendar app, task manager) | ✅ local sessions only | "Local-only — cannot run on headless hosts" |
| Local data store / vault / local script | ⚠️ only where the path/data exists | State the path dependency explicitly |

---

## Step 3 — The mechanic map (CC → Codex)

The spine of the conversion. Every behavioural CC mechanic resolves to one of: **MAP** (a Codex equivalent), **GENERALISE** (plain language), or **RE-ARCHITECT** (rebuild).

| CC mechanic | Disposition | Codex equivalent |
|---|---|---|
| `AskUserQuestion` (4-option gate) | MAP | In-line approval prompt + **WAIT** (`approval_policy = on-request`). The structured 4-option UI → a plain numbered question in prose. **Headless** (`codex exec`/Automation): no one to ask → write a report of intended actions; never act destructively. |
| Skill tool / `/name` invocation | MAP | Codex reads `~/.codex/skills/<name>/SKILL.md` (same format). "Load `/other`" → "read the `<other>` skill". |
| `context: fork` + `agent:` (isolated subagent) | GENERALISE / RE-ARCHITECT | No Codex subagent fork. Run the work **inline**; if it's heavy/parallel and load-bearing → a Codex **Automation** or separate `codex exec` (T3). |
| `Agent`/`Task` tool, `Workflow` (dynamic multi-agent fan-out) | RE-ARCHITECT | Codex is single-agent → **sequential steps**, or an **Automation** per work item. Load-bearing parallelism = T3. |
| Scheduled cloud routines / scheduled CC tasks | RE-ARCHITECT | **Codex app Automations** (canonical scheduled runtime; in-app run tracking). `codex exec` via cron/launchd for headless/CI only. |
| `/effort` flag + `effort:` frontmatter | MAP (drop key) | Codex `reasoning_effort` (config.toml `model_reasoning_effort` / per-session) — **harness-level, not a per-skill field**. The frontmatter key is stripped (Codex ignores it). |
| `ToolSearch` / deferred MCP tools | GENERALISE | Codex loads MCP tools via config.toml `enabled_tools` (no runtime tool search). Drop the `ToolSearch` call; assume the tool is configured, or flag the dependency. |
| `mcp__X__tool` tokens | GENERALISE → forces Tier-B | The grep guard **rejects all `mcp__` tokens**. A retained MCP call must be rephrased to natural language ("search the knowledge graph", "query the calendar") — which is why MCP-dependent skills are almost always **Tier-B hand-authored** (where the Codex tool is used naturally). |
| `Read`/`Write`/`Edit`/`Grep`/`Glob`/`Bash` tool-name references | GENERALISE | Codex has filesystem + shell. Generalise tool-name invocations to plain verbs: "read the file", "run the command", "search for". |
| `EnterPlanMode` / `ExitPlanMode` / plan mode | GENERALISE | No plan-mode tool → "outline the plan, confirm, then execute". |
| `SlashCommand` (invoke another command) | MAP | Read the target skill/command file instead. |
| `SendUserFile`, `ScheduleWakeup`, `TaskCreate`, harness task tools | GENERALISE / RE-ARCHITECT | No equivalent → describe the output path / fold into an Automation. |

---

## Step 4 — Frontmatter transformation

The pipeline strips CC-only frontmatter keys (Codex ignores unknown keys, but they imply CC behaviour and must go):

**Stripped:** `allowed-tools`, `context`, `agent`, `effort`, `model`, `user-invocable`, `disable-model-invocation`, `hooks`.

**Kept:** `name`, `description` (the universal pair).

A provenance banner is injected after the closing `---` on pipeline-deployed copies (`<!-- DEPLOYED COPY — generated ... Do NOT edit here -->`) so generated copies are never hand-edited.

---

## Step 5 — Distribution decision: Tier-A (pipeline) vs Tier-B (hand-authored)

Orthogonal to effort tier, but correlated. **The grep guard is the automatic backstop that forces the right call.**

```
Does any behavioural CC token (mcp__, AskUserQuestion, Agent tool,
context: fork, subagent, SlashCommand, EnterPlanMode) survive a
frontmatter-strip + addressee-transform?
        │
   No ──┴── Yes
   │          │
Tier-A      Tier-B (hand-author in ~/.codex/skills/<name>)
allowlist
```

### Tier-A — pipeline

Opt-in **allowlist** (`name:mode`). Mechanics: staging copy (symlink-resolving) → strip CC frontmatter keys → inject provenance banner → optional **`transform`** mode (`Claude Code`→`the agent harness`, `Claude`→`the agent` across all `.md`) → **grep guard** (fails loudly on behavioural CC tokens) → deploy with delete. A `--check` mode is the drift/orphan gate. **Use only when verbatim- or transform-clean.** Deployed copies are **generated** — never hand-edit; edit the CC source and regenerate.

- `verbatim` — copy as-is (frontmatter normalised + banner only). Use when there are zero addressee tokens.
- `transform` — additionally apply the addressee sed map. Use when "Claude"/"Claude Code" appear as generic addressee (NOT where they're factual product references — a blind transform would corrupt those; defer to Tier-B or verbatim with a manual scan).

### Tier-B — hand-authored Codex-native

For skills that are CC-shaped (approval/orchestration mechanics the guard rejects), MCP-dependent, or have no clean CC source. Author **directly** in `~/.codex/skills/<name>/` (NOT pipeline-managed; not allowlisted). Maintain a trimmed, Codex-approval-flow version directly; sync only harness-neutral data and engines from the CC source.

**Tier-B authoring checklist:**
- [ ] SKILL.md frontmatter = `name` + `description` only.
- [ ] Every mechanic from Step 3 mapped/generalised/re-architected (no surviving CC tokens — run the guard pattern as a self-check).
- [ ] MCP/plugin/local-app dependencies stated as notes (🔌).
- [ ] Approval gates phrased for `on-request` + a headless-fallback ("write a report, don't act") where the skill may run under `codex exec`/Automation.
- [ ] Sensitive-data gate (🔒) satisfied — process + pointers, no PII.
- [ ] Self-paths use `~/.codex/...`, not legacy CC paths.

---

## Step 6 — Worked examples

**T2 (convert interactive → process) — a legal-document-generation skill:** the CC skill uses `AskUserQuestion` to pick jurisdiction/template interactively. Codex version: a **parameterised process** — "determine jurisdiction and template from the request (ask in-line only if ambiguous), then generate". The decision tree stays; the harness UI goes.

**T3 (re-architect scheduled/multi-agent → Automation):** a CC skill that provisions a weekly scan via a scheduled cloud routine. The provisioning is not portable. Codex version: a **Codex Automation** (the canonical scheduled runtime) running the scan steps, writing its report to a **shared store** (knowledge graph / docs) so every harness sees results, and registered in your automation runbook. The *playbook* (what to scan, how to read results) always ports as knowledge; the *automation* is the T3 work.

---

## Step 7 — Verification (before deploy/commit)

| Check | How |
|---|---|
| **No surviving CC mechanics** | grep guard: `grep -rnE 'mcp__\|AskUserQuestion\|Agent tool\|context: fork\|subagent\|SlashCommand\|EnterPlanMode'` (pipeline runs this automatically; run manually for Tier-B). |
| **Sensitive-data re-scan (🔒 BLOCKING)** | For data-bearing skills: confirm no PII/regulated data in any file. |
| **Harness-dep note present (🔌)** | Each MCP/plugin/local-app dependency is stated. |
| **Self-paths corrected** | `~/.codex/...` not legacy CC paths. |
| **Drift/orphan** | The pipeline's `--check` mode (Tier-A). |
| **Count reconciliation** | Allowlist count = deployed banner-marked dir count. |

---

## Phase-1 assessment workflow (for a batch reformat)

For a multi-skill reformat, run a **read-only assessment first**: read each skill and record one row per the evidence-table template. No pre-exclusion — assign the tier and gates from evidence, then build in waves.

**Template:** `templates/cc-to-codex-assessment-template.md` — columns: skill · effort-tier (T1/T2/T3) · distribution (Tier-A/B) · 🔒 sensitive-data verdict · 🔌 harness-deps · what-survives · disposition.

---

## Appendix — conversion checklist

- [ ] Effort tier assigned (T1/T2/T3) with the "what only works because of CC?" question.
- [ ] 🔒 sensitive-data gate checked (extract-at-source if data-bearing).
- [ ] 🔌 harness-tool dependencies noted (MCP/plugin/local-app/path).
- [ ] Every Step-3 mechanic mapped/generalised/re-architected.
- [ ] Frontmatter reduced to `name` + `description`.
- [ ] Tier-A (verbatim/transform-clean) vs Tier-B (hand-author) decided; grep guard passes.
- [ ] Verification table green; drift `--check` clean.
- [ ] Allowlist entry added (Tier-A) or `~/.codex/skills/<name>` authored (Tier-B); manifest + provenance map updated.

---

*Home: `/instruction-creator` references. Machinery: your Codex distribution tooling (deploy pipeline + allowlist). Codex harness reference: the Codex CLI/config docs.*
*Last updated: 2026-06-16.*
