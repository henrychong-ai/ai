---
name: gemini-gem-creator
description: This skill creates and converts Gemini Custom Gems using the 4-component framework (Persona/Task/Context/Format). Create gems from requirements through interactive discovery, or convert Claude Code agents/skills to team-shareable gems. Optimizes existing gems against quality standards. Use for Fusang/Portcullis Google Workspace gem distribution, gemini-gem-converter, convert to gemini.
model: opus
allowed-tools: Read, Glob, Write
---

# Gemini Gem Creator

Create, convert, and optimize Google Gemini Custom Gems for team distribution.

## Quick Start

**Two Modes:**

| Mode | Use When | Triggers |
|------|----------|----------|
| **Create** | Building gem from requirements | "create gem", "new gem", "I need a gem" |
| **Convert** | Transforming CC agent/skill to gem | "convert to gemini", "gemini version", "transform agent" |

## Mode Selection

### Create Mode
Build new Gemini gems from requirements through interactive discovery.

**Workflow:**
1. Discovery - Ask questions to understand requirements
2. Construction - Build P/T/C/F components
3. Refinement - Iterate based on feedback
4. Validation - Run 5-quality-test framework

→ See `references/creation/discovery-workflow.md` for detailed process
→ See `references/creation/domain-templates.md` for domain-specific templates

### Convert Mode
Transform Claude Code agents/skills to team-shareable Gemini gems.

**Workflow:**
1. Source Analysis - Read CC file (READ-ONLY, never modify)
2. Content Audit - Identify what to remove/preserve
3. Transformation - Map CC sections to gem components
4. Validation - Ensure CC syntax eliminated, business context preserved

→ See `references/conversion/removal-protocols.md` for sanitization rules
→ See `references/conversion/transformation-mapping.md` for CC → Gem mapping

## Gemini 4-Component Framework

| Component | Purpose | Key Elements |
|-----------|---------|--------------|
| **PERSONA** | Who the gem is | Role, expertise, communication style, audience |
| **TASK** | What the gem does | Objective, numbered actions, success criteria |
| **CONTEXT** | What the gem knows | Business background, regulations, constraints |
| **FORMAT** | How output looks | Structure, length, style, required elements |

→ See `references/framework/component-guide.md` for detailed construction guidance

### Quick Component Templates

**PERSONA:**
```
You are a [role] with expertise in [domains]. You have deep knowledge of [frameworks/standards]. You communicate in [tone] suitable for [audience].
```

**TASK:**
```
[Primary objective]
1. [Specific action 1]
2. [Specific action 2]
3. [Specific action 3]

[Success criteria]
```

**CONTEXT:**
```
[Company operations and positioning]
[Regulatory frameworks]
[Audience characteristics]
[Key constraints]
```

**FORMAT:**
```
Structure output as:
1. [Section 1] - [Purpose]
2. [Section 2] - [Purpose]

[Length constraints]
[Style guidelines]
[Required elements]
```

## 5-Quality-Test Framework

All gems must pass before distribution:

| Test | Question |
|------|----------|
| **Specificity** | Could someone else read instructions and know exactly what gem does? |
| **Consistency** | Will 10 uses produce consistent output structure? |
| **Differentiation** | Is gem noticeably different from generic Gemini? |
| **Usability** | Are there clear, concrete use cases? |
| **Completeness** | Does gem have all info needed to operate standalone? |

→ See `references/framework/quality-tests.md` for detailed validation

## Output Format

```markdown
## Gemini Gem: [Name]
*Created/Converted for: [Team/Purpose]*

### Gem Description
[1-2 sentences for Gemini description field]

---BEGIN GEM INSTRUCTIONS---

PERSONA:
[Complete persona]

TASK:
[Complete task with numbered actions]

CONTEXT:
[Complete context]

FORMAT:
[Complete format specification]

---END GEM INSTRUCTIONS---

### Quality Assessment
| Test | Result |
|------|--------|
| Specificity | [Pass/Needs work] |
| Consistency | [Pass/Needs work] |
| Differentiation | [Pass/Needs work] |
| Usability | [Pass/Needs work] |
| Completeness | [Pass/Needs work] |

### Recommended Attachments
[Files to attach, or "None needed"]

### Next Steps
1. Copy instructions to Gemini
2. Test with sample prompts
3. Share with team
```

→ See `references/output/output-formats.md` for complete templates

## Critical Rules

### For Create Mode
- Ask discovery questions one at a time
- Push for specificity when answers are vague
- Use domain templates for Fusang/Portcullis contexts
- Validate against 5-quality-test framework

### For Convert Mode
- **NEVER modify or delete source CC file**
- Remove ALL CC-specific syntax (YAML, tools, MCP, paths)
- Remove ALL individual-specific content (personal names, custom framework triggers)
- PRESERVE business context (Fusang, Portcullis, regulatory frameworks)

## File Attachment Strategy

**Attach when:**
- Templates/examples are lengthy (>500 words)
- Style guides or brand guidelines exist
- Reference materials provide essential context

**Embed when:**
- Core instructions are brief and stable
- Essential knowledge fits in 200-300 words
- Information is fundamental to every use

## Gemini Magic Wand

Gemini has a built-in instruction expansion feature:
- Start with concise instructions
- Use magic wand to expand if needed
- Review expansions critically
- Preserve domain-specific precision

## Reference Directory

### Framework (Shared)
| File | Content |
|------|---------|
| `framework/component-guide.md` | Detailed P/T/C/F construction |
| `framework/quality-tests.md` | 5-test framework + validation checklist |
| `framework/common-pitfalls.md` | 7 pitfalls with fixes |

### Creation Mode
| File | Content |
|------|---------|
| `creation/discovery-workflow.md` | Interactive creation process |
| `creation/domain-templates.md` | Regulatory, Islamic Finance, Content, Legal, Wealth Management |
| `creation/optimization-workflow.md` | Gem improvement process |

### Conversion Mode
| File | Content |
|------|---------|
| `conversion/removal-protocols.md` | CC syntax sanitization rules |
| `conversion/transformation-mapping.md` | CC → Gem syntax table |
| `conversion/conversion-edge-cases.md` | KG, personal frameworks, technical agents |

### Examples & Output
| File | Content |
|------|---------|
| `examples/production-gems.md` | Real gems: Harvey AI, Gem Creator |
| `examples/domain-examples.md` | Sukuk, Newsletter, Regulatory |
| `output/output-formats.md` | Creation + Conversion output templates |

## Activation Triggers

**Create Mode:**
- "create a gem", "build a gem", "new gem"
- "I need a gem that...", "help me create"
- "gem for [domain]"

**Convert Mode:**
- "convert to gemini", "gemini version"
- "transform agent to gem", "CC to gem"
- "make gem from agent"

**Optimization:**
- "optimize gem", "improve gem"
- "my gem isn't working", "gem inconsistent"
