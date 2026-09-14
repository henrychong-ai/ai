---
name: codex
description: "Routes requests to OpenAI GPT-6 Astra and the GPT-5.6 family (Sol/Terra/Luna) through the official Codex plugin for Claude Code — second opinions, hard problems, code review. Runs in the background by default via the Agent tool (main thread stays free; the harness notifies on completion); foreground on explicit request. Triggers on /codex, \"use codex\"; model-aware: astra (default) / sol / terra / luna; reasoning levels: none/minimal/low/medium/high/xhigh (default medium)."
allowed-tools: Agent, Bash
---

# Codex Skill — OpenAI GPT-6 Astra + GPT-5.6 (Sol / Terra / Luna)

Second opinions, hard problems, and code review via GPT-6 Astra or GPT-5.6. **Dispatch runs in the background via the Agent tool** — the main thread stays free while Codex thinks; the harness notifies on completion and Claude integrates the response then.

**Transport (since 2026-09-09):** the official **Codex plugin for Claude Code** (`codex@openai-codex`, marketplace `openai/codex-plugin-cc`). Its companion CLI talks to the Codex **app-server** runtime, a shared local daemon started on demand, which inherits `~/.codex/config.toml` and the existing ChatGPT login. This replaces the stdio MCP server (`codex mcp-server`, deprecated in Codex CLI 0.149.1 and removed from this setup on 2026-09-09) — the tools `mcp__codex__codex` and `mcp__codex__codex-reply` no longer exist. Setup, upgrade, and troubleshooting: `references/codex-plugin-setup.md`.

## Quick Reference

Grammar: `/codex [model] [reasoning] [foreground]` — arguments in any order; all optional.

| Trigger | Model | Reasoning |
|---------|-------|-----------|
| `/codex` | astra | medium |
| `/codex [model]` | specified | medium |
| `/codex [level]` | astra | specified |
| `/codex high` | astra | high |
| `/codex sol xhigh` | sol | xhigh |
| `/codex terra high` | terra | high |
| `/codex luna low` | luna | low |

**Models** (tier names are durable; the generation number advances on its own cadence — GPT-6 Astra sits above the still-available GPT-5.6 family):

