# Skill Content Formats & Source-File Archive Guide

Load this reference whenever a skill has — or is about to acquire — binary files (PDFs, images, audio, video, scanned documents) or any non-text content that AI cannot load inline. Two concerns:

1. **Convert** the substantive content of each binary into an AI-friendly text format that lives inside the skill (`.md`, `.csv`, `.jsonl`, etc.) so it loads at zero cost into Claude's context.
2. **Archive** the original binary outside the skill in a companion directory (`~/.claude/skill-originals/<skill>/...` universal, or a personal override location) for reverse-lookup if the canonical original is ever needed (legal, claims, signatures, exact-format reproduction).

The skill stays lightweight + searchable. The original binary stays preserved + recoverable.

---

## Format-by-Content-Type Mapping (CANONICAL)

Use these defaults when authoring a new skill OR converting existing binaries.

| Content type | Format | Notes |
|---|---|---|
| **Reference docs, policies, prose, narrative** | `.md` | Default for anything text-shaped. Loads inline. |
| **Tabular data** (biomarkers, schedules, comparisons, inventories) | `.csv` | Default tabular format. RFC 4180 quoting handles commas-in-fields universally — every competent parser (Claude, pandas, Excel, Sheets) reads quoted CSV correctly. |
| **Tabular data (bioinformatics)** | `.tsv` | Community-standard for genome / VCF / 23andMe raw / FASTA-adjacent tables. Use only when honouring an established bioinformatics convention; otherwise use `.csv`. |
| **Structured records / event streams** (visits, lab results, KG exports, append-only logs) | `.jsonl` | One record per line — streams + appends cleanly, schema-flexible per entity. |
| **Single config object** (settings consumed programmatically) | `.json` | When a tool/runtime reads the file. No comments. |
| **Config with comments or nested structure** | `.yaml` | Same family as skill frontmatter. Comments + anchors + readable nesting. |
| **Diagrams, flowcharts, state machines** | Mermaid in `.md` | Claude reads AND renders Mermaid. Avoid PNG/SVG diagram exports — source is the artefact. |
| **Code, scripts** | Native (`.py` / `.ts` / `.sh` / `.sql`) | Keep in `scripts/`. |
| **Time-series data** | `.csv` with ISO 8601 dates | `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ` — unambiguous and sortable. |
| **Templates** (forms, letters, briefs, prompts) | `.md` or `.csv` | `.md` for prose templates; `.csv` for repeated-row data templates. |
| **Email exports** | `.md` (subject + body per file) + archive raw `.eml` | One `.md` per message for searchability; archive `.eml` if signatures/headers matter. |
| **Calendar / schedules** | `.csv` or `.md` + archive raw `.ics` | Extract events to text; archive `.ics` if recurrence rules / VTIMEZONE must round-trip. |
| **Audio / video** | Whisper transcript to `.md` + archive original | Speaker labels + timestamps if useful. |
| **Scanned documents / images-with-text** | OCR to `.md` + archive original | `tesseract` for clean scans; `markitdown[ocr]` for mixed binaries. |
| **Digitally-created PDFs** (policies, brochures, terms) | `pdftotext -layout` → `.md` + archive original | `-layout` preserves columns and table structure. |
| **Spreadsheets** (.xlsx, .numbers, Google Sheets export) | Per-sheet `.csv` | One `.csv` per logical sheet. Drop styling/charts (not AI-useful). |
| **Word docs** | `markitdown` → `.md` + archive original | Plain markdown captures structure. |
| **Form-style PDFs** (claim forms, intake forms) | `pdftotext -layout` → `.md` (field labels) + archive original | Extract field labels for AI awareness; original required for fill-and-submit. |
| **Knowledge graph exports** | `.jsonl` (one entity per line) | Append-friendly; schema-flexible per entity. |
| **Raw genomic / instrument data** | Native (`.tsv` / `.vcf`) + curated `.md` summary | Don't inline 15 MB of raw data — write a curated summary `.md` that the skill loads, archive the raw file. |
| **Plain text without structure** | `.md` | Prefer `.md` even for unstructured text — supports light formatting if the file later evolves. |

### Heuristic when in doubt

- Does Claude need to **read** the substantive content? → text format inside the skill (`.md` / `.csv` / `.jsonl`).
- Does Claude need to **reproduce** the original (exact bytes, signatures, fillable fields)? → archive the original outside the skill.
- Often **both** — extract to text AND archive the original.

