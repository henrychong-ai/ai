# Cross-Platform Skill Conversion Guide

Convert Claude Code skills to the Claude.ai ecosystem (Desktop, iOS, Android, Web).

---

## Overview

### Platform Ecosystem

Claude skills exist in two separate ecosystems:

```
┌─────────────────────────────────────────────────────────┐
│                CLAUDE.AI ECOSYSTEM                       │
│         (Auto-syncs across all platforms)                │
│                                                          │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│   │  Web    │  │ Desktop │  │   iOS   │  │ Android │   │
│   │claude.ai│  │  App    │  │   App   │  │   App   │   │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
│         ▲           ▲            ▲            ▲         │
│         └───────────┴────────────┴────────────┘         │
│                    Cloud Sync                            │
└─────────────────────────────────────────────────────────┘
                          │
                   [CONVERSION GAP]
                          │
┌─────────────────────────────────────────────────────────┐
│                  CLAUDE CODE                             │
│              (Filesystem-based)                          │
│                                                          │
│              ~/.claude/skills/                           │
│                                                          │
│   • Full Bash access        • MCP servers                │
│   • Filesystem operations   • Local tool execution       │
│   • Python/Node scripts     • System integration         │
└─────────────────────────────────────────────────────────┘
```

### Key Insight

**Once a skill is uploaded to ANY Claude.ai platform, it syncs to ALL Claude.ai platforms automatically.**

The only conversion needed is: **Claude Code → Claude.ai**

### Two Distribution Mechanisms (CD-S vs CD-P)

| Type | Label | Method | Scope | Storage |
|------|-------|--------|-------|---------|
| **Skills** | CD-S | Upload `.zip` to Settings > Custom Skills | Auto-activate on trigger phrases across all conversations | `~/.claude/claude-desktop-skills/` |
| **Project Knowledge bundles** | CD-P | Upload directory contents to a specific Project's Knowledge panel | Scoped to one Project; per-skill `references/cd-project-recipe.md` materialised by `/instruction-creator` per `cd-project-bundle-guide.md` | `~/.claude/claude-desktop-projects/<project>/` (directory, not zip) |

**Use CD-S when:** Skill is knowledge-only, moderate size (< 30MB), should activate globally.
**Use CD-P when:** Skill has large reference files (PDFs, etc.), needs scoped context, or exceeds zip size limits.

### DXT/MCPB Extensions (Separate System)

DXT (now MCPB) extensions are for bundling **MCP servers** into Claude Desktop — not for knowledge/skills. They use `manifest.json` + server code, created via `mcpb init` / `mcpb pack`. Do not confuse with skill zips.

---

## Platform Comparison Matrix

| Feature | Claude Code | Claude.ai Web | Claude Desktop | Claude iOS/Android |
|---------|-------------|---------------|----------------|-------------------|
| **Skill Location** | `~/.claude/skills/` | Cloud (Settings) | Cloud (Settings) | Cloud (Settings) |
| **Upload Method** | Filesystem | Zip upload | Zip upload | Auto-sync from web |
| **Cross-Device Sync** | None | Auto | Auto | Auto |
| **Bash Execution** | Full | None | None | None |
| **MCP Servers** | Full | None | Limited (Extensions) | None |
| **Filesystem Access** | Full | Sandboxed | Sandboxed | None |
| **Python/Node** | Full | Sandboxed (Code Execution) | Sandboxed | Sandboxed |
| **Local Tools** | Full (git, ffmpeg, etc.) | None | None | None |

---

## Skill Portability Classification

### Portable Skills (Convert These)

Skills that rely primarily on **knowledge and methodology** rather than tool execution:

**Characteristics:**
- No `allowed-tools` restrictions, OR only uses: `Read`, `WebSearch`, `Grep`, `Glob`
- No MCP tool references (`mcp__*`)
- No Bash command execution
- No local file path dependencies
- Knowledge-based content (frameworks, methodologies, reference data)