| Arg | Model ID | Use for (illustrative — not required outputs) |
|-----|----------|-----------------------------------------------|
| `astra` *(default)* | `gpt-6-astra` | Frontier flagship (released 2026-09-03), succeeding Sol — the catalogue's "most capable model for complex, demanding work". Strongest agentic execution, roughly 1.9x faster task completion than Sol on Mind2Web, shorter and less verbose reasoning, stronger long-context retrieval. Catalogue default effort `medium`. $10 in / $50 out per million tokens, against Sol's $5 / $30. On ChatGPT Pro, Business, and Enterprise plus the API. Source: [DataCamp GPT-6 Astra overview](https://www.datacamp.com/blog/gpt-6-astra) |
| `sol` | `gpt-5.6-sol` | Previous flagship — deep reasoning at half Astra's price |
| `terra` | `gpt-5.6-terra` | Balanced everyday work (≈GPT-5.5 quality, ~half Sol's cost) |
| `luna` | `gpt-5.6-luna` | Fastest/cheapest — high-volume or simple checks |

`spark` is a plugin alias for `gpt-5.3-codex-spark`, an ultra-fast coding model outside this skill's grammar; pass it explicitly as `--model spark` when a call genuinely wants it.

**Reasoning:** `none` → `minimal` → `low` → `medium` → `high` → `xhigh`, defaulting to `medium` (Astra's own catalogue default). These six are the full set the **companion** accepts — the model catalogue also lists `max` (and `ultra` on Astra, Sol, and Terra), but the companion rejects both with `Unsupported reasoning effort`, so route work needing them to the Codex Desktop app or the native CLI. Omitting `--effort` falls back to `model_reasoning_effort` in `~/.codex/config.toml`.

**Service tier is config-global.** There is no per-call flag: the tier comes from `service_tier` in `~/.codex/config.toml` (`"default"` for standard processing, `"fast"` for priority routing — on ChatGPT-plan auth Fast is ~1.5x speed at **2.5x plan usage** for GPT-5.6, not free). A user asking for `fast` or `standard` per call gets the configured tier — say so, and point at config.toml as the place to change it.

Extract model tier and reasoning level from user input in any order; any dimension the user omits takes its default (astra / medium).

## Plugin Commands

The plugin ships slash commands of its own. Prefer them where they fit; use `/codex` for arbitrary prompts and second opinions with an explicit model and effort.

| Command | Use for |
|---------|---------|
| `/codex:review` | Codex's native review of local git state (working tree or branch) — no custom focus text |
| `/codex:adversarial-review` | Challenge review of local git state; accepts focus text |
| `/codex:rescue` | Hand a stuck task to the plugin's write-capable rescue agent |
| `/codex:status`, `/codex:result`, `/codex:cancel` | Manage background plugin jobs |
| `/codex:setup` | Readiness check; also toggles the optional stop-time review gate |
| `/codex:transfer` | Hand the current Claude session's context to Codex |

## Companion CLI Reference

Call the companion through the wrapper on PATH (for example `~/scripts/codex-companion`), which resolves the version-volatile plugin root for you:

```bash
~/scripts/codex-companion task --model gpt-6-astra --effort medium --cwd "$PWD" "prepared prompt"
```

Without the wrapper, resolve the plugin root inline instead — see `references/codex-plugin-setup.md`.

| Subcommand | Flags | Notes |
|------------|-------|-------|
| `task` | `[--background] [--write] [--resume-last\|--resume\|--fresh] [--model <id>] [-m <id>] [--effort <level>] [--cwd <dir>] [--prompt-file <file>] [--json] [prompt]` | The general query / second-opinion path. Sandbox defaults to **read-only** and approval policy to **never**, so it is safe in a background subagent. `--write` switches to a workspace-write sandbox. Without `--background` it runs in the foreground, printing `[codex] …` progress lines then the final assistant message. |
| `review` | `[--wait\|--background] [--base <ref>] [--scope auto\|working-tree\|branch]` | Codex's native diff review |
| `adversarial-review` | same as `review`, plus trailing focus text | Challenge review |
| `status` | `[job-id] [--wait] [--timeout-ms <ms>] [--all] [--json]` | Background job state |
| `result` / `cancel` | `[job-id] [--json]` | Fetch or stop a background job |
| `setup` | `[--json] [--enable-review-gate\|--disable-review-gate]` | Readiness probe; makes no model call |
| `task-resume-candidate` | `--json` | Names the thread `--resume-last` would continue |
| `transfer` | `[--source <claude-jsonl>] [--json]` | Session handoff to Codex |

**Flag hygiene:** the parser treats an unrecognised flag as prompt text rather than erroring, so a stray `--wait` on `task` silently lands inside the prompt Codex reads. Pass `task` only the flags in the table above. Model strings pass through verbatim (the sole alias is `spark`), so a typo reaches the API as a model name.

**Long prompts:** write the prompt to a file under `$TMPDIR` and pass `--prompt-file <file>` instead of inlining it as an argument.

**Health:** `~/scripts/codex-companion setup --json` returns `ready`, `codex.available`, `auth.loggedIn`, and `sessionRuntime` without a model call. `ready: false` or `auth.loggedIn: false` means Codex is degraded — report it and suggest `/codex:setup`, and keep going without Codex.

**Usage and rate limits:** `references/codex-rate-limits.md`.

## Context Preparation

Curate context before calling — quality in = quality out:
1. Extract the relevant code snippets rather than whole files
2. Include full error traces when debugging
3. State what has been tried
4. Define what "solved" looks like
5. Mention constraints (performance, security, compatibility)

**Anti-patterns:** dumping entire files • vague questions • missing tech context • no success criteria.

## Execution: Background Dispatch (DEFAULT)

**Every `/codex` invocation runs in the background by default.** Dispatch the companion call through the `Agent` tool with `run_in_background: true`; the main thread runs no synchronous Codex call, which would block until Codex returns.

**Foreground override (explicit request only):** run the companion command directly on the main thread when the user asks for it (`/codex foreground …`, "run codex in the foreground", "wait for codex").

After dispatch, reply with one short line (e.g. `Codex query dispatched; will surface the response when ready`) and continue with other work. When the harness fires the completion notification, integrate the output per **Response Integration**.

### Dispatch Pattern

```
Agent({
  description: "Codex: [3-5 word topic]",
  subagent_type: "codex-relay",   // dedicated leaf relay agent; its frontmatter pins model: sonnet + effort: medium. The Agent tool has no per-call effort param, so effort is pinned in the agent definition (~/.claude/agents/codex-relay.md). Verbatim relay at Sonnet cost; use a named agent rather than a fork, which pins the parent model. A newly created agent registers at session start.
  run_in_background: true,
  // Relay behaviour (verbatim pass-through, single Bash call, leaf-only) lives in the
  // agent's own system prompt — the task prompt carries only the call parameters:
  prompt: "Run the Codex companion once with:\n\n--model gpt-6-astra        // default; gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna when the user names sol/terra/luna\n--effort medium            // default; none/minimal/low/medium/high/xhigh\n--cwd [working dir]\n[--write]                  // only when Codex must modify or run something; omit for read-only review and reasoning\n[--resume-last]            // only for a follow-up on the previous thread\n\nPrompt:\n[prepared prompt]"
})
```

`--background` stays out of the relay's command: the Agent dispatch already provides the backgrounding, and adding it would leave a tracked job for the relay to poll.

### Continue an Existing Thread

For follow-ups, dispatch the same way and add `--resume-last`, which continues the most recent Codex task thread for that workspace. This replaces the old thread-ID follow-up call. `task-resume-candidate --json` names the thread that would be resumed; `--fresh` forces a new one.

### Parallel Queries

Issue multiple background `Agent` calls in a single message — one per branch (e.g. approach A vs approach B). Each fires its own completion notification; integrate them as they return.

## Response Integration

Triggered when the background Agent's completion notification fires. Integrate with main-thread context rather than passing the text through.

| Pattern | When | Action |
|---------|------|--------|
| **Implement** | Working code returned | Verify fit → adapt style → implement → test |
| **Synthesise** | Second opinion | Both perspectives → agreements and differences → recommendation |
| **Iterate** | Needs refinement | Dispatch a fresh background Agent with `--resume-last` |
| **Conflict** | Disagreement | Both approaches → trade-offs → recommend with rationale |
