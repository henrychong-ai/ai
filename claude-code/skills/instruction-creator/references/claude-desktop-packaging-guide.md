# Claude Desktop Skill Zip Packaging Guide

Load this reference whenever packaging a **skill `.zip`** for upload to Claude Desktop / Claude.ai Settings → Capabilities → Skills.

**Scope:** skill zips ONLY. Project Custom Instructions (a single paste-ready `.md` file, not a zip) are handled separately by `cd-project-bundle-guide.md`.

---

## Output Directory

**Build every Claude Desktop skill `.zip` into one dedicated output directory of your choosing** — referred to as `<output-dir>` throughout this skill (for example `dist/claude-desktop/` in a skills repo, or a folder under your home directory). Keep zips out of the skill source directory so they are never committed or re-bundled, and out of throwaway locations such as `/tmp/` so the latest upload artefact stays findable.

| Artefact | Output directory | Filename | Structure | Upload target |
|---|---|---|---|---|
| **Skill zip** | `<output-dir>/` | `<skill-name>.zip` (bare) | Wrapper folder + `SKILL.md` | Settings → Capabilities → Skills |

Create the directory on first use if it doesn't yet exist.

### Invocation patterns

**Prerequisite: [uv](https://docs.astral.sh/uv/)** (macOS, Linux, Windows). `convert_to_claudeai.py` and `quick_validate.py` need PyYAML and declare it in a PEP 723 header, so `uv run <script>` supplies it with no install step. Started any other way (plain `python3`, or as a subprocess of another script) they re-run themselves once through uv (`scripts/_script_deps.py`); without uv they exit with the fix. Never `pip install` into a system or Homebrew Python.

**Paths:** `<ic>` below is this skill's base directory — Claude Code states it when the skill loads (for a personal install, `~/.claude/skills/instruction-creator`). `<skills-dir>` is wherever the skill sources live (`~/.claude/skills/`, or a skills repo's skill directory). Scripts locate their siblings relative to themselves, so no path is hardcoded.

```bash
# Skill zip (portable)
python3 <ic>/scripts/package_skill.py \
    <skills-dir>/<skill-name> \
    <output-dir>/

# Skill zip (CC-specific → sanitised for Claude.ai)
uv run <ic>/scripts/convert_to_claudeai.py \
    <skills-dir>/<skill-name> \
    <output-dir>/
```

