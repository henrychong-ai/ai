---
name: codex
description: Route requests to OpenAI GPT-5.4 via Codex MCP for second opinions, hard problems, and code review. Triggers on /codex, "use codex", with reasoning levels (none/low/medium/high/xhigh) and service tier (fast/standard).
allowed-tools: mcp__codex__codex, mcp__codex__codex-reply
---

# Codex Skill - OpenAI GPT-5.4 Integration

Access OpenAI's GPT-5.4 (unified coding + reasoning model) for second opinions, hard problems, and code review. Runs in main thread—context flows TO Codex, responses flow BACK for integration.

## Quick Reference

| Trigger | Model | Reasoning | Service Tier |
|---------|-------|-----------|--------------|
| `/codex` | gpt-5.4 | high | fast (default) |
| `/codex [level]` | gpt-5.4 | specified | fast |
| `/codex standard` or `/codex normal` | gpt-5.4 | high | standard |
| `/codex [level] standard` | gpt-5.4 | specified | standard |

**Reasoning Levels:** `none` → `low` → `medium` → `high` → `xhigh` (always pass explicitly)
**Service Tiers:** `fast` (default, 1.5x speed, 2x tokens) • `standard`/`normal` (opt-in to disable fast)

### Argument Parsing

Arguments can appear in any order. Extract:
1. **Reasoning level** — any of: `none`, `low`, `medium`, `high`, `xhigh` (default: `high`)
2. **Service tier** — `fast` (default, explicit is valid), `standard` or `normal` disables fast mode

## When to Use Codex

**USE FOR:** Stuck after multiple attempts • Unfamiliar errors • Architecture decisions • Algorithm design • Unfamiliar tech • Solution validation • Debugging not progressing • Second opinions

**DON'T USE FOR:** Simple operations • Standard CRUD • Well-documented APIs • Tasks you're handling confidently • Minimal context situations

**PROACTIVE:** Before major architecture decisions • After same error 2+ times • When user wants alternatives • Complex multi-file refactoring

## Context Preparation

**Quality of response depends on context preparation.**

### Checklist
1. **Extract relevant code** - Curated snippets, not entire files
2. **Include errors** - Full stack trace if debugging
3. **State what's tried** - Avoid redundant suggestions
4. **Define success** - What does "solved" look like?
5. **Mention constraints** - Performance, security, compatibility

### Prompt Structure
```
## Context
[Language/Framework], [Project description], [Current state]

## Relevant Code
[Minimal, curated snippets]

## Problem
[Specific, focused question]

## Constraints
[Requirements, limitations]

## Expected Output
[Code, explanation, comparison, etc.]
```

### Anti-Patterns
- Dumping entire files without curation
- Vague questions ("make this better")
- Missing technology context
- No success criteria
- Asking what Claude can answer confidently
- **Omitting the `config` block** — model, reasoning effort, and service tier must ALWAYS be passed explicitly
- **Downgrading reasoning level** (using `medium` or lower instead of `high`) without explicit user request
- **Omitting `service_tier`** — always pass `"fast"` (default) or `"standard"` (only when user requests)

## MCP Syntax

### MANDATORY: Always Pass Config Block

**CRITICAL:** Every `mcp__codex__codex` call MUST include the `config` object with `model`, `model_reasoning_effort`, and `service_tier` explicitly set. Never rely on Codex config.toml defaults — always pass these three parameters so the user can see exactly what model configuration is being used.

**Defaults: `gpt-5.4` model + `high` reasoning + `fast` service tier.** Do not downgrade any without explicit user request.

### Default Session (high reasoning, fast tier)
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.4",
    "model_reasoning_effort": "high",
    "service_tier": "fast"
  }
})
```

### With Different Reasoning Level (fast tier maintained)
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.4",
    "model_reasoning_effort": "medium",  // user-specified: none/low/medium/xhigh
    "service_tier": "fast"
  }
})
```

### Standard Tier (only when user passes `standard` or `normal`)
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.4",
    "model_reasoning_effort": "high",  // or user-specified level
    "service_tier": "standard"
  }
})
```

**Note:** `service_tier` must always be explicitly passed — `"fast"` (default) or `"standard"` (when user requests). Never omit it.

### Continue Conversation
```
mcp__codex__codex-reply({
  conversationId: "[from previous response]",
  prompt: "[follow-up]"
})
```

## Response Integration

**Don't just pass through—INTEGRATE with main thread context.**

| Pattern | When | Action |
|---------|------|--------|
| **Direct Implementation** | Codex provides working code | Verify fit → Adapt style → Implement → Test |
| **Synthesis** | Second opinion | Present both perspectives → Highlight agreements/differences → Unified recommendation |
| **Iterative** | Response needs refinement | Use `codex-reply` → Provide feedback → Repeat |
| **Conflict** | Claude and Codex disagree | Present both → Explain trade-offs → Recommend with rationale |

## Use Case Patterns

**Second Opinion:** Share implementation + ask "Is this sound? Alternatives? Edge cases?"

**Debugging:** Error + relevant code + what's tried + "What's causing this?"

**Architecture:** Options considered + requirements + constraints + "Which approach and why?"

**Performance:** Current code + metrics + target + "What optimizations?"

**Code Review:** Code + review focus areas + "What issues and fixes?"

**Alternatives:** Current approach + likes/dislikes + "What other approaches? Trade-offs?"

## Parallel Execution

Run multiple queries concurrently for independent analyses:
```
mcp__codex__codex({ prompt: "Analyze A...", config: {...} })
mcp__codex__codex({ prompt: "Analyze B...", config: {...} })
```
