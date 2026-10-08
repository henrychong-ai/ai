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

### Two Distribution Mechanisms (Skill Zip vs Linked Project)

| Type | Method | Scope | Storage |
|------|--------|-------|---------|
| **Skill `.zip`** | Upload `.zip` to Settings → Capabilities → Skills | Auto-activates on trigger phrases across every Claude.ai conversation; bundled files reach every consumer surface (Desktop, web, iOS, Android) via `/mnt/skills/user/<skill>/` | `<output-dir>/<skill>.zip` (your packaging output directory; see `claude-desktop-packaging-guide.md`) |
| **Project Custom Instructions** (linked-skill only) | Paste contents into a specific Claude Desktop Project → Custom Instructions field | Scoped to that Project; carries per-surface capability matrix; the skill's `references/cd-project-recipe.md` is emitted to the .md by `/instruction-creator` per `cd-project-bundle-guide.md` | `<output-dir>/<skill>-project-instructions.md` (single file, side-by-side with `<skill>.zip`) |

**The skill zip applies to every distributable skill.** **Project Custom Instructions apply only to "linked skills"** — those with a paired Claude Desktop Project. Standalone skills need only the zip. Desktop-only Projects (Claude Desktop Projects without a backing CC skill) are managed in the Claude Desktop GUI only and need no /instruction-creator artifacts.

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

## Instruction Size Limits by Surface

Account-level instruction fields are the one place where a paste can fail *silently for the user and loudly for Claude*: the field accepts the text, and the sessions it feeds simply stop receiving instructions. Check the limit before every paste and every packaging run.

| Surface / field | Limit | Unit | Behaviour when exceeded | Status |
|---|---|---|---|---|
| Claude Desktop / claude.ai **Instructions for Claude** (Settings → General; the one account-level field — in the new Claude experience it includes the former Cowork "Global instructions" and applies to every conversation: Chat, Cowork, Dispatch) | **32,768** for the whole field | Unicode code points of the trimmed text | Treat as blocking. Desktop 2.x: *"These instructions are too long, so Claude might not use them. Shorten them to 32,768 characters or fewer."* Desktop 1.x: *"over the 32,768 allowed in Claude sessions. Claude won't use them until they're shorter"*. The app holds 32,768 as its default and accepts a server-served limit | Observed 2026-09-14 (Desktop 1.52386.6) and 2026-10-05 (2.19675.0); undocumented |
| Cowork **Global instructions** (Settings → Cowork) | shares the 32,768 above once merged | code points | In the new Claude experience the app imports this text into Instructions for Claude ("We brought your global instructions over from Cowork"), so two artefacts that each fit can exceed the cap together | Support article "Get started with Claude Cowork" + Desktop 2.19675.0, checked 2026-10-05; the separate field remains only for accounts not yet moved |
| Claude.ai Project custom instructions | not measured here | — | — | Check the field before relying on it |
| Skill `description` frontmatter | 1,024 | characters | Upload rejected with `field 'description' in SKILL.md must be at most 1024 characters` | Verified |
| Skill `.zip` upload (Desktop / Teams org skill) | 30 MB | bytes | Upload rejected | Verified (`claude-desktop-packaging-guide.md`) |
| Claude Code `CLAUDE.md` and `.claude/rules/*.md` | 4 MiB | bytes | A larger file is skipped; recommendation stays under 200 lines per file | Official docs |
| Claude Code auto-memory `MEMORY.md` | 200 lines or 25 KB | lines / bytes | Content past the threshold is not loaded | Official docs |

### How to measure

Count **Unicode code points of the trimmed text**, which is what the 32,768 check uses (Desktop 2.x evaluates `Array.from(text.trim()).length`), and count everything that will sit in the field: when a core artefact and a Cowork adapter share the field, add them together (a 40,021-code-point paste produced exactly the banner figure 40,021; its UTF-16 length was 40,063 and its byte length 40,631). `python3 -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read()))' FILE` is the reference measurement. `wc -c` reports bytes and over-counts every emoji, arrow, and em-dash; JavaScript `.length` over-counts astral-plane emoji.

