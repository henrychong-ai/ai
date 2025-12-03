# YAML Frontmatter Complete Guide

**Comprehensive reference for all instruction file YAML frontmatter fields**

---

## Agent Front Matter

**Location:** `~/.claude/agents/*.md`

**Required Fields:**
```yaml
---
name: agent-name                    # Required: kebab-case identifier
description: Brief description...   # Required: specialization + when to use
model: sonnet-4.5                   # Required: claude model version
---
```

**Field Specifications:**

### `name` (Required)
- **Format:** kebab-case (lowercase with hyphens)
- **Purpose:** Agent identifier, must match filename
- **Examples:** `compliance-officer`, `typescript`, `things`
- **Rules:** No spaces, no underscores, descriptive

### `description` (Required)
- **Format:** Single paragraph, 1-3 sentences
- **Purpose:** Agent capabilities and when to use
- **Include:** Specialization, use cases, proactive guidance
- **Pattern:** "[Specialization]. [Capabilities]. Use PROACTIVELY for [triggers]."
- **Examples:**
  - `"TypeScript specialist with advanced type system mastery. Use PROACTIVELY for fintech TypeScript optimization."`
  - `"Compliance expert for regulatory requirements. Use PROACTIVELY for compliance queries."`

### `model` (Required)
- **Format:** Model identifier string (aliases or full IDs)
- **Purpose:** Specifies Claude model to use for agent execution
- **Recommended:** Use aliases for automatic version updates

**Model Aliases** (recommended):
- `opus` - Latest Opus model (strategic analysis, compliance, legal, complex multi-step reasoning)
- `sonnet` - Latest Sonnet model (code development, technical tasks, balanced capability) **[DEFAULT]**
- `haiku` - Latest Haiku model (fast operations, simple tasks, speed-optimized)

**Full Model IDs** (version-specific):
- `claude-opus-4-5` - Opus 4.5 (specific version)
- `claude-sonnet-4-5` - Sonnet 4.5 (specific version)
- `claude-haiku-4-5` - Haiku 4.5 (specific version)

**Priority Order** (highest to lowest):
1. **Task tool `model` parameter** - Explicit override at invocation time
2. **Agent YAML `model` field** - Default specified in agent file
3. **Inherit from parent** - If neither specified, inherits from calling conversation
4. **System default** - Sonnet 4.5 if nothing else specified

**Built-in Agent Defaults**:
- Explore: `haiku` (fast searches and information gathering)
- Plan: `sonnet` (capable analysis and planning)
- General-Purpose: `sonnet` (complex reasoning and execution)
- claude-code-guide: `haiku` (quick documentation lookups)

**Model Selection Guidance**:
- **Use `opus`**: Strategic analysis, regulatory compliance, legal review, complex architectural decisions requiring deep multi-step reasoning
- **Use `sonnet`**: Code development, technical tasks, general problem-solving, balanced capability (recommended default for most agents)
- **Use `haiku`**: Fast operations, simple tasks, quick lookups, speed-optimized workflows

**Best Practices**:
- **Use aliases** (`opus`, `sonnet`, `haiku`) not version numbers - aliases automatically use latest model version
- **No maintenance needed** - aliases update automatically when new model versions released
- **Choose based on complexity** - match model capability to task requirements
- **Team agents** - consider using `sonnet` as default for broader accessibility (Pro plan users lack Opus access)

**Override at Invocation** (Task tool example):
```xml
<invoke name="Task">
  <parameter name="subagent_type">my-agent</parameter>
  <parameter name="model">haiku</parameter>  <!-- Overrides agent's default -->
  <parameter name="prompt">Task description</parameter>
</invoke>
```

**Accessibility Considerations**:
- **Pro plan users** - Cannot access Opus models
- **Fallback behavior** - If agent specifies `model: opus` but user lacks access, fallback behavior may be inconsistent (may error or fallback to Sonnet)
- **Team agents** - For shared/team agents, use `sonnet` as default to ensure broad accessibility across all plan types

