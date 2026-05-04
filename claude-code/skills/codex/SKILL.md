---
name: codex
description: This skill should be used to route requests to OpenAI GPT-5.5 via Codex MCP for second opinions, hard problems, and code review. Triggers on /codex, "use codex", with reasoning levels (none/low/medium/high/xhigh) and service tier (fast/standard).
allowed-tools: mcp__codex__codex, mcp__codex__codex-reply
---

# Codex Skill — OpenAI GPT-5.5

Second opinions, hard problems, code review via GPT-5.5. Runs in main thread — context flows TO Codex, responses flow BACK for integration.

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

## MCP Syntax

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

Don't pass through — INTEGRATE with main thread context.

| Pattern | When | Action |
|---------|------|--------|
| **Implement** | Working code returned | Verify fit → Adapt style → Implement → Test |
| **Synthesise** | Second opinion | Both perspectives → Agreements/differences → Recommendation |
| **Iterate** | Needs refinement | `codex-reply` → Feedback → Repeat |
| **Conflict** | Disagreement | Both approaches → Trade-offs → Recommend with rationale |
