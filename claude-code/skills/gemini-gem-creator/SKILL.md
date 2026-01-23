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

## Gemini Knowledge Base Limits (Official)

**Hard Limits per Gem:**

| Constraint | Limit | Source |
|------------|-------|--------|
| **Maximum files** | **10 files** | Google Workspace Blog |
| **File size** | 100 MB per file | Google Workspace Updates |
| **Excluded** | Video, audio files | Gemini Apps Help |

**Supported File Types:**

| Category | Formats |
|----------|---------|
| **Documents** | TXT, DOC, DOCX, PDF, RTF, DOT, DOTX |
| **Spreadsheets** | XLS, XLSX, CSV, TSV |
| **Google Workspace** | Google Docs, Google Sheets |
| **NOT Supported** | Markdown (.md), JSON, YAML, XML |

**CRITICAL: Markdown (.md) files CANNOT be uploaded to Gemini Gems knowledge base.**

**Planning Implications:**
- With only 10 file slots, consolidate related content (e.g., combine SG/MY/HK clauses into single file)
- 100 MB per file is generous - size is rarely the constraint, file count is
- Google Docs from Drive auto-update; local uploads are static snapshots
- Context window: ~32K tokens (free) / 1M tokens (Gemini Advanced)

**Sources:**
- [Google Workspace Updates Blog](https://workspaceupdates.googleblog.com/2024/11/upload-google-docs-and-other-file-types-to-gems.html)
- [Google Workspace Blog](https://workspace.google.com/blog/product-announcements/new-gemini-gems-deeper-knowledge-and-business-context)

## Markdown to TXT Conversion

**When preparing Markdown files for Gemini Gems knowledge base:**

1. **Keep the Markdown syntax** - Do NOT strip formatting (headers, lists, bold, etc.)
2. **Only change the file extension** - Rename `.md` to `.txt`
3. **Content stays identical** - The model understands Markdown syntax in plain text

**Why keep Markdown syntax:**
- LLMs are trained on massive amounts of Markdown and understand it natively
- `#`, `##`, `###` convey document hierarchy to the model
- Lists, bold, tables provide structural information
- Stripping syntax removes valuable semantic information

**Conversion command:**
```bash
# Simple rename (content unchanged)
for f in *.md; do mv "$f" "${f%.md}.txt"; done

# Or create copies
for f in *.md; do cp "$f" "${f%.md}.txt"; done
```

**Result:** `.txt` files containing Markdown syntax are perfectly valid and give Gemini full structural understanding of your documents.

## File Attachment Strategy

**Attach when:**
- Templates/examples are lengthy (>500 words)
- Style guides or brand guidelines exist
- Reference materials provide essential context

**Embed when:**
- Core instructions are brief and stable
- Essential knowledge fits in 200-300 words
- Information is fundamental to every use

**Consolidation Strategy (to maximize 10-file limit):**
- Combine jurisdiction variants into single files (e.g., `model-clauses-all-jurisdictions.txt`)
- Merge related guides (e.g., combine boilerplate + term-termination into `general-provisions-guide.txt`)
- Keep templates separate when they're used independently
- Always use `.txt` extension (not `.md`) for knowledge base uploads

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