**Examples of Portable Skills:**
- `legal-harvey-ai` - Legal knowledge and templates
- `islamic-finance` - Financial principles and structures
- `compliance` - Regulatory knowledge
- `analyzing-financial-statements` - Financial analysis methodology
- `content-marketer` - Content creation frameworks
- Any pure-methodology or pure-reference skill with no tool execution

### Non-Portable Skills (Claude Code Only)

Skills that **require local tool execution**:

**Characteristics:**
- Uses Bash commands (git, ffmpeg, python, etc.)
- Requires MCP servers (KG, Things, DayOne, Obsidian)
- Depends on filesystem operations
- Executes Python/Node scripts locally
- References local paths that won't exist on Claude.ai

**Examples of Non-Portable Skills:**
- `pdf` - Requires Python libraries (pypdf, pdfplumber)
- `xlsx` - Requires openpyxl, LibreOffice
- `git` - Requires git CLI
- `images` - Requires ImageMagick
- `ffmpeg` - Requires ffmpeg CLI
- `obsidian` - Requires Obsidian MCP server
- `things` - Requires Things MCP server
- `infrastructure` - Requires SSH, system access

### Partially Portable Skills

Some skills have both portable knowledge AND non-portable tool dependencies:

**Strategy:** Create a "lite" version that extracts only the portable knowledge.

**Example:** A health/wellness skill that combines portable knowledge with local tool dependencies
- **Non-Portable:** Personal-data MCP servers (journal apps, knowledge graph queries against private nodes), local scripts
- **Portable:** Reference protocols, methodology frameworks, generic checklists
- **Solution:** Create a `*-lite` variant that exposes only the portable knowledge layer

---

## Conversion Rules

### YAML Frontmatter Transformation

**Remove these fields:**
```yaml
# REMOVE - Claude Code specific
allowed-tools: Read, Grep, Glob, Bash, WebSearch
```

**Keep these fields:**
```yaml
# KEEP - Universal
name: skill-name
description: This skill should be used when...
```

**Optional - Add platform metadata:**
```yaml
# OPTIONAL - For documentation
platforms: [claude-ai, claude-desktop, claude-ios]
```

### Before/After Example

**BEFORE (Claude Code):**
```yaml
---
name: legal-harvey-ai
description: This skill should be used for legal research, contract drafting...
allowed-tools: Read, Grep, WebSearch
---
```

**AFTER (Claude.ai):**
```yaml
---
name: legal-harvey-ai
description: This skill should be used for legal research, contract drafting...
---
```

---

## Content Transformation Rules

### 1. MCP Tool References

**Remove or convert:**
```markdown
# BEFORE (CC)
Use `mcp__kg__semantic_search("query")` to find entities.
Use `mcp__things__get_projects()` to list projects.

# AFTER (Claude.ai)
[Remove entirely - MCP not available]
OR
Search the knowledge graph for relevant entities.
List your current projects.
```

### 2. Bash/CLI Examples

**Remove or generalize:**
```markdown
# BEFORE (CC)
Run the conversion:
```bash
python scripts/convert.py input.pdf output.md
```

# AFTER (Claude.ai)
[Remove - local execution not available]
OR
Convert the PDF to markdown format.
```

### 3. File Path References

**Convert to bundled content or remove:**
```markdown
# BEFORE (CC)
See `references/dietary-framework.md` for complete food lists.
Load `~/.claude/skills/legal-harvey-ai/references/templates.md` for examples.

# AFTER (Claude.ai)
See the Dietary Framework section below for complete food lists.
[Content bundled inline or in zip]
```

### 4. Tool Invocation Patterns

**Remove CC-specific patterns:**
```markdown
# BEFORE (CC)
Use the Read tool to examine the file.
Execute with Bash(python script.py).
Search using Grep for the pattern.

# AFTER (Claude.ai)
Examine the file content.
[Remove execution reference]
Search for the pattern.
```

### 5. Script References

**Remove or document alternative:**
```markdown
# BEFORE (CC)
Run `scripts/calculate_ratios.py` with the financial data.

# AFTER (Claude.ai)
Calculate the financial ratios using the formulas below:
[Include formulas inline]
```

