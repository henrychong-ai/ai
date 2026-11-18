---
name: codex
description: "Routes requests to OpenAI GPT-6 (Astra/Sol/Luna) through the official Codex plugin for Claude Code — second opinions, hard problems, code review. Runs in the background by default via the Agent tool (main thread stays free; the harness notifies on completion); foreground on explicit request. Triggers on /codex, \"use codex\"; model-aware: astra (default) / sol / luna; reasoning levels: none/minimal/low/medium/high/xhigh (default medium)."
allowed-tools: Agent, Bash
---

# Codex Skill — OpenAI GPT-6 (Astra / Sol / Luna)

Second opinions, hard problems, and code review via Astra 6.2, Sol 6.2, or Luna. **Dispatch runs in the background via the Agent tool** — the main thread stays free while Codex thinks; the harness notifies on completion and Claude integrates the response then.

**Transport (since 2026-09-09):** the official **Codex plugin for Claude Code** (`codex@openai-codex`, marketplace `openai/codex-plugin-cc`). Its companion CLI talks to the Codex **app-server** runtime, a shared local daemon started on demand, which inherits `~/.codex/config.toml` and the existing ChatGPT login. This replaces the stdio MCP server (`codex mcp-server`, deprecated in Codex CLI 0.149.1 and dropped by this skill on 2026-09-09) — the tools `mcp__codex__codex` and `mcp__codex__codex-reply` no longer exist. Setup, upgrade, and troubleshooting: `references/codex-plugin-setup.md`.

## Quick Reference

Grammar: `/codex [model] [reasoning] [foreground]` — arguments in any order; all optional.

| Trigger | Model | Reasoning |
|---------|-------|-----------|
| `/codex` | astra | medium |
| `/codex [model]` | specified | medium |
| `/codex [level]` | astra | specified |
| `/codex high` | astra | high |
| `/codex sol xhigh` | sol | xhigh |
| `/codex luna low` | luna | low |

**Models** (tier names resolve to these explicit IDs, updated 2026-11-18):

| Arg | Model ID | Use for (illustrative — not required outputs) |
|-----|----------|-----------------------------------------------|
| `astra` *(default)* | `gpt-6.2-astra` | Complex reasoning, second opinions, and code review; pass the workflow's explicit effort |
| `sol` | `gpt-6.2-sol` | Coding and everyday work; the capacity fallback for Astra uses `xhigh` |
| `luna` | `gpt-6-luna` | High-volume or simple checks |

Terra (`gpt-6.1-terra`) remains available for visual and everyday work through native Codex routes. This skill's named argument grammar remains `astra` / `sol` / `luna`.

`spark` is a plugin alias for `gpt-5.3-codex-spark`, an ultra-fast coding model outside this skill's grammar; pass it explicitly as `--model spark` when a call genuinely wants it.

**Reasoning:** `none` → `minimal` → `low` → `medium` → `high` → `xhigh`, defaulting to `medium` under this workflow's policy. These six are the full set the **companion** accepts — the model catalogue also lists `max` (and `ultra` on Astra and Sol), but the companion rejects both with `Unsupported reasoning effort`, so route work needing them to the Codex Desktop app or the native CLI. The installed 6.2 catalogue supports `low` / `medium` / `high` / `xhigh` / `max` / `ultra`; select an effort supported by both the model and the companion. Omitting `--effort` falls back to `model_reasoning_effort` in `~/.codex/config.toml`.

**Service tier is config-global.** The companion has no per-call tier flag. Use the configured standard tier and consult the installed catalogue for current tier availability and usage costs.

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

Call the companion through a wrapper script you create once (these docs use `~/scripts/codex-companion`; substitute your own path), which resolves the version-volatile plugin root for you:

```bash
~/scripts/codex-companion task --model gpt-6.2-astra --effort medium --cwd "$PWD" "prepared prompt"
```

The wrapper body, and the inline alternative without one, are in `references/codex-plugin-setup.md` → Plugin Root Resolution.

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
  subagent_type: "codex-relay",   // dedicated leaf relay agent; its frontmatter pins model: sonnet + effort: low. The Agent tool has no per-call effort param, so effort is pinned in the agent definition (install claude-code/agents/codex-relay.md from this repo to ~/.claude/agents/). Verbatim relay at Sonnet cost; use a named agent rather than a fork, which pins the parent model. A newly created agent registers at session start.
  run_in_background: true,
  // Relay behaviour (verbatim pass-through, single Bash call, leaf-only) lives in the
  // agent's own system prompt — the task prompt carries only the call parameters:
  prompt: "Run the Codex companion once with:\n\n--model gpt-6.2-astra        // default; gpt-6.2-sol | gpt-6-luna when the user names sol/luna\n--effort medium            // default; none/minimal/low/medium/high/xhigh\n--cwd [working dir]\n[--write]                  // only when Codex must modify or run something; omit for read-only review and reasoning\n[--resume-last]            // only for a follow-up on the previous thread\n\nPrompt:\n[prepared prompt]"
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