---

## Skill Front Matter

**Location:** `~/.claude/skills/*/SKILL.md`

**Required Fields:**
```yaml
---
name: skill-name                    # Required: kebab-case identifier
description: This skill should...   # Required: third-person usage description
---
```

**Field Specifications:**

### `name` (Required)
- **Format:** kebab-case (lowercase with hyphens)
- **Purpose:** Skill identifier, matches parent directory name
- **Examples:** `pdf`, `xlsx`, `travel`, `instruction-creator`
- **Rules:** No spaces, no underscores, descriptive

### `description` (Required)
- **Format:** Third-person voice, 1-3 sentences
- **Purpose:** What skill does and when to use it
- **Pattern:** "This skill should be used when [use cases]. [Capabilities]. [Special triggers]."
- **Examples:**
  - `"This skill should be used when creating or reviewing Claude instruction files. Expert guidance on CCUP architecture."`
  - `"This skill should be used when working with PDFs for extraction, creation, merging, or form handling."`
- **Voice:** Always third-person (not "Use this skill...")

---

## Slash Command Front Matter

**Location:** `~/.claude/commands/*.md`

**All Fields Optional** (organizational metadata only)

**Optional Fields:**
```yaml
---
allowed-tools: Tool(specific-commands)  # Optional: restrict tool access
argument-hint: [format]                 # Optional: guide argument format
description: Brief command purpose      # Optional: command description
model: sonnet-4.5                       # Optional: specific model
---
```

**Field Specifications:**

### `allowed-tools` (Optional)
- **Format:** Tool name pattern string
- **Purpose:** Restricts which tools command can use
- **Examples:**
  - `"Tool(read, write)"` - Only Read and Write tools
  - `"Tool(bash:git)"` - Only git bash commands
  - `"Tool(mcp__kg)"` - Only KG MCP tools
- **Use When:** Security or scope restriction needed

### `argument-hint` (Optional)
- **Format:** Free-text hint string
- **Purpose:** Guide users on expected argument format
- **Examples:**
  - `"[city]"` - Single city name expected
  - `"[file.pdf]"` - PDF file path expected
  - `"[query] or leave empty"` - Query or no args
- **Display:** Shown in command help/autocomplete

### `description` (Optional)
- **Format:** Brief sentence describing command purpose
- **Purpose:** Organizational metadata for command listing
- **Examples:**
  - `"Search knowledge graph for entities"`
  - `"Generate PRD for project"`
  - `"Sync configuration files across platforms"`

### `model` (Optional)
- **Format:** Model identifier string
- **Purpose:** Override default model for command
- **Recommended:** `sonnet-4.5`
- **Use When:** Specific model requirements (cost, speed, capability)

---

## Project Instructions Front Matter

**Location:** Project root or docs directory

**Recommended Fields:**
```yaml
---
file_type: project_instructions     # Type identifier
version: 1.0                         # Semantic version
last_updated: YYYY-MM-DD            # Last modification date
platform_compatibility: both        # desktop | code | both
business_domain: domain_name        # Business area
token_estimate: ~4000               # Approximate token count
---
```

**Field Specifications:**

### `file_type` (Recommended)
- **Format:** String identifier
- **Purpose:** Categorize instruction file type
- **Options:** `project_instructions`, `project_index`, `global_ccup`
- **Use:** Organization and tooling support

### `version` (Recommended)
- **Format:** Semantic version (X.Y or X.Y.Z)
- **Purpose:** Track instruction file evolution
- **Pattern:** Major.Minor.Patch
- **Example:** `1.0`, `2.1`, `3.5.2`

### `last_updated` (Recommended)
- **Format:** YYYY-MM-DD
- **Purpose:** Track modification date
- **Example:** `2025-10-28`

### `platform_compatibility` (Recommended)
- **Format:** String enum
- **Purpose:** Indicate which Claude platforms supported
- **Options:** `desktop`, `code`, `both`
- **Use:** Platform-specific optimization guidance

