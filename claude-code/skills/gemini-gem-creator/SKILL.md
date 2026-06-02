---
name: gemini-gem-creator
description: Creates and converts Gemini Custom Gems using the 4-component framework (Persona/Task/Context/Format). Create gems from requirements through interactive discovery, or convert Claude Code agents/skills to team-shareable gems. Optimizes existing gems against quality standards. Use for Fusang/Portcullis Google Workspace gem distribution.
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

## Model-Aware Gem Design (Gemini 3.x)

A gem runs on whichever model the user selects in the Gemini app — **a gem cannot pin its own model**. Write gem instructions to be model-portable, and recommend a runtime model in the gem doc.

**Current model selector (verify against [Gemini release notes](https://gemini.google/release-notes/)):**

| Model / mode | Recommend for |
|--------------|---------------|
| **Gemini 3.5 Flash** (app default) | Fast, high-volume, agentic tasks |
| **Gemini 3.1 Pro** (shown as "Pro") | Complex reasoning, deep analysis, hardest problems |
| **Gemini 3.5 Pro** (rolling out ~2026-06) | Successor flagship — recheck availability |
| **Deep Think** (mode) | Deepest multi-step reasoning |
| **Deep Research** (mode) | Multi-source research gems (e.g. dossier-style) |

Add a **Recommended Model** line to every gem, e.g. "Recommended Model: select *Pro* or *Deep Think* for deep analysis; *3.5 Flash* for quick drafts."

**Gemini 3.x instruction style (differs from older models — [Google guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/gemini-3-prompting-guide)):**
- Be concise and direct — Gemini 3 over-analyses verbose, legacy prompt-engineering scaffolding.
- It is terse by default — to get longer or conversational output, say so explicitly in FORMAT.
- Lead with the most critical role + constraints (PERSONA/TASK first); a static gem instruction acts as a system instruction, so front-load what anchors behaviour.
- Structure with Markdown **or** XML-style tags — pick one, do not mix.
- State desired verbosity explicitly ("concise" / "comprehensive") rather than relying on defaults.

## Gemini Knowledge Base Limits (verified 2026-06 — recheck quarterly)

**Hard Limits per Gem:**

| Constraint | Limit | Source |
|------------|-------|--------|
| **Maximum files** | **10 files** | Gemini Apps Help (file types & limits) |
| **File size** | 100 MB per file (video up to 2 GB; audio higher) | Gemini Apps Help |

**Supported File Types (Gemini accepts "most file types"):**

| Category | Formats |
|----------|---------|
| **Documents** | Markdown (.md), TXT, PDF, DOC, DOCX, RTF |
| **Spreadsheets / Data** | XLS, XLSX, CSV, TSV, JSON |
| **Code** | JS, TS, Python, and other common source files |
| **Images** | JPG, PNG (visual context) |
| **Google Workspace** | Google Docs, Google Sheets |

**Markdown (.md) is now natively supported** — upload `.md` directly, no conversion needed (this reverses earlier guidance). Plain `.txt` still works, so existing `.txt` knowledge files remain valid.

**Planning Implications:**
- With only 10 file slots, consolidate related content (e.g., combine SG/MY/HK clauses into one file)
- 100 MB per file is generous — file count (10) is the real constraint, not size
- Google Docs from Drive auto-update; local uploads are static snapshots
- Context window on current Gemini 3.x models: ~1M input tokens — ample for embedded gem context

**Sources:**
- [Tips for creating custom Gems — Gemini Apps Help](https://support.google.com/gemini/answer/15235603)
- [Supported file types & limits — Gemini Apps Help](https://support.google.com/gemini/answer/14903178)

## Markdown Files (.md now supported natively)

Upload `.md` files directly to a gem's knowledge base — Gemini ingests Markdown and uses its structure (`#` headers, lists, tables, bold) as semantic signal. **No `.md`→`.txt` conversion is required** (this reverses earlier guidance).

**Optional `.txt` fallback (legacy):** if a specific upload path ever rejects `.md`, copy to `.txt` without stripping syntax — the Markdown content stays identical and fully readable:
```bash
for f in *.md; do cp "$f" "${f%.md}.txt"; done   # keeps Markdown syntax inside
```

Either way, **keep the Markdown syntax** — `#`/`##` hierarchy, lists, and tables give the model structural information that improves comprehension.

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

## Refining Gem Instructions in the Builder (magic wand)

Gemini's gem builder has a **magic wand** icon at the bottom of the Instructions box that lets Gemini re-write and expand your draft instructions (confirmed current 2026-06 — [Google Gems tips](https://blog.google/products-and-platforms/products/gemini/google-gems-tips/)):
- Write a concise draft, then click the magic wand to have Gemini rewrite/expand it
- Treat it as a first-draft generator, not a final editor — review before saving; it can add hedges or generic lines you don't want
- Gemini 3.x prefers concise instructions, so trim rather than pad
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