### Why CSV is the tabular default (and TSV is not)

CSV with proper quoting (RFC 4180) handles fields containing commas without ambiguity — `"Chong, Henry",1980,HK` is parsed identically by every modern tool (pandas, Excel, Numbers, Sheets, every language stdlib, Claude itself). The folklore "use TSV when fields contain commas" is a 1990s hangover from naïve parsers and does not apply in 2026. TSV only earns a spot for bioinformatics community-standard formats (genome data, VCF, etc.), where the convention is fixed regardless of whether commas appear.

### Formats deliberately NOT in this table

- **`.toml`** — usable only when a tool *requires* it (`Cargo.toml`, `pyproject.toml`). For free-choice skill config, prefer `.yaml` (comments + readable nesting) or `.json` (programmatic consumption). Never pick TOML as a default for skill-authored knowledge content.
- **`.txt`** — superseded by `.md` for skill content. `.txt` outputs from conversion tools (e.g. tesseract's default extension) should be renamed to `.md` immediately.
- **`.xml`** — too verbose for skill authoring; convert to `.json` / `.jsonl` if structure is needed, or `.md` if the content is narrative.
- **`.parquet`, `.sqlite`** — binary formats. If you need a queryable database alongside a skill, that's a tool integration, not a skill knowledge file.

---

## Conversion Toolbox

Local tools that produce these formats reliably. All available on macOS via Homebrew or pipx.

| Tool | Best for | Invocation pattern |
|---|---|---|
| **`pdftotext -layout`** (poppler) | Digitally-created PDFs with text layer | `pdftotext -layout "input.pdf" "output.md"` — preserves columns and tables |
| **`tesseract`** | Images with text, scanned PDFs (after rasterise) | `tesseract input.jpg output -l eng` (outputs `output.txt`; rename to `.md`) |
| **`markitdown`** | Mixed binary → markdown (Word, Excel, PowerPoint, some PDF) | `markitdown input.pdf -o output.md` — install with `pipx install 'markitdown[all]'` for full PDF/OCR support |
| **`pandoc`** | Anything → anything (LaTeX, RST, DOCX, EPUB, HTML, MD) | `pandoc -f docx -t markdown input.docx -o output.md` |
| **`whisper`** | Audio/video → transcript | `whisper input.m4a --model base --output_format md` |
| **`magick`** (ImageMagick) | Image preprocessing for OCR (deskew, contrast) | `magick input.jpg -auto-level -density 300 output.png` then tesseract |
| **`ffmpeg`** | Extract audio from video for whisper | `ffmpeg -i video.mp4 -vn audio.m4a` |

### Conversion quality tiers

| Tier | Input quality | Tools | Expected output |
|---|---|---|---|
| **A** | Digitally-created PDF, machine-readable text layer | `pdftotext -layout` | Clean text, preserved structure, ~1 second per file |
| **B** | Image-based PDF (scanned), reasonable resolution | `pdftoppm` + `tesseract` | Mostly accurate OCR, some character errors; review headers/numbers |
| **C** | Low-quality scan, handwriting, unusual fonts | Manual OCR + cleanup, or `markitdown[ocr]` with vision model | Lower accuracy; manually verify key data points |

Skip "claim forms" and other fillable templates from full text extraction — extract the field labels only (so AI knows what data the form requires) and keep the original PDF for filling/submission.

---

## Source-File Archive Convention

When a skill has binaries that have been converted to text, **move the originals** out of the skill into a companion archive directory.

### Universal default location

```
~/.claude/skill-originals/<skill-name>/<original-subdir-structure>/<original-filename>.<ext>
```

**Why `skill-originals/`?** Pithy, descriptive (these are the canonical pre-conversion originals), and avoids the "archive" ambiguity that could imply deprecated skills. Matches the `~/.claude/skill-*` and `~/.claude/claude-desktop-*` naming convention.

### Personal override locations

Check `~/.claude/overrides/skills/instruction-creator.md` for a personal override. Henry's machine routes archives to:

```
~/Obsidian/memory-bank/_skills/<skill-name>/<original-subdir-structure>/<original-filename>.<ext>
```

This keeps Henry's personal skill-originals inside the Obsidian-synced memory-bank so they're backed up + searchable from Obsidian + accessible across devices.

### Subdir structure: preserve, don't flatten

Always preserve the original subdirectory structure under the skill-name root. This makes reverse-lookup trivial — if the skill's `references/insurance/foris/forms/AXA-HK-Dental-Claim-Form-2025.md` is the extracted text, the original lives at the symmetric path `<archive-root>/medical/references/insurance/foris/forms/AXA-HK-Dental-Claim-Form-2025.pdf`. No mental translation needed.

### SKILL.md pointer pattern

Each skill that has archived originals documents the archive location in its SKILL.md, near the section that references the extracted-text files. Pattern:

```markdown
**[Section title]** — text extracts in `references/<subdir>/*.md`. Original binaries archived to `<archive-root>/<skill-name>/references/<subdir>/` (preserved subdir structure) for reverse lookup if exact-format originals ever needed (legal, claims, signatures).
```

Reference implementation: `~/.claude/skills/medical/SKILL.md` Insurance Coverage section.

---

## Migration Playbook (for skills with existing binaries)

When applying this pattern to a skill that currently has PDFs/images/etc. mixed in with `references/`:

1. **Inventory the binaries.**
   ```bash
   find ~/.claude/skills/<skill>/ -type f \( -name "*.pdf" -o -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.mp4" -o -name "*.m4a" \) -exec du -h {} \;
   ```
2. **Classify each binary** against the format table above. Decide: text-extract-only, archive-only, or both.
3. **Convert** the substantive ones using the toolbox above. Land outputs in the same subdirectory as the original, with a normalised kebab-case filename matching the original (replacing spaces, fixing typos, ASCII-only).
4. **Spot-check** each extracted file — open the largest and smallest outputs; verify substantive text is present and readable. For OCR outputs, check that key fields (numbers, names, dates) came through correctly.
5. **Create the archive subdir tree** under the archive root preserving structure:
   ```bash
   mkdir -p <archive-root>/<skill>/<each-original-subdir-relative-path>
   ```
6. **Move the originals** preserving filenames + subdir structure:
   ```bash
   mv <skill-path>/<original-subdir>/<filename>.<ext> <archive-root>/<skill>/<original-subdir>/
   ```
7. **Update SKILL.md** — replace any references to the binary filenames with the new `.md` filenames; add an archive-location pointer paragraph (pattern above).
8. **Update any in-skill cross-references** (e.g. `insurance-overview.md` referencing other policy docs) — `sed -i.bak 's|\.pdf|\.md|g' <file>` or equivalent.
9. **Rebuild the skill zip** (if CD-S / CD-T marked) — the new `.md` content should now be included (subject to 30 MB cap; see `claude-desktop-packaging-guide.md`).
10. **Update the CD-P recipe** (if CD-P marked) — decide whether the new text content should join the Project bundle's File Manifest.
11. **Update distribution manifest** — bump CD-S to `○` pending re-zip; same for CD-P if recipe changed.

Reference run-through: the 2026-05-19 `/medical` insurance extraction (12 PDFs + 1 JPG → 13 `.md`; originals to `~/Obsidian/memory-bank/_skills/medical/`).

---

## CD-S / CD-T / CD-P Compliance Implications

When a skill goes through this conversion + archive workflow:

| Marker | Implication |
|---|---|
| **CD-S** | Skill zip size shrinks dramatically when bulky binaries leave the skill. Re-zip after migration — see `claude-desktop-packaging-guide.md` for size-reduction strategies if still over 30 MB. |
| **CD-T** | Same as CD-S. Verify the extracted `.md` content does not contain personal data that would have been "protected" by being PDF-buried — if any sensitive content surfaced in extraction, re-sanitise before team-plan re-upload. |
| **CD-P** | Decide whether the new `.md` extracts belong in the Project Knowledge bundle. If yes, add them to the recipe's File Manifest at `references/cd-project-recipe.md` and rebuild the bundle dir. |

---

## When to skip this pattern

- **Tiny binaries** (< 100 KB) used as illustrations or reference samples — leave in `references/` as-is if their content isn't worth converting.
- **Binary tooling artefacts** that need to round-trip exactly (font files, signed certificates, executable models) — never convert these to text; if they're part of the skill, they live in `references/` directly.
- **Confidential originals** that must not be extracted to searchable text (rare — but if a binary's substantive content shouldn't be inline-loadable for security reasons, leave it as a binary in `references/` with a clear note in SKILL.md).