---

## Reference Bundling Strategy

### What to Bundle

**Include in zip:**
- `SKILL.md` (required, converted)
- `references/*.md` files (knowledge content)
- `references/*.pdf` files (insurance docs, guides — Claude can read PDFs)
- `templates/*.md` files (document templates)
- `templates/*.csv`, `*.json` (structured templates)

**Exclude from zip (non-portable artifacts):**
- `scripts/` directory (Python/shell — won't execute on Claude.ai)
- `.DS_Store` (macOS Finder metadata)
- `__pycache__/`, `*.pyc` (Python bytecode cache)
- Credentials or sensitive data

### Size Considerations

- **Individual file limit:** 30MB per file
- **Recommended total:** < 10MB for fast loading
- **Tested sizes:** Zips up to ~50MB have been successfully created — upload acceptance varies
- **Very large skills (400MB+):** Use CD-P (Project) instead of CD-S (Skill zip)
- **Large references:** Consider CD-P for skills with many large PDFs

### Bundling Decision Matrix

| Content Type | Include? | Notes |
|--------------|----------|-------|
| Reference markdown | Yes | Core knowledge |
| Templates (md/csv/json) | Yes | Output patterns |
| PDFs (any size) | Yes | Claude can read PDFs in skills |
| Images (jpg/png) | Yes | Claude can view images |
| Python scripts | **No** | Won't execute — non-portable |
| `.DS_Store` | **No** | macOS metadata — non-portable |
| `__pycache__/` | **No** | Python cache — non-portable |
| API keys/credentials | **Never** | Security risk |

---

## Conversion Script Usage

### Basic Usage

```bash
# Convert a single skill
uv run --with pyyaml python ~/.claude/skills/instruction-creator/scripts/convert_to_claudeai.py \
    ~/.claude/skills/<skill-name> \
    ~/.claude/claude-desktop-skills/

# Output: ~/.claude/claude-desktop-skills/<skill-name>.zip
```

### Batch Conversion

```bash
# Convert multiple skills
for skill in legal-harvey-ai islamic-finance compliance; do
    uv run --with pyyaml python ~/.claude/skills/instruction-creator/scripts/convert_to_claudeai.py \
        ~/.claude/skills/$skill \
        ~/.claude/claude-desktop-skills/
done
```

### Script Options

```bash
uv run --with pyyaml python convert_to_claudeai.py <skill_path> <output_dir> [options]

Options:
  --dry-run        Show what would be converted without writing
  --verbose        Show detailed conversion steps
  --keep-tools     Keep allowed-tools field (not recommended)
  --inline-refs    Inline all reference content into SKILL.md
```

---

## Upload Process

### Step 1: Generate Zip

```bash
uv run --with pyyaml python convert_to_claudeai.py ~/.claude/skills/<skill-name> ~/.claude/claude-desktop-skills/
# Creates: ~/.claude/claude-desktop-skills/<skill-name>.zip
```

### Step 2: Upload to Claude.ai

1. Open Claude.ai (web) or Claude Desktop
2. Go to **Settings** (gear icon)
3. Navigate to **Capabilities** or **Features**
4. Find **Custom Skills** section
5. Click **Upload** or drag-drop the zip file
6. Verify skill appears in list

### Step 3: Verify Sync

1. Open Claude iOS or Android app
2. Check Settings > Skills
3. Verify uploaded skill appears
4. Test with a trigger phrase

### Step 4: Test Functionality

Start a conversation and use a skill trigger:
```
User: Help me draft a non-disclosure agreement for a vendor relationship
Claude: [Should activate legal-harvey-ai skill and apply contract templates]
```

---

## Zip Structure Requirements

### Valid Structure

```
skill-name.zip
└── skill-name/
    ├── SKILL.md           # Required
    └── references/        # Optional
        ├── guide.md
        └── templates.md
```

### Common Mistakes

```
# WRONG: Files at root level
skill.zip
├── SKILL.md
└── references/

# WRONG: Missing SKILL.md
skill.zip
└── skill-name/
    └── references/

# WRONG: Wrong file name
skill.zip
└── skill-name/
    └── skill.md  # Must be SKILL.md (uppercase)
```

---

## Troubleshooting

### Skill Not Activating

**Symptoms:** Uploaded skill doesn't trigger on expected phrases.

**Solutions:**
1. Verify `name` field matches expected trigger
2. Check `description` contains trigger keywords
3. Ensure SKILL.md is in correct location in zip
4. Try more explicit trigger: "use skill [name]"

### Skill Shows Errors

**Symptoms:** Error message when skill loads.

**Solutions:**
1. Check YAML frontmatter syntax (valid YAML)
2. Remove any `allowed-tools` field
3. Ensure no broken file references
4. Validate markdown formatting

### Description Too Long (Upload Validation Failure)

**Symptoms:** Upload rejected with `field 'description' in SKILL.md must be at most 1024 characters`.

**Cause:** Claude Desktop validates description length on upload. Limit is **1024 characters** (target: 1–2 lines of dense content). CC-only skills often accumulate longer descriptions over time because no equivalent validation runs locally.

**Solutions:**
1. Count current length:
   ```bash
   awk '/^description:/{sub(/^description: /,""); desc=$0; while ((getline line) > 0 && line !~ /^[a-z-]+:/ && line !~ /^---$/) desc = desc " " line; print "Length:", length(desc); exit}' SKILL.md
   ```
2. Trim techniques (preserve trigger terms — they drive auto-invocation):
   - Replace "including A, B, C" with "(A, B, C)"
   - Collapse repeated verbs: "creating/updating agents, creating/updating skills" → "creating/updating agents/skills"
   - Drop fillers: "optimal", "complex", "and" before final list item
   - Remove duplicate trigger phrases (e.g. drop `"effort level"` if `"effort"` is already in the list — superstring matching covers it)
3. Re-zip and re-upload. No validation runs in Claude Code, so the Claude Desktop upload step is the only gate.

### Content Not Available

**Symptoms:** Skill activates but can't access reference content.

**Solutions:**
1. Verify references included in zip
2. Check file paths in SKILL.md match actual files
3. Consider inlining critical content
4. Reduce file sizes if exceeding limits

### Sync Not Working

**Symptoms:** Skill on Desktop but not on iOS.

**Solutions:**
1. Ensure same account logged in on both
2. Wait a few minutes for sync
3. Force refresh by logging out/in
4. Check Claude.ai web to verify upload succeeded

---

## Appendix: Portable Skill Checklist

Before converting, verify:

- [ ] No `mcp__*` tool references in content
- [ ] No Bash command examples that are essential
- [ ] No local file path dependencies
- [ ] No script execution requirements
- [ ] All critical knowledge is in markdown files
- [ ] References are under 10MB total
- [ ] No sensitive data (credentials, personal info)
- [ ] Skill provides value without tool execution

---

## Appendix: Recommended Skills for Conversion

Based on analysis of common Claude Code skills:

### Priority 1 (High Value, Easy Conversion)

| Skill | Conversion Effort | Mobile Value |
|-------|-------------------|--------------|
| legal-harvey-ai | Low | High |
| islamic-finance | Minimal | High |
| compliance | Low | High |
| content-marketer | Minimal | High |
| analyzing-financial-statements | Low | High |

### Priority 2 (Moderate Value)

| Skill | Conversion Effort | Mobile Value |
|-------|-------------------|--------------|
| analyzing-financial-statements | Minimal | Medium |
| creating-financial-models | Minimal | Medium |
| content-marketer | Minimal | High |
| travel | Low (sanitize personal data) | Very High |

### Not Recommended (Non-Portable)

| Skill | Reason |
|-------|--------|
| pdf, xlsx, docx, pptx | Require Python libraries |
| git | Requires git CLI |
| images, ffmpeg | Require CLI tools |
| obsidian, things | Require MCP servers |
| infrastructure, devops | Require SSH, system access |

---

*Last Updated: 2026-01-06*
*For use with instruction-creator skill*
