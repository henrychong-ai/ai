# Common Instruction Patterns

**Proven structures and templates for effective instruction files**

---

## Agent Patterns

### Domain Specialist Pattern
**Use When:** Creating expert agent for specific technical domain

**Structure:** the SKILL.md "Agent Template Structure" (frontmatter, one role paragraph, contract), plus the domain knowledge the agent cannot load from a skill:
```markdown
---
name: agent-name
description: [Domain] specialist. [Capabilities]. Use PROACTIVELY for [triggers].
model: opus
# effort: omitted; pin only when a specific level is needed
disallowedTools: Agent, Task    # leaf worker: no nested fan-out
---

[One paragraph: role, domain owned, outcome it is accountable for.]

## Contract
- **Inputs:** [what the brief supplies]
- **Does:** [work, tools, checks before returning]
- **Boundary:** [actions it stops and reports instead of performing]
- **Returns:** [report to the caller: results, verification, failures, decisions needed]

## Domain Knowledge
[Only what the agent cannot load from a skill or reference]
```

**Examples:** typescript, python, rust, sql agents

---

### Business Context Pattern
**Use When:** Agent needs company/domain business integration

**Structure:** the Domain Specialist structure above, with the business context named as an input the agent loads rather than pasted into its body:
```markdown
## Contract
- **Inputs:** the brief, plus [project instructions / domain skill] for business priorities and escalation thresholds
- **Does:** [business-first workflow]
- **Boundary:** [decisions above the escalation threshold go back to the caller]
- **Returns:** [recommendation, the context it relied on, open decisions]
```

**Examples:** compliance-officer, business-domain agents

---

## Skill Patterns

### Tool Integration Pattern
**Use When:** Skill wraps specific tool or file format operations

**Structure:**
```markdown
# [Tool Name] Skill

Expert [tool/format] operations for [use cases].

## About [Tool/Format]

[Brief overview of what it is and why it's useful]

## Key Capabilities

- **[Operation 1]**: [Description]
- **[Operation 2]**: [Description]
- **[Operation 3]**: [Description]

## Using This Skill

### [Operation 1]
[Step-by-step guidance]

**Example:**
[Concrete example]

### [Operation 2]
[Step-by-step guidance]

## Bundled Resources

**Scripts (`scripts/`):**
- `script-name.py`: [Purpose]

**References (`references/`):**
- `reference-doc.md`: [Content description]

## Quick Reference

Common operations:
- **"[User query]"**: [What Claude does]
- **"[User query]"**: [What Claude does]
```

**Examples:** pdf, xlsx, docx, pptx skills

---

### Knowledge Domain Pattern
**Use When:** Skill provides specialized knowledge with references

**Structure:**
```markdown
# [Domain] Skill

Specialized knowledge for [domain area] with [key focus].

## About [Domain]

[Domain overview and scope]

## Core Concepts

### [Concept 1]
[Explanation]

### [Concept 2]
[Explanation]

## Practical Applications

### [Use Case 1]
[Guidance]

### [Use Case 2]
[Guidance]

## Reference Materials

Detailed guides in `references/` subdirectory:
- **`guide-1.md`**: [Content]
- **`guide-2.md`**: [Content]

## Quick Reference

When working with [domain]:
- **"[Query pattern]"**: [Approach]
- **"[Query pattern]"**: [Approach]
```

**Examples:** travel, finance, compliance skills

---

## Slash Command Patterns

### Simple Query Pattern
**Use When:** Command performs single query or lookup

**Structure:**
```markdown
# [Query Description]

Query [source] for [information] and return [result].

## Input Processing
- $ARGUMENTS represents [expected input]
- If empty: [default behavior]
- If provided: [query behavior]

## Tool Usage
- Use [specific tool] to query [source]
- Apply filters: [filtering logic]

## Output Requirements
- Format: [output structure]
- Include: [required elements]
- Handle empty results: [fallback]
```

**Examples:** /kg, /things commands

---

### Workflow Orchestration Pattern
**Use When:** Command coordinates multi-step workflow

**Structure:**
```markdown
# [Workflow Description]

Coordinate [multi-step process] to achieve [outcome].

## Workflow Steps

### Phase 1: [Name]
- Tool: [specific tool]
- Action: [what to do]
- Verification: [how to verify]

### Phase 2: [Name]
- Tool: [specific tool]
- Action: [what to do]
- Verification: [how to verify]

### Phase 3: [Name]
- Tool: [specific tool]
- Action: [what to do]
- Verification: [how to verify]

## Error Handling
- If Phase 1 fails: [recovery]
- If Phase 2 fails: [recovery]

## Success Criteria
[How to determine workflow succeeded]
```

**Examples:** /sync-config, /prd commands

---

## MCP Tool Integration Pattern

### MCP Tool Wrapper Skill
**Use When:** Skill wraps one or more MCP tool calls and needs to guide correct parameter usage

