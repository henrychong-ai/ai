---
name: codex
description: "Routes requests to OpenAI GPT-5.6 (Sol/Terra/Luna) via Codex MCP for second opinions, hard problems, and code review. Runs in background by default via Agent tool (main thread stays free; harness notifies on completion); foreground only on explicit request. Triggers on /codex, \"use codex\"; model-aware: sol (default) / terra / luna; reasoning levels: none/low/medium/high/xhigh (default xhigh)/max/ultra; service tiers: fast/standard."
allowed-tools: Agent, mcp__codex__codex, mcp__codex__codex-reply
---

# Codex Skill — OpenAI GPT-5.6 (Sol / Terra / Luna)

Second opinions, hard problems, code review via GPT-5.6. **Dispatch runs in the background via the Agent tool** — the main thread stays free while Codex thinks; the harness notifies on completion and Claude integrates the response then.

**Model-aware (since 2026-07-13):** `/codex` accepts a model tier — **`sol`** (`gpt-5.6-sol`, flagship, **default**), **`terra`** (`gpt-5.6-terra`, balanced), **`luna`** (`gpt-5.6-luna`, fastest/cheapest) — alongside reasoning level and service tier, in any order (e.g. `/codex luna xhigh`, `/codex sol xhigh fast`, `/codex terra high standard`).

## Quick Reference

Grammar: `/codex [model] [reasoning] [tier] [foreground]` — arguments in any order; all optional.

| Trigger | Model | Reasoning | Service Tier |
|---------|-------|-----------|--------------|
| `/codex` | sol | xhigh | fast (default) |
| `/codex [model]` | specified | xhigh | fast |
| `/codex [level]` | sol | specified | fast |
| `/codex luna xhigh` | luna | xhigh | fast |
| `/codex sol xhigh fast` | sol | xhigh | fast |
| `/codex terra high standard` | terra | high | standard |

**Models** (GPT-5.6 family — tier names are durable; the generation number advances on its own cadence):

