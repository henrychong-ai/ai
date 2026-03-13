# MCP Tool Documentation Guide

**Best practices for documenting MCP tool calls in skills and instruction files**

**Updated:** 2026-03-13

---

## The Documentation Gap

MCP tool definitions provide Claude with a JSON schema (`name`, `description`, `inputSchema`), but schemas alone are often insufficient for correct tool usage — especially for tools with:

- Generic `object` params with `additionalProperties: true` (pass-through bags)
- Optional parameters where inclusion patterns matter
- Domain-specific value conventions not captured in schemas
- Parameters that exist at multiple levels (top-level AND nested)

**Skills and instruction files bridge this gap** by providing structured examples and explicit guidance that the schema cannot express.

---

## Claude API `input_examples` Field

The Claude API supports an `input_examples` field on tool definitions that provides concrete usage examples directly in the tool schema:

```json
{
  "name": "create_ticket",
  "input_schema": { ... },
  "input_examples": [
    {
      "title": "Critical bug",
      "priority": "critical",
      "labels": ["bug", "production"],
      "escalation": { "level": 2, "sla_hours": 4 }
    },
    {
      "title": "Feature request",
      "labels": ["feature-request"]
    },
    {
      "title": "Update docs"
    }
  ]
}
```

**Key properties:**
- Type: `array of map[unknown]` — each entry is a sample input object
- Shows progressive complexity (minimal → partial → full specification)
- Teaches format conventions, nesting patterns, and optional parameter correlations
- Internal testing: **72% → 90% accuracy** on complex parameter handling

### MCP Limitation

**`input_examples` is NOT available for MCP tools.** The MCP protocol spec defines tools with only `name`, `description`, `inputSchema`, and `annotations`. There is no `input_examples` field in the MCP tool definition.

This means:
- MCP servers **cannot** provide `input_examples` through the protocol
- Claude Code receives MCP tool definitions without examples
- Claude relies solely on `inputSchema` + `description` + system prompt instructions

**Implication:** For MCP tools, skill file documentation is the **only mechanism** to provide usage examples. This makes well-structured examples in skills critically important.

---

## MCP Tool Call Syntax in Skills

### Standard Format

Use JavaScript function call syntax for MCP tool examples:

```
mcp__<server>__<tool>({
  paramName: "value",
  nestedObject: {
    "key": "value"
  }
})
```

This maps directly to how Claude Code invokes MCP tools — it is not pseudocode.

### Naming Convention

MCP tools follow the pattern: `mcp__<server-name>__<tool-name>` with double underscores separating server and tool names.

---

## Best Practices for MCP Tool Examples

### 1. Show Progressive Complexity

Mirror the `input_examples` pattern — show minimal, partial, and full usage:

```markdown
### Minimal (required params only)
\`\`\`
mcp__service__query({
  prompt: "Find all open issues"
})
\`\`\`

### Typical (common optional params)
\`\`\`
mcp__service__query({
  prompt: "Find all open issues",
  config: {
    "max_results": 50,
    "sort": "created_desc"
  }
})
\`\`\`

### Full (all params)
\`\`\`
mcp__service__query({
  prompt: "Find all open issues",
  config: {
    "max_results": 50,
    "sort": "created_desc",
    "filters": ["status:open", "priority:high"]
  },
  cwd: "/path/to/project"
})
\`\`\`
```

### 2. Use Correct/Incorrect Examples for Ambiguous Parameters

When the schema is ambiguous (especially `additionalProperties: true` objects), show both wrong and right:

```markdown
**Wrong: Config values at top level**
\`\`\`
mcp__service__call({
  prompt: "...",
  setting_a: "value",    // NOT a top-level param — silently ignored
  setting_b: "value"     // NOT a top-level param — silently ignored
})
\`\`\`

**Correct: Settings nested in config**
\`\`\`
mcp__service__call({
  prompt: "...",
  config: {              // All config overrides grouped here
    "setting_a": "value",
    "setting_b": "value"
  }
})
\`\`\`
```

### 3. Document Schema vs Config Boundaries

When a tool has parameters that exist in multiple locations, explicitly document which go where:

```markdown
> **Parameter Placement:**
> - `param_a` is a top-level schema parameter — pass directly
> - `param_b` and `param_c` are NOT top-level — they only work inside `config`
> - Putting `param_b` at the top level will silently fail
```

### 4. Include a Schema Reference Table

Document the actual MCP tool schema so Claude has authoritative parameter information:

```markdown
## Tool Schema Reference

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `prompt` | string | **Yes** | User prompt |
| `config` | object | No | config.toml overrides (additionalProperties: true) |
| `model` | string | No | Model override |
```

### 5. Label Deprecated Parameters

When tools have deprecated parameters, make deprecation visible:

```markdown
| ~~`oldParam`~~ | string | — | **DEPRECATED** — use `newParam` |
```

### 6. Annotate Examples with Comments

Use inline comments to explain parameter choices:

```
mcp__service__call({
  prompt: "[prepared prompt]",
  config: {
    "model": "gpt-5.4",
    "reasoning": "high",    // user-specified: none/low/medium/xhigh
    "tier": "fast"           // default; use "standard" only when user requests
  }
})
```

---

## Common Pitfalls

### 1. `additionalProperties: true` Without Declared Properties

**Problem:** When an MCP tool defines `config: { type: "object", additionalProperties: true }` with no declared properties, Claude has no schema guidance about what keys go inside `config`.

**Solution:** Document valid config keys explicitly in the skill, with a schema reference table and annotated examples.

### 2. Parameters at Wrong Nesting Level

**Problem:** Claude sees a parameter name (e.g., `model`) at the top level of the schema and assumes all related settings go at the top level too.

**Solution:** Use correct/incorrect example pairs. Add a Parameter Placement Warning callout.

### 3. Relying on Schema Alone

**Problem:** The MCP tool's `description` field is too generic (e.g., "Run a session") and the schema doesn't convey usage patterns.

**Solution:** Enriched examples in the skill that cover the most common invocation patterns with realistic values.

### 4. Stale Examples After API Changes

**Problem:** MCP tool adds `threadId` but skill examples still show deprecated `conversationId`.

**Solution:** Include a schema reference table sourced from actual tool definitions. Review when upstream tools update.

---

## Skill Review Checklist for MCP Tools

When a skill wraps MCP tool calls, verify:

- [ ] Schema reference table documents all top-level parameters
- [ ] `config` / pass-through object keys explicitly documented
- [ ] Examples use correct nesting (not flattened)
- [ ] Correct/incorrect example pairs for ambiguous parameters
- [ ] Deprecated parameters clearly marked
- [ ] Progressive complexity (minimal → typical → full)
- [ ] Inline comments explain non-obvious parameter values
- [ ] Default values stated explicitly
- [ ] Examples use realistic values, not generic placeholders

---

**Last Updated:** 2026-03-13
**Use Case:** Reference guide for documenting MCP tool calls in skills and instruction files