### `business_domain` (Recommended)
- **Format:** Domain identifier string
- **Purpose:** Categorize business area
- **Examples:** `fintech`, `healthcare`, `compliance`, `ecommerce`

### `token_estimate` (Recommended)
- **Format:** Approximate token count (~N)
- **Purpose:** Performance planning and optimization
- **Example:** `~4000`, `~6000`
- **Guidance:** Round to nearest 1000

---

## Field Validation Rules

### Name Fields
- **Must:** Use kebab-case only
- **Must:** Be descriptive and unique
- **Must:** Match filename/directory name
- **Must Not:** Contain spaces or underscores
- **Must Not:** Use special characters except hyphens

### Description Fields
- **Must:** Be clear and concise (1-3 sentences)
- **Must:** Explain when to use (agents: "Use PROACTIVELY", skills: third-person)
- **Must:** Be specific about capabilities
- **Must Not:** Be vague or generic
- **Must Not:** Exceed ~200 words

### Model Fields
- **Must:** Use valid model identifier
- **Should:** Default to `sonnet-4.5` for new files
- **Must Not:** Use deprecated model names
- **Must Not:** Leave empty if field included

---

## Common Patterns

### Agent Proactive Description
```yaml
description: [Specialization]. [Key capabilities]. Use PROACTIVELY for [trigger patterns]. [Notable features].
```

**Example:**
```yaml
description: TypeScript fintech specialist with advanced type system mastery. React, Vue, API, microservices. Use PROACTIVELY for fintech TypeScript optimization, type-safe trading systems, advanced type patterns.
```

### Skill Third-Person Description
```yaml
description: This skill should be used when [use cases]. [Capabilities summary]. [Special notes if any].
```

**Example:**
```yaml
description: This skill should be used when creating or reviewing Claude instruction files. Expert guidance on CCUP architecture, YAML frontmatter, agent-vs-skill decisions, and instruction best practices.
```

### Command Description
```yaml
description: [Action verb] [object] [purpose/outcome]
```

**Example:**
```yaml
description: Search knowledge graph for entities and relations
```

---

## Model Configuration Examples

### Strategic Agent (Opus)
```yaml
---
name: compliance-officer
description: Regulatory compliance specialist for digital securities. Use PROACTIVELY for compliance queries.
model: opus  # Complex multi-step regulatory reasoning
---
```

### Technical Agent (Sonnet - Recommended Default)
```yaml
---
name: typescript-specialist
description: TypeScript fintech development expert. Use PROACTIVELY for type-safe trading systems.
model: sonnet  # Balanced capability for code development
---
```

### Fast Operations Agent (Haiku)
```yaml
---
name: quick-lookup
description: Fast documentation and reference lookup specialist. Use PROACTIVELY for quick answers.
model: haiku  # Speed-optimized for simple tasks
---
```

### Task Tool Override Example
```xml
<!-- Agent default: sonnet, but override to haiku for quick task -->
<invoke name="Task">
  <parameter name="subagent_type">typescript-specialist</parameter>
  <parameter name="model">haiku</parameter>
  <parameter name="prompt">Quick syntax check for interface definition</parameter>
</invoke>
```

---

## Validation Checklist

**For Agents:**
- ✅ name: kebab-case, matches filename
- ✅ description: includes specialization + "Use PROACTIVELY" + triggers
- ✅ model: Use aliases (`opus`, `sonnet`, `haiku`) not version numbers

**For Skills:**
- ✅ name: kebab-case, matches directory name
- ✅ description: third-person voice, explains when to use

**For Commands:**
- ✅ All fields optional (YAML frontmatter is metadata only)
- ✅ If included: properly formatted per specifications

**For All:**
- ✅ Valid YAML syntax (proper indentation, quoting)
- ✅ No duplicate fields
- ✅ No typos in field names
- ✅ Proper date formats (YYYY-MM-DD)

---

**Last Updated:** 2025-10-28
**Use Case:** Complete reference for all YAML frontmatter fields and formats