| Arg | Model ID | Use for (illustrative — not required outputs) |
|-----|----------|-----------------------------------------------|
| `sol` *(default)* | `gpt-5.6-sol` | Flagship deep reasoning — hardest problems, cross-model second opinions, code review |
| `terra` | `gpt-5.6-terra` | Balanced everyday work (≈GPT-5.5 quality, ~half Sol's cost) |
| `luna` | `gpt-5.6-luna` | Fastest/cheapest — high-volume or simple checks |

**Reasoning:** `none` → `low` → `medium` → `high` → `xhigh` (default) → `max` → `ultra` — both opt-in. `max` = deepest single-agent reasoning (settings-enabled, costly). `ultra` = `max` + Codex cooperative subagents (automatic task delegation; subagents inherit the parent model + effort → highest cost). ⚠️ `ultra` is reliably available only via the Codex Desktop app / native CLI; over this skill's MCP/websocket path it is best-effort and may downgrade to `max` (cc-switch #5209).
**Tiers:** `fast` (default) • `standard`/`normal` (opt-in) — see the service-tier note under *MANDATORY: Always Pass Config Block*.

Arguments appear in any order. Extract model tier + reasoning level + service tier from user input; any dimension the user omits takes its default (sol / xhigh / fast). Codex "ultra" auto-delegation mode is deliberately not exposed — it spawns sub-agents, conflicting with the leaf-relay background dispatch.

## Context Preparation

Curate context before calling — quality in = quality out:
1. Extract relevant code snippets (not entire files)
2. Include full error traces if debugging
3. State what's been tried
4. Define what "solved" looks like
5. Mention constraints (performance, security, compatibility)

**Anti-patterns:** Dumping entire files • Vague questions • Missing tech context • No success criteria

## Execution: Background Dispatch (DEFAULT)

**Every `/codex` invocation runs in the background by default.** Dispatch the Codex MCP call via the `Agent` tool with `run_in_background: true`. The main thread does **not** call `mcp__codex__codex` synchronously — that would block until Codex returns.

**Foreground override (explicit request only):** Run synchronously — calling `mcp__codex__codex` directly on the main thread — only when the user explicitly asks for it (e.g. `/codex foreground …`, "run codex in the foreground", "wait for codex"). Absent an explicit foreground request, always dispatch in the background.

After dispatch, reply to the user with one short line (e.g. `Codex query dispatched; will surface response when ready`) and continue with other work. When the harness fires the background-completion notification, surface and integrate the Codex output per the **Response Integration** section below.

### Dispatch Pattern

```
Agent({
  description: "Codex: [3-5 word topic]",
  subagent_type: "general-purpose",
  model: "sonnet",           // thin pass-through relay — pin to Sonnet; never inherit the (possibly Opus) session model. Reliable verbatim relay without the Opus cost; do NOT use a fork (fork pins the parent model + can't downgrade)
  run_in_background: true,
  prompt: "You are a mechanical relay — do NOT analyse, plan, reason about, or add commentary to the task. Call mcp__codex__codex exactly once with the parameters below, then return Codex's full response verbatim — no summarisation, no truncation, no commentary.\n\nprompt: [prepared prompt]\ncwd: [working dir]\nsandbox: \"read-only\"        // default (non-mutating); escalate to workspace-write ONLY for write/run tasks; never danger-full-access\napproval-policy: \"never\"    // MANDATORY in background — no interactive approver exists in a subagent, so any approval gate = silent hang\nconfig: { model: [gpt-5.6-sol (default) | gpt-5.6-terra | gpt-5.6-luna], model_reasoning_effort: [xhigh (default) | none/low/medium/high/max/ultra], service_tier: [fast (default) | standard] }"
})
```

### Continue an Existing Thread

For follow-ups, dispatch the same way but instruct the background agent to call `mcp__codex__codex-reply` with the `threadId` from the prior response plus the new `prompt`.

### Parallel Queries

Spawn multiple background `Agent` calls in a single message — one per branch (e.g. approach A vs approach B). Each fires its own completion notification; integrate as they return.

## MCP Tool Schema

### `mcp__codex__codex`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `prompt` | string | **Yes** | Initial user prompt |
| `model` | string | No | Top-level override (also in config — use config for consistency) |
| `config` | object | No | config.toml overrides (`additionalProperties: true`) |
| `cwd` | string | No | Working directory |
| `sandbox` | enum | No | `read-only` / `workspace-write` / `danger-full-access` |
| `approval-policy` | enum | No | `untrusted` / `on-failure` / `on-request` / `never` |
| `profile` | string | No | Config profile from config.toml |
| `base-instructions` | string | No | Replace default instructions |
| `developer-instructions` | string | No | Injected as developer role message |
| `compact-prompt` | string | No | Prompt used when compacting the conversation |

### `mcp__codex__codex-reply`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `prompt` | string | **Yes** | Follow-up prompt |
| `threadId` | string | Yes (effectively) | Thread ID from previous response |
| ~~`conversationId`~~ | — | — | **DEPRECATED** — use `threadId` |

**Checking usage / rate limits:** the MCP can't report quota — see `references/codex-rate-limits.md`.

## MCP Syntax (Reference for the Background Agent)

The patterns below describe how the spawned background agent calls `mcp__codex__codex`. The `/codex` skill itself never calls these MCP tools from the main thread — it only spawns the wrapper Agent.

### MANDATORY: Always Pass Config Block

Every call MUST include `config` with `model`, `model_reasoning_effort`, and `service_tier`, AND explicitly set the top-level `sandbox` and `approval-policy` params. Never rely on config.toml defaults.

**Non-blocking approval is MANDATORY for background dispatch.** A background Agent/subagent has **no interactive approver**, so any approval-gated codex action blocks the MCP call indefinitely — the silent, no-error "hang" (the call never returns, no completion notification). Codex reasons fine, then freezes the moment it tries to act. Always pass:
- `approval-policy: "never"` — codex never pauses for an approval that cannot be granted in a background context.
- `sandbox: "read-only"` (**default**) — safe to never-approve because nothing can mutate. Correct for the common case (second opinion / review / reasoning, which only reads).
- Escalate to `sandbox: "workspace-write"` ONLY when codex must write or run; keep `approval-policy: "never"` (or `on-failure`) so it still never blocks — bounded to the workspace. **Never pair `approval-policy: "never"` with `danger-full-access`** — non-blocking approval is safe only because the sandbox bounds what can happen, so never combine it with an unbounded sandbox.

(Detection/recovery for a residual hang — e.g. transport stall or rate-limit — remains: `stat` the background agent's `.output` for a tiny + stale signature, never Read the JSONL; then stop and re-dispatch.)

**Defaults:** `gpt-5.6-sol` + `xhigh` + `fast`. Do not downgrade reasoning or switch model tier without explicit user request.

**Service tier — `fast` is the CONFIG value; Codex maps it internally to the `priority` request tier.** Write `service_tier: "fast"` (the config-layer name), never `"priority"` as a config value; use `"standard"`/`"default"` for normal speed. ⚠️ Over the MCP/websocket path this skill uses, `service_tier: "fast"` has been reported ineffective in some cases (openai/codex #14204 — closed; OpenAI states Fast is server-routed, so an observed `default` is inconclusive). `features.fast_mode` is a client-side feature gate (on by default), not a model capability flag. Treat `fast` as best-effort: worst case is standard speed, no error.

> **Parameter Placement:**
> - `model_reasoning_effort` and `service_tier` are **NOT** top-level params — **only work inside `config`**
> - `model` exists at top level AND in config — **always use `config`** for consistency
> - Top-level `model_reasoning_effort` or `service_tier` will **silently fail**

### Correct Syntax
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  cwd: "[working dir]",                    // pass explicitly so codex isn't operating in an unexpected dir
  sandbox: "read-only",                   // default; workspace-write only for write/run tasks; never danger-full-access + never
  "approval-policy": "never",             // MANDATORY in background — no approver exists, so any gate = silent hang
  config: {
    "model": "gpt-5.6-sol",               // default tier; gpt-5.6-terra | gpt-5.6-luna when the user names terra/luna
    "model_reasoning_effort": "xhigh",     // default; or user-specified: none/low/medium/high/max/ultra
    "service_tier": "fast"                 // config value "fast" → Codex maps to the "priority" request tier; "standard"/"default" opt-in
  }
})
```

### Continue Conversation
```
mcp__codex__codex-reply({
  threadId: "[from previous response]",
  prompt: "[follow-up]"
})
```

### Parallel Queries
```
mcp__codex__codex({
  prompt: "Analyze approach A...",
  config: { "model": "gpt-5.6-sol", "model_reasoning_effort": "xhigh", "service_tier": "fast" }
})
mcp__codex__codex({
  prompt: "Analyze approach B...",
  config: { "model": "gpt-5.6-sol", "model_reasoning_effort": "xhigh", "service_tier": "fast" }
})
```

### Common Mistakes

**❌ Config values at top level**
```
mcp__codex__codex({
  prompt: "...",
  model_reasoning_effort: "xhigh",   // ❌ NOT top-level — silently ignored
  service_tier: "fast"               // ❌ NOT top-level — silently ignored
})
```

**❌ Missing config block**
```
mcp__codex__codex({
  prompt: "...",
  model: "gpt-5.6-sol"              // ❌ Only sets model, loses reasoning + tier
})
```

**❌ Deprecated conversationId**
```
mcp__codex__codex-reply({
  conversationId: "...",             // ❌ Use threadId instead
  prompt: "..."
})
```

## Response Integration

Triggered when the background Agent's completion notification fires. Don't pass through — INTEGRATE with main thread context.

| Pattern | When | Action |
|---------|------|--------|
| **Implement** | Working code returned | Verify fit → Adapt style → Implement → Test |
| **Synthesise** | Second opinion | Both perspectives → Agreements/differences → Recommendation |
| **Iterate** | Needs refinement | Dispatch a fresh background Agent that calls `codex-reply` with the prior `threadId` |
| **Conflict** | Disagreement | Both approaches → Trade-offs → Recommend with rationale |
