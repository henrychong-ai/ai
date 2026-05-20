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
| **Skill `.zip`** | CD-S | Upload `.zip` to Settings → Capabilities → Skills | Auto-activates on trigger phrases across every Claude.ai conversation; bundled files reach every consumer surface (Desktop, web, iOS, Android) via `/mnt/skills/user/<skill>/` | `~/.claude/skills-claude-desktop/<skill>.zip` |
| **Project Custom Instructions** (linked-skill only) | CD-P | Paste contents into a specific Claude Desktop Project → Custom Instructions field | Scoped to that Project; carries per-surface capability matrix; the skill's `references/cd-project-recipe.md` is emitted to the .md by `/instruction-creator` per `cd-project-bundle-guide.md` | `~/.claude/skills-claude-desktop/<skill>-project-instructions.md` (single file, side-by-side with `<skill>.zip`) |

**CD-S applies to every distributable skill.** **CD-P applies only to "linked skills"** — those with a paired Claude Desktop Project. Standalone skills need only CD-S. CD-only Projects (Claude Desktop Projects without a backing CC skill) are managed in the Claude Desktop GUI only and need no /instruction-creator artifacts.

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
- Coaching/methodology skills (pure knowledge content)
- Dietary frameworks and recipe skills
- Legal knowledge and templates
- Financial principles and structures
- Regulatory/compliance knowledge bases
- Financial analysis methodologies
- Marketing playbooks, brand voice files, content strategy

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
- Note-taking integrations - Require app-specific MCP servers (e.g. Obsidian, Things)
- Infrastructure skills - Require SSH, VPN, etc.

### Partially Portable Skills

Some skills have both portable knowledge AND non-portable tool dependencies:

**Strategy:** Create a "lite" version that extracts only the portable knowledge.

**Example:** a personal-health skill
- **Non-Portable:** Journal/MCP integrations, knowledge-graph domain queries, local scripts
- **Portable:** Dietary framework, condition protocols, biomarker targets
- **Solution:** Create a "lite" variant with just the knowledge content

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
name: cooking
description: This skill should be used for cooking, recipe, meal planning...
allowed-tools: Read, Grep, WebSearch
---
```

**AFTER (Claude.ai):**
```yaml
---
name: cooking
description: This skill should be used for cooking, recipe, meal planning...
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
Load `~/.claude/skills/cooking/references/recipes.md` for examples.

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
- **Tested sizes:** 25MB and 52MB zips have been created successfully — upload acceptance varies
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

## Conversion Methods

### Method 1: Manual Zip (Recommended for Batch)

Faster, no dependencies, handles symlinked skills. Excludes non-portable artifacts automatically.

```bash
OUTDIR="$HOME/.claude/skills-claude-desktop"

# Single skill (from parent directory to get wrapper folder)
cd ~/.claude/skills && zip -r "$OUTDIR/<skill-name>.zip" <skill-name> \
    -x "*/scripts/*" -x "*/.DS_Store" -x "*/__pycache__/*" -x "*.pyc"

# Symlinked skill (use the physical target path)
SRC="$HOME/path/to/skill-source-repo/skills"
cd "$SRC" && zip -r "$OUTDIR/<skill-name>.zip" <skill-name> \
    -x "*/scripts/*" -x "*/.DS_Store" -x "*/__pycache__/*" -x "*.pyc"

# Batch (multiple skills)
for skill in skill-a skill-b skill-c; do
    cd ~/.claude/skills && zip -r "$OUTDIR/$skill.zip" "$skill" \
        -x "*/scripts/*" -x "*/.DS_Store" -x "*/__pycache__/*" -x "*.pyc"
done
```

**Key:** Always `cd` to the **parent directory** before zipping so the skill name becomes the wrapper folder in the zip.

**Symlink handling:** If a skill in `~/.claude/skills/` is a symlink to a skill-source repo, `cd` to the physical target path before zipping.

### Method 2: Convert Script (Content Transformation)

Use when you need YAML field stripping (`allowed-tools` removal) and CC-specific content transformation.

```bash
# Single skill
uv run --with pyyaml python ~/.claude/skills/instruction-creator/scripts/convert_to_claudeai.py \
    ~/.claude/skills/<skill-name> \
    ~/.claude/skills-claude-desktop/

# Options: --dry-run, --verbose, --keep-tools, --inline-refs
```

**Note:** The convert script transforms content (strips CC-specific fields) but does not currently exclude `scripts/`, `.DS_Store`, or `__pycache__/`. For pure knowledge skills that don't need content transformation, Method 1 is simpler.

---

## Upload Process (CD-S Skills)

### Step 1: Generate Zip

See "Conversion Methods" above. Zips output to `~/.claude/skills-claude-desktop/`.

### Step 2: Upload to Claude.ai

1. Open Claude.ai (web) or Claude Desktop
2. Go to **Settings** (gear icon)
3. Navigate to **Custom Skills** section
4. Click **Upload** or drag-drop the zip file from `~/.claude/skills-claude-desktop/`
5. Verify skill appears in list

### Step 3: Verify Sync

Skills auto-sync across all Claude.ai platforms (Web, Desktop, iOS, Android) once uploaded to any one.

### Step 4: Test

Start a conversation and use a skill trigger phrase to verify activation.

---

## Project Setup (CD-P Projects)

For skills too large for zip upload or that benefit from scoped context.

### Step 1: Prepare Project Files

Copy/adapt SKILL.md and reference files to a working directory of your choice.

### Step 2: Create Project in Claude Desktop

1. Open Claude Desktop > Projects
2. Create new project
3. Add custom instructions (from SKILL.md content)
4. Attach reference files

### Step 3: Track in Manifest

Update distribution manifest with `CD-P: ✓` and project path.

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

## Appendix: Example Distribution Patterns

### CD-S (Skill Zips) — typical sizing

| Skill type | Typical Zip Size | Notes |
|-----------|------------------|-------|
| Markdown-only knowledge skill | < 100 KB | Ship as-is |
| Skill with a handful of reference PDFs | 1–10 MB | Comfortable upload size |
| Skill with many reference PDFs (e.g. policies, statutes) | 10–25 MB | Approaching the 30 MB cap — audit before adding more |
| Skill with very large PDF/media payload | > 30 MB | Cannot upload as a single .zip — see size-reduction strategies |

### CD-P (Projects)

CD-P is appropriate when a skill is too large for the 30 MB cap, when the user needs a scoped Project context, or when the skill backs a paired Claude Desktop Project that needs Custom Instructions text. See `cd-project-bundle-guide.md` for the v3 single-file recipe pattern.

### Not Recommended for CD-S (Non-Portable)

| Skill type | Reason |
|------------|--------|
| `pdf`, `xlsx`, `docx`, `pptx` | Require Python libraries |
| `git` | Requires git CLI + credentials |
| `images`, `ffmpeg` | Require CLI tools |
| Infrastructure skills | Require SSH, VPN, system access |

### Distribution Tracking

If you maintain a multi-repo distribution setup (e.g. local + team + public copies of skills), a manifest file in your `/git` skill can track CD-S / CD-T / CD-P status with stale-check on push.

---

*Last Updated: 2026-03-25*
*For use with instruction-creator skill*
