# Claude Desktop Project Bundle Guide

Load this reference whenever generating, refreshing, or scaffolding a Claude Desktop **Project Custom Instructions** file for a skill that backs a Claude Desktop Project.

**v3 (2026-05-19 latest):** Universal pattern for all **linked skills** (skills that back a Claude Desktop Project — marked `CD-P ✓` or `CD-P ○` in `distribution-manifest.md`). The only Project-specific artifact is the paste-ready Custom Instructions `.md` file, emitted side-by-side with the matching skill `.zip` at `~/.claude/skills-claude-desktop/`. Knowledge files travel inside the skill `.zip` via Claude.ai's auto-synced skill mount (`/mnt/skills/user/<skill>/`) and reach every consumer surface (Desktop, web, iOS, Android) without duplication.

The `.zip` format remains reserved exclusively for Skill uploads (see `claude-desktop-packaging-guide.md`). Custom Instructions are a single paste-ready `.md` file.

---

## Linked skill vs standalone skill vs CD-only Project

| Type | manifest CD-P column | Required artifacts at `~/.claude/skills-claude-desktop/` | `/instruction-creator` responsibility |
|---|---|---|---|
| **Linked skill** (skill + paired CD Project) | `✓` or `○` | `<skill>.zip` + `<skill>-project-instructions.md`, side-by-side | Yes — generate and refresh both |
| **Standalone skill** (no paired CD Project) | `-` | `<skill>.zip` only | Yes — generate and refresh the .zip only |
| **CD-only Project** (Project, no backing CC skill) | n/a — not in manifest | n/a — managed in Claude Desktop GUI only | None |

CD-only Projects (Claude Desktop Projects with no backing CC skill) are managed entirely in the Claude Desktop GUI. /instruction-creator has no role in maintaining them.

---

## Architectural overview

**Separation of concerns:**

| Concern | Owner | Where it lives |
|---|---|---|
| **Engine** — the Custom Instructions extraction + emission procedure | `/instruction-creator` (this skill) | This guide |
| **Recipe** — the paste-ready Custom Instructions text (with per-surface capability matrix) + File Manifest tracking which skill files end up bundled in the .zip + Sync Log | The specific skill backing the Project | `references/cd-project-recipe.md` inside that skill |
| **Output** — single paste-ready `.md` file | Side-by-side with the skill .zip | `~/.claude/skills-claude-desktop/<skill>-project-instructions.md` |

This split means: any linked skill carries a single small recipe file; the extraction logic lives once in `/instruction-creator`; the output is reproducible and never committed to the skill's source.

---

## Recipe file schema

Every linked skill keeps **one file** at `references/cd-project-recipe.md` with exactly three sections:

```markdown
# Claude Desktop Project Recipe — <skill-name>

## Custom Instructions

(Full paste-ready text. Becomes `<skill-name>-project-instructions.md` in the output. Written in second-person "You are ..." voice addressed to the Claude Desktop Project.

REQUIRED: includes a per-surface capability matrix near the top — rows for: bundled skill files, local filesystem (if applicable), MCP servers, local scripts, browser dashboards, image attachments. Columns for: Claude Desktop, Claude.ai web, Claude iOS / Android.)

## File Manifest

| Source path (relative to skill root) | Reachable as `/mnt/skills/user/<skill>/...` | Notes |
|---|---|---|
| references/foo.md | ✅ | |
| references/tests/README.md | ✅ | |
| templates/bar.csv | ✅ | |

(Source paths are relative to the skill's root directory — i.e. starting from `~/.claude/skills/<skill-name>/`. The manifest documents which skill files are reachable from the Project via the auto-synced skill mount — not files copied into a separate bundle dir.)

## Sync Log

| Date | Trigger | Notes |
|---|---|---|
| YYYY-MM-DD | Initial recipe creation | |
| YYYY-MM-DD | Refresh — content X changed | What changed, what was re-emitted |
```

The Sync Log lives inside the recipe so it travels with the skill in git — record-of-truth for what was uploaded and when.

---

## Emission procedure

When the user asks to (re)generate the Project Custom Instructions for skill `<S>`:

1. **Verify linked-skill status** — check `~/.claude/skills/git/references/distribution-manifest.md` for the CD-P column on row `<S>`. If `-` or absent, this skill does NOT have a paired Project — stop and tell the user no Custom Instructions are needed. If `✓` or `○`, proceed.
2. **Load** the recipe at `~/.claude/skills/<S>/references/cd-project-recipe.md`. If absent, prompt the user to scaffold it (see "Scaffolding a new recipe" below).
3. **Verify** the Custom Instructions section contains a per-surface capability matrix. If missing, prompt the user to add it before emitting (linked skills require it).
4. **Resolve output path** — universal default is `~/.claude/skills-claude-desktop/<S>-project-instructions.md` (alongside the matching `<S>.zip`).
5. **Extract** the **Custom Instructions** section blockquote — strip the leading `> ` from each line, collapse trailing blanks.
6. **Write** the extracted text to the output path. **Do NOT auto-overwrite** if the user has indicated paste-edits are in flight; instead, prompt for confirmation.
7. **Report** to the user: file ready at the output path; suggest the next action ("re-upload `<S>.zip` to Claude.ai Settings → Capabilities → Skills; paste this file's contents into Claude Desktop → Project `<Name>` → Custom Instructions").