**Structure:**
```markdown
# [Tool Name] Skill

[Brief description of what the MCP tool does and when to use it]

## Quick Reference
[Trigger table, defaults, argument parsing]

## MCP Tool Schema Reference

### `mcp__server__tool` — Top-Level Parameters
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `param_a` | string | **Yes** | Description |
| `config` | object | No | Pass-through overrides (additionalProperties: true) |

> **Parameter Placement Warning:**
> - `setting_x` and `setting_y` only work inside `config`
> - Putting them at the top level will silently fail

## MCP Syntax

### Default Call
[Annotated example with correct nesting]

### Common Mistakes
[Incorrect/correct example pairs]

### Continue Conversation (if applicable)
[Follow-up tool example with correct param names]
```

**Key Principles:**
- Document actual schema (top-level params vs pass-through objects)
- Use correct/incorrect example pairs for ambiguous parameters
- Show progressive complexity (minimal → typical → full)
- Mark deprecated parameters with strikethrough
- Since MCP tools cannot use Claude API `input_examples`, skill examples are the **only** mechanism for usage guidance

**Reference:** See `mcp-tool-documentation-guide.md` for comprehensive MCP documentation practices

**Examples:** codex skill

---

## Integration Patterns

### Agent + Project Instructions
**When:** Agent needs business context

**Pattern:**
```markdown
## Contract
- **Inputs:** the brief, plus project-instructions.md for business priorities, strategic goals, and escalation thresholds
```

**Integration:**
- Agent loads project-instructions.md on activation
- Applies business context to all decisions
- Uses escalation criteria from project context

---

### Skill + Bundled Scripts
**When:** Skill needs deterministic code execution

**Pattern:**
```markdown
## Bundled Resources

**Scripts (`scripts/`):**
- `operation.py`: Performs [specific operation]
  - Usage: [how to call]
  - Parameters: [what to pass]
  - Output: [what returns]

## Using [Operation]

When user requests [operation]:
1. Prepare inputs: [requirements]
2. Execute: `bash scripts/operation.py [args]`
3. Verify: [check output]
```

**Integration:**
- Script handles deterministic operations
- SKILL.md guides when and how to use script
- Claude loads script only if needed for patching

---

### Agent + Skill Hybrid
**When:** Need both proactive and explicit access

**Pattern:**

**Agent:**
```markdown
## Contract
- **Inputs:** the brief, plus the [skill-name] skill for bundled references and detailed procedures
- **Does:** [proactive operation the agent owns]
```

**Skill:**
```markdown
## About This Skill

Works in conjunction with [agent-name] agent:
- **Agent**: Proactive operation and monitoring
- **Skill**: Explicit invocation and bundled resources

For automatic operation, the agent handles triggers.
For manual control, use "use skill [name]".
```

**Example:** instruction-creator (skill handles both proactive creation and explicit reference)

---

## Template Variables

### Common Placeholders
- `[domain]`: Technical or business domain
- `[tool]`: Specific tool or format name
- `[operation]`: Specific action or workflow
- `[source]`: Data source or system
- `[outcome]`: Desired result or goal

### Agent Body Sections
- **Role paragraph**: role, domain owned, accountable outcome
- **Contract**: inputs, what it does, approval boundary, report returned to the caller
- **Domain Knowledge** (optional): only what cannot be loaded from a skill

---

## Anti-Patterns to Avoid

**❌ Vague Descriptions**
```yaml
description: Helps with TypeScript stuff
```
**✅ Specific Descriptions**
```yaml
description: TypeScript specialist with advanced type system mastery. Use PROACTIVELY for fintech TypeScript optimization.
```

---

**❌ Missing Integration**
```markdown
## Domain Expertise
[No reference to business context or other files]
```
**✅ Clear Integration**
```markdown
## Contract
- **Inputs:** the brief, plus project-instructions.md for business priorities
```

---

**❌ Kitchen Sink Pattern**
```markdown
[Everything in one massive section with no structure]
```
**✅ Organized Sections**
```markdown
## Section 1: [Clear purpose]
## Section 2: [Clear purpose]
## Section 3: [Clear purpose]
```

---

**❌ Duplicate Content**
```markdown
SKILL.md: [Complete guide to X]
references/guide-to-x.md: [Complete guide to X again]
```
**✅ Progressive Disclosure**
```markdown
SKILL.md: [Overview + when to use]
references/guide-to-x.md: [Detailed guide loaded as needed]
```

---

## Validation Patterns

### Quick Validation Checklist
```markdown
Agent Validation:
- ✅ YAML front matter complete (`model: opus` unless another tier is warranted; `effort` omitted unless needed)
- ✅ "Use PROACTIVELY" in description where auto-delegation is wanted
- ✅ Contract defined: inputs, approval boundary, report returned to the caller
- ✅ Leaf workers bar `Agent`/`Task` or list an explicit `tools:` allowlist

Skill Validation:
- ✅ YAML front matter complete
- ✅ Third-person description
- ✅ Imperative/infinitive writing style
- ✅ Bundled resources organized

Command Validation:
- ✅ Natural language instructions clear
- ✅ Tool usage specified
- ✅ $ARGUMENTS handling described
- ✅ Output format defined
```

---

**Last Updated:** 2026-09-24 (agent patterns moved to the lean role + contract template)
**Use Case:** Reference templates and patterns for instruction file creation
