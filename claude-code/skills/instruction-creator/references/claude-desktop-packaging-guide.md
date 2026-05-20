# Claude Desktop Skill Zip Packaging Guide

Load this reference whenever packaging a **skill `.zip`** for upload to Claude Desktop / Claude.ai Settings → Capabilities → Skills.

**Scope:** skill zips ONLY. Project Knowledge bundles (which are directories, not zips) are handled separately by `cd-project-bundle-guide.md` — see that reference for Project bundle generation.

---

## Output Directory (MANDATORY)

**All Claude Desktop skill `.zip` uploads land in `~/.claude/skills-claude-desktop/`.** No exceptions — do not leave zips in `/tmp/`, the skill source directory, or anywhere else.

| Artefact | Output directory | Filename | Structure | Upload target |
|---|---|---|---|---|
| **Skill zip** | `~/.claude/skills-claude-desktop/` | `<skill-name>.zip` (bare) | Wrapper folder + `SKILL.md` | Settings → Capabilities → Skills |

`~/.claude/` is the standard Claude Code config directory on every user's machine, so this path is portable across machines — no per-user customisation required. Create the directory on first use if it doesn't yet exist.

Per-directory README documents the convention + structural requirements: `~/.claude/skills-claude-desktop/README.md`.

### Invocation patterns

```bash
# Skill zip (portable)
python3 ~/.claude/skills/instruction-creator/scripts/package_skill.py \
    ~/.claude/skills/<skill-name> \
    ~/.claude/skills-claude-desktop/

# Skill zip (CC-specific → sanitised for Claude.ai)
uv run --with pyyaml python ~/.claude/skills/instruction-creator/scripts/convert_to_claudeai.py \
    ~/.claude/skills/<skill-name> \
    ~/.claude/skills-claude-desktop/
```

For Project Custom Instructions emission (the `.md` paste file for a linked skill's paired Claude Desktop Project, co-located with the `.zip` in `~/.claude/skills-claude-desktop/`), see `cd-project-bundle-guide.md`.

---

## Filename Character Validation (MANDATORY)

Claude Desktop's upload validator rejects any zip path containing characters outside `[A-Za-z0-9._-/]` with the error **"Zip file contains path with invalid characters"**. Forbidden: spaces, apostrophes (smart `'` U+2019 AND ASCII `'`), em/en-dashes, parentheses, all other punctuation and non-ASCII bytes.

**Rename bundled files to kebab-case before packaging.** Then update SKILL.md `Read references/...` paths to match.

Pre-zip check (run against source dir):

```bash
find ~/.claude/skills/<name> -type f | LC_ALL=C grep -P '[^A-Za-z0-9._\-/]' && echo "FIX FILENAMES" || echo "OK"
```

Post-zip check (run against output zip):

```bash
python3 -c "
import zipfile
with zipfile.ZipFile('<zip-path>') as z:
    p = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/')
    [print(f'BAD: {i.filename!r}') for i in z.infolist() if set(i.filename) - p] or print('CLEAN')
"
```

Real-world bite (2026-05-20): `islamic-finance` rejected on upload — 6 PDFs had spaces, 1 had a smart-quote apostrophe, 1 had an ASCII apostrophe. Fix required kebab-casing all 7 + updating 5 SKILL.md path refs. Future enhancement: bake this check into `convert_to_claudeai.py` so it fails locally instead of at upload.

---

## 30 MB Upload Limit (MANDATORY)

**All Claude Desktop .zip skill uploads must be strictly under 30 MB total.**

Skills exceeding 30 MB will fail to upload. This applies to BOTH:
- **CD-S** (Henry's individual Claude Max plan)
- **CD-T** (Fusang Claude Teams plan)

### Implications for Skill Packaging

Before zipping for Claude Desktop, audit the skill contents:

```bash
du -sh ~/.claude/skills/<skill-name>/         # Total disk usage
find ~/.claude/skills/<skill-name>/ -type f -name "*.pdf" -exec du -h {} \; | sort -h  # Find large PDFs
```

If the skill folder exceeds 30 MB, reduce it before packaging via `package_skill.py`. Options:

| Strategy | When to Use |
|---|---|
| **Remove PDFs** | The skill content is mostly markdown — PDFs are reference-only and rarely loaded into context. Strip and link to source URLs instead. |
| **Convert PDFs to .md extracts** | The PDF content is high-value for context loading — extract substantive sections to markdown (smaller; also parseable). See `compliance` skill's `references/statutes/` pattern. |
| **Split into core + extras** | Create `<skill>-core.zip` (markdown only, <30MB) for general use + `<skill>-references.zip` (PDFs) for users who need source documents. |
| **Strip media** | Remove image / video / audio assets if not essential to the skill's reasoning. |
| **Compress images** | If images are essential, use `cwebp` / `pngquant` / `magick mogrify` to reduce file sizes before packaging. |

### Pre-Upload Verification

Always check zip size before attempting upload:

```bash
ls -lh /path/to/skill.zip
# Output should show size <30MB:
# -rw-r--r--  1 user  staff   28M  ...  skill.zip   ✅
# -rw-r--r--  1 user  staff   62M  ...  skill.zip   ❌ Will fail upload
```

### Real-World Examples (2026-05-13)

| Skill | Initial Zip Size | Status | Required Action |
|---|---|---|---|
| `compliance.zip` | 62 MB | ❌ Over limit | Split: ship .md content + 9 statute extracts under one zip; relocate 41 regulator PDFs to a separate distribution |
| `fusang.zip` | 52 MB | ❌ Over limit | Strip strategy/product/market/commercial PDFs from CD-S/CD-T copy; keep markdown body |
| `portcullis.zip` | 35 KB | ✅ Well under | Ship as-is — markdown-only skill |

**Convention**: When a skill folder grows past 30 MB total, fork a `<skill>-references-pdf/` directory inside the skill (still distributed via Fusang AI repo for git access), but exclude it from `package_skill.py` for Claude Desktop zipping. Document in the skill's TODO.md.