For Project Custom Instructions emission (the `.md` paste file for a linked skill's paired Claude Desktop Project, co-located with the `.zip` in `<output-dir>`), see `cd-project-bundle-guide.md`.

#### Built-in name collisions (rename in three places)

Claude ships **built-in skills** (for example `brand-guidelines`), and an upload whose skill name matches one is rejected. A skill with a colliding name must be renamed in all three places — the `.zip` filename, its wrapper folder, and the SKILL.md `name:` frontmatter. The scripts name the folder and zip from the source directory name and preserve the frontmatter `name:`, so build from a renamed temporary copy:

```bash
# 1. temp copy whose dir name IS the new skill name (-L resolves symlinks)
STAGE="$(mktemp -d)" && cp -RL <skills-dir>/<skill-name> "$STAGE/<new-name>"
# 2. rewrite the frontmatter name field (-i.bak works with both BSD and GNU sed)
sed -i.bak 's/^name: <skill-name>$/name: <new-name>/' "$STAGE/<new-name>/SKILL.md" && rm "$STAGE/<new-name>/SKILL.md.bak"
# 3. sanitise + zip → <new-name>.zip (folder + zip + internal name all match)
uv run <ic>/scripts/convert_to_claudeai.py "$STAGE/<new-name>" <output-dir>/
```

### `package_skill.py` vs `convert_to_claudeai.py` (which to use)

Both build a wrapper-folder zip; they differ in how much they touch the content.

- **`convert_to_claudeai.py` = sanitiser.** Strips CC-only frontmatter (`allowed-tools`) **textually** — the surviving frontmatter lines ship byte-for-byte (since 2026-09-10; it previously re-serialised the frontmatter through a YAML dump, which is what produced the escaped-frontmatter rejection described under Built-In Packaging Enforcement) — and scrubs `mcp__…` / `Bash(…)` references from **prose** (→ `[MCP tool]` / `[CLI command]`, reporting each scrub). **Fenced code blocks are preserved verbatim**, so a documented example like `allowed-tools: Bash(git:*)` is not corrupted. Use it when a skill genuinely needs sanitising for distribution.
- **`package_skill.py` = verbatim.** Validates, then zips the source unchanged. Use it when the source is **already distribution-clean** (no `allowed-tools`, nothing to scrub) — e.g. `instruction-creator` itself.

After packaging either way, verify any documented tool literal survived: `unzip -p <skill>.zip <skill>/SKILL.md | grep -F 'Bash(git:*)'`.

### What the packagers leave out

The packagers walk the filesystem, not the git index, so a gitignored file still ships unless a rule below excludes it. Both scripts drop:

| Left out | Why |
|---|---|
| Maintainer files — `TODO.md`, `CHANGELOG.md`, `README.md`, `cd-project-recipe.md`, `.gitignore`, `todo/` directories | Dev logs, roadmaps, and maintainer context that do not serve skill consumers |
| Build and OS cruft — `__pycache__/`, `*.pyc`, `.DS_Store` | Never content |
| Tool caches — `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, `.venv/` | These write their own internal `.gitignore`, so they are invisible to `git status` and to review, yet a filesystem walk would ship them |
| Database binaries — `*.duckdb`, `*.sqlite`, `*.sqlite3` | Derived caches that can hold a full dataset even when gitignored; regenerate them on the consumer side or ship a text extract |

`convert_to_claudeai.py` additionally drops `*.env`, `*.key`, `*.pem`, and a browser-only `dashboard/` directory, and honours a **per-skill exclude file**: an optional `.claudeai-exclude` at the skill root, one pattern per line (`#` comments), using a `dir/` prefix, a `*` glob on the filename, or an exact relative path. Use it to ship a curated subset (for example summary CSVs) while keeping bulk data out of the zip. The file itself never ships.

```text
# .claudeai-exclude
data/raw/
*.parquet
notes/working-draft.md
```

Bundled reference PDFs that push a skill past the size limit still need manual stripping, or a `.claudeai-exclude` entry: see the 30 MB section below.

---

## Built-In Packaging Enforcement (Layer 2 — since 2026-07-20)

Both packaging scripts import `scripts/packaging_checks.py` and **fail the build locally** instead of failing at Claude Desktop upload time or silently shipping content that would need re-sanitising on every rebuild:

| Check | When | Outcome |
|---|---|---|
| **Archive layout** — every member must sit inside ONE top-level folder named for the skill; a bare root-level file, a second top-level folder, a `__MACOSX/` tree, or a root-level `.DS_Store` fails; the folder name must match the skill name | Always (post-zip) | ERROR (new build discarded) — Claude.ai rejects the whole upload: "All files must be inside the top-level folder" (see § Single Top-Level Folder) |
| **Frontmatter literal** — the wrapper-root `SKILL.md` frontmatter contains a hex/unicode escape (`\u2014`, `\x..`, `\U........`), a line ending in `\` (escaped line break), or lacks `name:` / `description:` | Always | ERROR (build aborts) — Claude Desktop rejects such a zip: "contains a hex/unicode escape or an escaped line break in its SKILL.md frontmatter, which can spell keys some parsers see and others don't. Write the text literally." |
| **Filename charset** — any zip path with chars outside `[A-Za-z0-9._-/]` | Always | ERROR (build aborts) |
| **Redundant binary** — a bundled PDF whose same-stem `.md` companion is also bundled | Always | ERROR — archive the PDF outside the skill per `skill-content-formats-guide.md`, ship the `.md` |
| **Large binary** — bundled binary > 1 MB | Always | WARNING |
| **30 MB zip cap** | Always (post-zip) | ERROR (new build discarded) |
| **Secret / personal-content scan** — real `op://` refs (vault names with spaces; placeholders and single-word teaching examples pass), real `/Users/<name>/` or `/home/<name>/` home paths (placeholder usernames pass), private-key blocks, AWS key ids | **`--team` only** | ERROR per hit |
| **Maintainer-local deny patterns** — optional extra regexes read from the file named by `SKILL_PACKAGING_DENY_FILE` (default `~/.claude/packaging-deny-patterns.txt`; one per line, `#` comments) for your own names, account ids, and other private strings | **`--team` only** | ERROR per hit |

**A failed build never touches the zip already at the output path.** Both scripts write the archive to a temporary file beside the output path (`.<skill>.zip.<pid>.tmp`), run the post-zip checks on it, and move it into place with one atomic rename only when every check passes (`packaging_checks.StagedZip`). On any failure the temporary file is removed and the previous zip stays byte-for-byte as it was. Before this, an oversized rebuild deleted the last good zip. Regression tests: `uv run --script scripts/test_packaging_atomic.py`.

**Pass `--team` on every build destined for shared/organisation distribution** (both scripts accept it). Personal-use builds omit it — a personal skill may legitimately contain your own paths and secret-store references.

```bash
# Team build — secret scan ON
uv run <ic>/scripts/convert_to_claudeai.py <skill> <output-dir>/ --team
python3 <ic>/scripts/package_skill.py <skill> <output-dir>/ --team
```

**Local deny file (`SKILL_PACKAGING_DENY_FILE`).** The `--team` scan knows generic secret shapes but not your private strings. List those as regexes, one per line, in a file outside any repository, and point the `SKILL_PACKAGING_DENY_FILE` environment variable at it; when the variable is unset the scripts read `~/.claude/packaging-deny-patterns.txt` if it exists. A missing file is not an error: the scan runs with the built-in patterns only.

```bash
# deny file: one regex per line, '#' starts a comment
#   (?i)example-corp
#   \bACCT-[0-9]{6}\b
SKILL_PACKAGING_DENY_FILE=/path/to/deny-patterns.txt \
    uv run <ic>/scripts/convert_to_claudeai.py <skill> <output-dir>/ --team
```

The sections below document the upload constraints the checks automate (folder layout, charset, 30 MB) — kept for background and for manual verification of zips built elsewhere.

---

## Single Top-Level Folder (MANDATORY)

Claude's skill uploader requires **every archive member to sit inside ONE top-level folder named for the skill** (`<skill>/SKILL.md`, `<skill>/references/…`). A single member outside that folder — even one bare root-level file — rejects the whole archive with the error **"All files must be inside the top-level folder"**. A second top-level folder, a Finder/ditto `__MACOSX/` tree, or a root-level `.DS_Store` fails the same way. Extra files *inside* the folder are fine.

Real-world bite (2026-09-21): a bespoke builder wrote every skill member as `<skill>/<name>` but appended a `manifest.json` at the archive root with no folder prefix. `<skill>/SKILL.md` was present and correct, so a presence-only check passed — yet Claude rejected the affected zips. Presence of `<skill>/SKILL.md` is necessary, not sufficient; the layout of *all* members is the test.

One-line diagnostic for any zip:

```bash
unzip -Z1 <zip> | awk -F/ '{print (NF==1 ? "ROOT FILE: "$1 : "folder: "$1)}' | sort -u
```

A correct skill zip prints exactly one `folder:` line and no `ROOT FILE` line. `packaging_checks.check_archive_layout()` automates this: both packagers run it post-zip and discard the new build on failure, leaving any existing zip in place.

Scope: this rule is for **skill zips**. Flat non-skill attachment archives (a zip of documents attached to a chat) are a different upload path and are not subject to it.

---

## Literal Frontmatter (MANDATORY)

Claude Desktop rejects a skill zip whose `SKILL.md` frontmatter contains a hex/unicode escape (`\u2014`, `\x..`) or a line ending in `\`. Both are what a YAML library emits when it re-serialises a frontmatter holding non-ASCII text (an em-dash, a curly quote) or a long `description`: without an allow-unicode option the character becomes an escape, and the default line width folds the value with `\` continuations.

Real-world bite (2026-09-10): a first-time skill upload was rejected with "contains a hex/unicode escape or an escaped line break in its SKILL.md frontmatter … Write the text literally." The converter had re-serialised the frontmatter through a YAML dump, and most zips it had built carried the same defect (every skill with a non-ASCII character or a description over about 70 characters). Identically escaped zips uploaded the same day as *replacements* of existing skills were accepted, so the check may be stricter for new skills or may have gone live between uploads — undetermined. It is a server-side check. Treat every escaped zip as un-uploadable regardless: a rebuild takes seconds.

- Write frontmatter values on one line, with non-ASCII characters typed as themselves.
- Never regenerate SKILL.md frontmatter through a YAML library. The converter removes fields textually and never dumps YAML; `packaging_checks.py` fails any build whose frontmatter is not literal.
- **Any zip built before 2026-09-10 with `convert_to_claudeai.py` should be rebuilt before its next upload.** Do not "fix" this by installing a round-trip YAML library — the check, not the library, is the guarantee.

Manual check for a zip built elsewhere:

```bash
unzip -p <zip> <skill>/SKILL.md | awk '/^---$/{d++; next} d==1' | grep -n -E '\\[uUx][0-9A-Fa-f]|\\$' && echo "NOT LITERAL" || echo "OK"
```

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

Real-world bite: a reference-heavy skill (one bundling many PDFs) was rejected on upload — 6 PDFs had spaces, 1 had a smart-quote apostrophe, 1 had an ASCII apostrophe. Fix required kebab-casing all 7 + updating 5 SKILL.md path refs. Both packaging scripts now run this check before zipping (see Built-In Packaging Enforcement above), so it fails locally instead of at upload.

---

## 30 MB Upload Limit (MANDATORY)

**All Claude Desktop .zip skill uploads must be strictly under 30 MB total.**

Skills exceeding 30 MB will fail to upload. This applies to BOTH:
- skill zips uploaded on an individual Claude plan (Pro/Max)
- skill zips uploaded to a Claude Team or Enterprise organisation

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
| **Convert PDFs to .md extracts** | The PDF content is high-value for context loading — extract substantive sections to markdown (smaller; also parseable), e.g. pull the key statute/policy text into a `references/` subfolder. |
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

### Worked Examples

| Skill | Initial Zip Size | Status | Required Action |
|---|---|---|---|
| `reference-heavy-skill.zip` | 62 MB | ❌ Over limit | Split: ship .md content + key reference extracts under one zip; relocate the bulky source PDFs to a separate distribution |
| `large-skill.zip` | 52 MB | ❌ Over limit | Strip the bulky reference PDFs from the uploaded copy; keep the markdown body |
| `small-skill.zip` | 35 KB | ✅ Well under | Ship as-is — markdown-only skill |

**Convention**: When a skill folder grows past 30 MB total, fork a `<skill>-references-pdf/` directory inside the skill (still tracked in your git repo for version control), but exclude it from `package_skill.py` for Claude Desktop zipping. Document in the skill's TODO.md.
