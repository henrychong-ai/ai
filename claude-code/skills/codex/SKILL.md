---
name: codex
description: This skill should be used to route requests to OpenAI GPT-5.5 via Codex MCP for second opinions, hard problems, and code review. Triggers on /codex, "use codex", with reasoning levels (none/low/medium/high/xhigh) and service tier (fast/standard).
allowed-tools: Agent, mcp__codex__codex, mcp__codex__codex-reply
---

# Codex Skill — OpenAI GPT-5.5

Second opinions, hard problems, code review via GPT-5.5. **Dispatch runs in the background via the Agent tool** — the main thread stays free while Codex thinks; the harness notifies on completion and Claude integrates the response then.

## Quick Reference

| Trigger | Reasoning | Service Tier |
|---------|-----------|--------------|
| `/codex` | high | fast (default) |
| `/codex [level]` | specified | fast |
| `/codex standard` | high | standard |
| `/codex [level] standard` | specified | standard |

**Reasoning:** `none` → `low` → `medium` → `high` (default) → `xhigh`
**Tiers:** `fast` (default, 1.5x speed) • `standard`/`normal` (opt-in)

Arguments appear in any order. Extract reasoning level + service tier from user input.

## Context Preparation

Curate context before calling — quality in = quality out:
1. Extract relevant code snippets (not entire files)
2. Include full error traces if debugging
3. State what's been tried
4. Define what "solved" looks like
5. Mention constraints (performance, security, compatibility)

**Anti-patterns:** Dumping entire files • Vague questions • Missing tech context • No success criteria

## Execution: Background Dispatch (MANDATORY)

Every `/codex` invocation dispatches the Codex MCP call via the `Agent` tool with `run_in_background: true`. The main thread does **not** call `mcp__codex__codex` synchronously — that would block until Codex returns.

After dispatch, reply to the user with one short line (e.g. `Codex query dispatched; will surface response when ready`) and continue with other work. When the harness fires the background-completion notification, surface and integrate the Codex output per the **Response Integration** section below.

### Dispatch Pattern

```
Agent({
  description: "Codex: [3-5 word topic]",
  subagent_type: "general-purpose",
  run_in_background: true,
  prompt: "Call mcp__codex__codex once with the prompt and config below. Return Codex's full response verbatim — no summarisation, no commentary.\n\nPrompt:\n[prepared prompt]\n\nConfig:\n  model: gpt-5.5\n  model_reasoning_effort: [high | user-specified]\n  service_tier: [fast | standard]"
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

## MCP Syntax (Reference for the Background Agent)

The patterns below describe how the spawned background agent calls `mcp__codex__codex`. The `/codex` skill itself never calls these MCP tools from the main thread — it only spawns the wrapper Agent.

### MANDATORY: Always Pass Config Block

Every call MUST include `config` with `model`, `model_reasoning_effort`, and `service_tier`. Never rely on config.toml defaults.

**Defaults:** `gpt-5.5` + `high` + `fast`. Do not downgrade without explicit user request.

> **Parameter Placement:**
> - `model_reasoning_effort` and `service_tier` are **NOT** top-level params — **only work inside `config`**
> - `model` exists at top level AND in config — **always use `config`** for consistency
> - Top-level `model_reasoning_effort` or `service_tier` will **silently fail**

### Correct Syntax
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.5",                   // always gpt-5.5
    "model_reasoning_effort": "high",      // or user-specified: none/low/medium/xhigh
    "service_tier": "fast"                 // default; "standard" only when user requests
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
  config: { "model": "gpt-5.5", "model_reasoning_effort": "high", "service_tier": "fast" }
})
mcp__codex__codex({
  prompt: "Analyze approach B...",
  config: { "model": "gpt-5.5", "model_reasoning_effort": "high", "service_tier": "fast" }
})
```

### Common Mistakes

**❌ Config values at top level**
```
mcp__codex__codex({
  prompt: "...",
  model_reasoning_effort: "high",    // ❌ NOT top-level — silently ignored
  service_tier: "fast"               // ❌ NOT top-level — silently ignored
})
```

**❌ Missing config block**
```
mcp__codex__codex({
  prompt: "...",
  model: "gpt-5.5"                   // ❌ Only sets model, loses reasoning + tier
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
