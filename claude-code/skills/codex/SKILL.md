---
name: codex
description: Route requests to OpenAI GPT-5.2 models via Codex MCP for second opinions, hard problems, and code review. Triggers on /codex, "use codex", with -g flag for general model and reasoning levels (none/low/medium/high/xhigh).
allowed-tools: mcp__codex__codex, mcp__codex__codex-reply
---

# Codex Skill - OpenAI GPT-5.2 Integration

Access OpenAI's GPT-5.2 models for second opinions, hard problems, and code review. Runs in main thread—context flows TO Codex, responses flow BACK for integration.

## Quick Reference

| Trigger | Model | Reasoning |
|---------|-------|-----------|
| `/codex` or `use codex` | gpt-5.2-codex | xhigh (default) |
| `use codex -g` | gpt-5.2 | xhigh |
| `use codex [level]` | gpt-5.2-codex | specified level |
| `use codex -g [level]` | gpt-5.2 | specified level |

**Reasoning Levels:** `none` → `low` → `medium` → `high` → `xhigh` (default, best quality)

## Models

| Aspect | gpt-5.2-codex (default) | gpt-5.2 (-g flag) |
|--------|-------------------------|-------------------|
| **Focus** | Specialized coding | General reasoning |
| **Strengths** | Multi-file reasoning, debugging, refactoring, performance optimization | Broad knowledge, research, strategy, documentation |
| **Best for** | Code problems, architecture, debugging | Non-code technical, cross-domain, research |
| **Context** | 400K tokens | 400K tokens |

**Model Selection:** Use default `gpt-5.2-codex` for any code-related problem. Use `-g` flag only when problem isn't primarily about code.

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

## MCP Syntax

### Primary Session
```
mcp__codex__codex({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.2-codex",         // or "gpt-5.2"
    "model_reasoning_effort": "xhigh"  // none/low/medium/high/xhigh
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
