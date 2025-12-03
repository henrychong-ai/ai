# Common Instruction Patterns

**Proven structures and templates for effective instruction files**

---

## Agent Patterns

### Domain Specialist Pattern
**Use When:** Creating expert agent for specific technical domain

**Structure:**
```markdown
# **AGENT NAME: DOMAIN SPECIALIST**

Expert in [domain] with [key capabilities]. Specialized for [specific use cases].

## 🎯 **AUTO-ACTIVATION SEQUENCE**
1. **Load Context**: [Context requirements]
2. **Tool Readiness**: [Tool preparation]
3. **Success Metrics**: [Excellence standards]

## 📚 **DOMAIN EXPERTISE**
### [Subtopic 1]
[Specialized knowledge]

### [Subtopic 2]
[Specialized knowledge]

## ⚙️ **OPERATIONAL PROTOCOLS**
### [Workflow 1]
[Step-by-step procedures]

### [Workflow 2]
[Step-by-step procedures]

## 🏆 **SUCCESS METRICS**
[Measurement criteria]
```

**Examples:** typescript, python, rust, sql agents

---

### Business Context Pattern
**Use When:** Agent needs company/domain business integration

**Structure:**
```markdown
# **AGENT NAME: BUSINESS SPECIALIST**

[Business domain] expert with [strategic focus]. Integrates [business context] for [outcome optimization].

## 🎯 **AUTO-ACTIVATION SEQUENCE**
1. **Load Context**: Reference project-instructions.md for business priorities
2. **Business Assessment**: [KPIs, metrics, strategic alignment]
3. **Tool Readiness**: [Business-aware tool preparation]

## 🏢 **BUSINESS CONTEXT**
[Company overview, strategic priorities, revenue optimization]

## 💼 **DOMAIN EXPERTISE**
[Business-specific knowledge and frameworks]

## ⚙️ **OPERATIONAL PROTOCOLS**
[Business-first workflows]

## 📊 **SUCCESS METRICS & KPIs**
[Business outcome measurements]
```

**Examples:** compliance-officer, security-auditor, code-reviewer agents

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

**Examples:** travel, islamic-finance, compliance skills

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

## Integration Patterns

### Agent + Project Instructions
**When:** Agent needs business context

**Pattern:**
```markdown
## 🎯 **AUTO-ACTIVATION SEQUENCE**
1. **Load Context**: Reference project-instructions.md for:
   - Business priorities and strategic goals
   - Revenue optimization frameworks
   - Escalation criteria and thresholds
2. **Business Assessment**: [Use context for decisions]
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
## 🎯 **AUTO-ACTIVATION SEQUENCE**
1. **Load Skill Context**: Reference [skill-name] skill for:
   - Bundled resources and references
   - Detailed procedures and patterns
2. **Proactive Operation**: [Auto-trigger behavior]
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

**Example:** instruction-creator (agent for proactive optimization, skill for explicit reference)

---

## Template Variables

### Common Placeholders
- `[domain]`: Technical or business domain
- `[tool]`: Specific tool or format name
- `[operation]`: Specific action or workflow
- `[source]`: Data source or system
- `[outcome]`: Desired result or goal

### Section Headers
- **🎯 AUTO-ACTIVATION SEQUENCE**: Agent startup
- **📚 DOMAIN EXPERTISE**: Knowledge areas
- **⚙️ OPERATIONAL PROTOCOLS**: Workflows
- **🏆 SUCCESS METRICS**: Measurements
- **🏢 BUSINESS CONTEXT**: Company info
- **📊 SUCCESS METRICS & KPIS**: Business measurements

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
## AUTO-ACTIVATION SEQUENCE
1. **Load Context**: Reference project-instructions.md for business priorities
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
- ✅ YAML front matter complete
- ✅ "Use PROACTIVELY" in description
- ✅ Auto-activation sequence defined
- ✅ Success metrics clear

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

**Last Updated:** 2025-10-28
**Use Case:** Reference templates and patterns for instruction file creation
