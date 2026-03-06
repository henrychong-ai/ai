---
name: codex
description: Route requests to OpenAI GPT-5.4 via Codex MCP for second opinions, hard problems, and code review. Triggers on /codex, "use codex", with reasoning levels (none/low/medium/high/xhigh).
allowed-tools: mcp__codex__codex, mcp__codex__codex-reply
---

# Codex Skill - OpenAI GPT-5.4 Integration

Access OpenAI's GPT-5.4 (unified coding + reasoning model) for second opinions, hard problems, and code review. Runs in main thread—context flows TO Codex, responses flow BACK for integration.

## Quick Reference

| Trigger | Model | Reasoning |
|---------|-------|-----------|
| `/codex` or `use codex` | gpt-5.4 | high (default) |
| `use codex [level]` | gpt-5.4 | specified level |

**Reasoning Levels:** `none` → `low` → `medium` → `high` → `xhigh` (always pass explicitly)

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
- **Downgrading reasoning level** (using `medium` or lower instead of `high`) without explicit user request

## MCP Syntax

**CRITICAL: Always use `high` reasoning unless user explicitly requests a different level.** Do not downgrade to `medium` or lower without explicit user instruction.

### Primary Session (Default - high reasoning)
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.4",
    "model_reasoning_effort": "high"  // ALWAYS pass explicitly - do not omit
  }
})
```

### With Different Reasoning Level (only when user explicitly requests)
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.4",
    "model_reasoning_effort": "medium"  // only include when user explicitly requests: none/low/medium/xhigh
  }
})
```

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