### Derivation rule for paste fields

1. **Never hand-paste a master file.** A pasted copy has no sync path back to the master, so it rots the moment the master moves. Generate the paste artefact from the master by script and stamp it with the master's version.
2. **Split by what is true for every session versus what is true because of the tools.** Identity, interpretation rules, precedence, preferences, and conventions belong in the account-level field. Tool routing, MCP limits, filesystem paths, and credential mechanics belong in a harness section or in on-demand file pointers. Since the new Claude experience there is one field for Chat and Cowork, so write the harness part as a section of the same artefact and scope it by session kind ("in Cowork, where the local filesystem and MCP servers are available…"; "in Chat, with no local filesystem…"): a flat "you are running in Cowork" declaration is false in ordinary chats. Zero overlap between the core and the harness section: duplicated text is a token tax on every turn and over-steers frontier models.
3. **Assert the size of the whole field at generation time.** Target at most 90% of the cap (29,491 code points for a 32,768 field) so a normal release cadence does not re-trip the limit; fail the generation loudly when exceeded rather than trimming silently.
4. **Declare precedence with any co-loaded file.** If the same account also loads a project or user `CLAUDE.md` in some session types, state in both artefacts which one is canonical when both are present (Core Rule 3).
5. **When a field is already over the limit, cut in this order:** harness mechanics → reference material that a pointer can replace → long illustrative tables → prose framing. Cut whole sections, not sentences; a section trimmed to half its length usually loses its meaning while keeping its cost.

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
- Requires MCP servers (e.g. a knowledge graph, task manager, journal, or note-taking app)
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
- `references/*.pdf` files (manuals, guides — Claude can read PDFs)
- `templates/*.md` files (document templates)
- `templates/*.csv`, `*.json` (structured templates)
- `scripts/` when the skill needs them — Claude.ai runs bundled scripts in its code-execution sandbox (`convert_to_claudeai.py` keeps `scripts/`); leave out any script that depends on local-only tools, paths or credentials

**Exclude from zip (non-portable artifacts):**
- `.DS_Store` (macOS Finder metadata)
- `__pycache__/`, `*.pyc` (Python bytecode cache)
- Credentials or sensitive data

### Size Considerations

- **Individual file limit:** 30MB per file
- **Recommended total:** < 10MB for fast loading
- **Tested sizes:** 25MB and 52MB zips have been created successfully — upload acceptance varies
- **Very large skills (400MB+):** Use a Desktop Project instead of a skill zip
- **Large references:** Consider a Desktop Project for skills with many large PDFs

### Bundling Decision Matrix

| Content Type | Include? | Notes |
|--------------|----------|-------|
| Reference markdown | Yes | Core knowledge |
| Templates (md/csv/json) | Yes | Output patterns |
| PDFs (any size) | Yes | Claude can read PDFs in skills |
| Images (jpg/png) | Yes | Claude can view images |
| Python scripts | Yes, when needed | Run in Claude.ai's code-execution sandbox; must not depend on local-only tools, paths or credentials |
| `.DS_Store` | **No** | macOS metadata — non-portable |
| `__pycache__/` | **No** | Python cache — non-portable |
| API keys/credentials | **Never** | Security risk |

---

## Conversion Methods

### Method 1: Manual Zip (Recommended for Batch)

Faster, no dependencies, handles symlinked skills. Excludes non-portable artifacts automatically.