No directory, no auto-README, no copied knowledge files. The skill `.zip` rebuild is a separate procedure (see `claude-desktop-packaging-guide.md`); the Custom Instructions emission is a one-file write.

---

## Cross-skill invocation pattern

Generating Project Custom Instructions is a two-skill collaboration:

| When user says... | Load... | Then... |
|---|---|---|
| "rebuild the project custom instructions for skill X" / "refresh /X's CD-P file" | `/instruction-creator` (engine) + `/X` (recipe owner) | Execute the procedure above with `<S> = X` |
| "create a new Claude Desktop Project for skill X" | `/instruction-creator` + `/X` | First check whether `~/.claude/skills/X/references/cd-project-recipe.md` exists; if not, scaffold it from the template above by reading the skill's existing references/ + templates/ + SKILL.md and proposing a manifest |

Each linked skill should add an activation cue near the top of its SKILL.md (one line): *"When asked to (re)build the Project Custom Instructions for this skill, load `/instruction-creator` alongside this skill and follow its `references/cd-project-bundle-guide.md`."*

---

## Scaffolding a new recipe (for newly-linked skills)

When asked to set up a new Claude Desktop Project for a skill `<S>` that doesn't yet have a recipe:

1. Read `~/.claude/skills/<S>/SKILL.md` to understand the skill's purpose, scope, conditions, output discipline.
2. Audit `~/.claude/skills/<S>/references/` and `~/.claude/skills/<S>/templates/` for candidate knowledge files. Exclude: heavy PDFs, source-only files, internal-tooling docs. (These all travel in the skill .zip auto-sync — the manifest documents which ones are reachable, not which ones get re-uploaded.)
3. Draft the **Custom Instructions** section in second-person voice — identity, primary subject matter, knowledge file references, **per-surface capability matrix** (Desktop / web / iOS / Android), what the Project can/can't do per surface, routing rules, output discipline.
4. Draft the **File Manifest** table documenting which skill files are reachable via the skill mount.
5. Write the **Sync Log** with a single creation row.
6. Save to `~/.claude/skills/<S>/references/cd-project-recipe.md`.
7. Update the skill's row in `distribution-manifest.md`: set CD-P `○` (recipe authored, awaiting first upload).
8. Surface the draft to the user for review before running the emission procedure.

---

## What this guide is NOT for

- **Skill `.zip` uploads** to Claude.ai Settings → Capabilities → Skills. See `claude-desktop-packaging-guide.md`.
- **Team-shared CD-T skills** on a Claude Team plan — the same single-file pattern applies symmetrically if a CD-T skill ever has a paired Team-workspace Project. See `claude-desktop-packaging-guide.md` for the .zip side.
- **Per-conversation Project content** edits inside Claude Desktop itself (those happen in the app).
- **CD-only Projects** (Claude Desktop Projects with no backing CC skill — out of scope, managed in GUI only).

---

## Edge case: Project-specific Knowledge panel overrides

The v3 default uploads zero knowledge files to the Project — the skill mount provides everything. If a Project ever needs Knowledge panel content NOT in the skill (e.g. interim drafts, sensitive ad-hoc context, sandboxed experimentation), author those files ad-hoc at a location of your choosing at that time and upload them manually. This is **not** a perpetual `/instruction-creator` output — it's a user-driven ad-hoc workflow.

---

## Migration notes (historical reference)

The CD-P pattern has evolved through three iterations on 2026-05-19:

| Era | Output | Knowledge files | Status |
|---|---|---|---|
| v1 (morning) | Regular directory at `~/.claude/claude-desktop-projects/<project>/` containing `<project>-project-instructions.md` + 30+ flat knowledge files + auto-README | Duplicated into the bundle dir; uploaded into the Project's Knowledge panel | Retired |
| v2 (afternoon) | Single `.md` file at `~/.claude/claude-desktop-skills/<skill>-project-instructions.md`, co-located with `<skill>.zip` | Travel inside the skill `.zip` via auto-synced skill mount | Superseded by v3 dir rename |
| v3 (latest) | Single `.md` file at `~/.claude/skills-claude-desktop/<skill>-project-instructions.md`, co-located with `<skill>.zip` | Same as v2 | **Current** |

**Why v2 over v1:** Once Claude.ai auto-syncs uploaded skills to every consumer surface (Desktop, web, iOS, Android) via `/mnt/skills/user/<skill>/`, duplicating those same files into a Project Knowledge panel is pure redundancy. The Custom Instructions text is the only Project-specific content.

**Why v3 over v2:** Directory name canonicalised. Both `.zip` skill uploads and `.md` Project Custom Instructions are "Claude Desktop deployment-target artifacts" — co-located at `~/.claude/skills-claude-desktop/` (replacing the older v2 `~/.claude/claude-desktop-skills/` which described only the .zip).

**Pre-v1 legacy:** `project-desktop/` subdir inside each skill (custom-instructions.md + README with re-zip script producing a `.zip`) — already migrated to recipe pattern in v1 and onwards.

Outputs land at `~/.claude/skills-claude-desktop/<skill>-project-instructions.md`, alongside the matching `<skill>.zip`.