```bash
OUTDIR="<output-dir>"   # your packaging output directory

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

**A hand-built zip skips the packaging scripts' built-in checks** (single top-level folder, literal frontmatter, filename charset, 30 MB cap) and their exclusions (tool caches, database binaries, maintainer files). Run the manual checks in `claude-desktop-packaging-guide.md` before uploading, or use `package_skill.py` for a verbatim zip that is checked.

**Symlink handling:** If a skill in `~/.claude/skills/` is a symlink to a skill-source repo, `cd` to the physical target path before zipping.

### Method 2: Convert Script (Content Transformation)

Use when you need YAML field stripping (`allowed-tools` removal) and CC-specific content transformation.

```bash
# Single skill
uv run <ic>/scripts/convert_to_claudeai.py \
    <skills-dir>/<skill-name> \
    <output-dir>/
# <ic> = this skill's base directory; see claude-desktop-packaging-guide.md § Invocation patterns

# Options: --dry-run, --verbose, --keep-tools, --inline-refs, --team
```

**Note:** The convert script transforms content (strips CC-specific fields), excludes `.DS_Store`, `__pycache__/`, `*.pyc`, tool caches, database binaries, maintainer files (`TODO.md`, `README.md`, `CHANGELOG.md`), and anything listed in the skill's optional `.claudeai-exclude` file (full list: `claude-desktop-packaging-guide.md` § What the packagers leave out), and keeps `scripts/` (Claude.ai mounts the full skill and its code-execution tool can run them). For pure knowledge skills that don't need content transformation, Method 1 is simpler.

---

## Upload Process (Skill Zips)

### Step 1: Generate Zip

See "Conversion Methods" above. Zips output to `<output-dir>`.

### Step 2: Upload to Claude.ai

1. Open Claude.ai (web) or Claude Desktop
2. Go to **Settings** (gear icon)
3. Navigate to **Custom Skills** section
4. Click **Upload** or drag-drop the zip file from `<output-dir>`
5. Verify skill appears in list

### Step 3: Verify Sync

Skills auto-sync across all Claude.ai platforms (Web, Desktop, iOS, Android) once uploaded to any one.

### Step 4: Test

Start a conversation and use a skill trigger phrase to verify activation.

---

## Project Setup (Linked Desktop Projects)

For skills too large for zip upload or that benefit from scoped context.

### Step 1: Prepare Project Files

Copy/adapt SKILL.md and reference files to a working directory of your choice.

### Step 2: Create Project in Claude Desktop

1. Open Claude Desktop > Projects
2. Create new project
3. Add custom instructions (from SKILL.md content)
4. Attach reference files

### Step 3: Track the Link

If you keep a distribution manifest, record that the skill now has a paired Desktop Project, and scaffold the skill's `references/cd-project-recipe.md` per `cd-project-bundle-guide.md`.

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

### Skill Zips — typical sizing

| Skill type | Typical Zip Size | Notes |
|-----------|------------------|-------|
| Markdown-only knowledge skill | < 100 KB | Ship as-is |
| Skill with a handful of reference PDFs | 1–10 MB | Comfortable upload size |
| Skill with many reference PDFs (e.g. policies, statutes) | 10–25 MB | Approaching the 30 MB cap — audit before adding more |
| Skill with very large PDF/media payload | > 30 MB | Cannot upload as a single .zip — see size-reduction strategies |

### Desktop Projects

A linked Desktop Project is appropriate when a skill is too large for the 30 MB cap, when the user needs a scoped Project context, or when the skill backs a paired Claude Desktop Project that needs Custom Instructions text. See `cd-project-bundle-guide.md` for the v3 single-file recipe pattern.

### Not Recommended for Skill Zips (Non-Portable)

| Skill type | Reason |
|------------|--------|
| `pdf`, `xlsx`, `docx`, `pptx` | Require Python libraries |
| `git` | Requires git CLI + credentials |
| `images`, `ffmpeg` | Require CLI tools |
| Infrastructure skills | Require SSH, VPN, system access |

### Distribution Tracking

If you maintain a multi-repo distribution setup (e.g. local + team + public copies of skills), a manifest file can record, per skill, which targets it ships to (personal-plan zip, team-plan zip, linked Desktop Project) and whether each upload is current, with a stale check before you push.

---

*Last Updated: 2026-03-25*
*For use with instruction-creator skill*
