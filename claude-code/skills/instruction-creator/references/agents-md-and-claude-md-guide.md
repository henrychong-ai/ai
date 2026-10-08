# AGENTS.md and CLAUDE.md — Directory Instruction Files

**Standard for directory-level (project, repo, workspace, subdirectory) instruction files across coding agents.**

Verified against the Claude Code memory docs (`https://code.claude.com/docs/en/memory` § AGENTS.md) and the v2.1.277 changelog entry on 2026-09-21. Re-verify before relying on version-specific behaviour.

---

## The Standard

| File | Role | Content |
|---|---|---|
| `AGENTS.md` | **Canonical** | All substantive, portable instructions. Read natively by Codex, Cursor, Copilot, Gemini CLI, and others. |
| `CLAUDE.md` | **Import shim** | First line `@AGENTS.md`. Below it, only genuinely Claude-only addenda (skill/hook/subagent mechanics); usually nothing. |

Shim template:

```markdown
@AGENTS.md
```

With Claude-only addenda:

```markdown
@AGENTS.md

## Claude Code only
- <mechanic that has no meaning on other harnesses>
```

**Scope:** directory-level files only. User-level and generated files are out of scope: `~/.claude/CLAUDE.md` and `~/.claude/rules/` have no `AGENTS.md` equivalent (Claude Code never reads `~/.claude/AGENTS.md`), and `~/.codex/AGENTS.md`, vendor-managed, and generated files keep their own arrangement.

## Why a Shim and Not the Native Fallback

Claude Code v2.1.277+ reads `AGENTS.md` natively, controlled by **Project instructions** in `/config`:

| Value | Loads |
|---|---|
| `claude-md-or-agents-md` (default) | `CLAUDE.md` files; `AGENTS.md` only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or above |
| `claude-md-and-agents-md` | Both, each directory's `CLAUDE.md` first, then its `AGENTS.md`; an `AGENTS.md` already imported or symlinked is skipped, never read twice |
| `claude-md` | `CLAUDE.md` files only |
| `managed-only` | Organisation-managed `CLAUDE.md` and auto memory only |

Settings-file form (user, `--settings`, or managed settings; ignored in project and local settings):

```json
{
  "pluginConfigs": {
    "agents-md@builtin": { "options": { "instructionFiles": "claude-md-and-agents-md" } }
  }
}
```

The native read is a safety net, not the mechanism to depend on:

| Native direct read | `@AGENTS.md` import from `CLAUDE.md` |
|---|---|
| Silently disabled by any ancestor `CLAUDE.md` or a `CLAUDE.local.md` (default mode) | Always loads |
| Absent from `/memory` and the Memory files list in `/context` | Listed |
| `InstructionsLoaded` hooks do not fire | Fire |
| `--add-dir` directories: not loaded | Loaded (with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`) |
| Unavailable before v2.1.277, on Bedrock and other third-party providers, with telemetry disabled, with `disableAllHooks` / `allowManagedHooksOnly`, with the built-in `agents-md` plugin disabled, and in the first session after an upgrade | Works everywhere |

Never read by Claude Code in any mode: `AGENTS.local.md`, `AGENTS.override.md`, anything under `.agents/`.

## Rejected Alternatives

| Pattern | Problem |
|---|---|
| `CLAUDE.md` that says in prose "read AGENTS.md" | Loads nothing. Claude sees `AGENTS.md` only if it decides to open it. Replace with the import. |
| `CLAUDE.md` symlinked to `AGENTS.md` | Edit/Write refuse to write through the link; Cowork desktop sessions skip symlinked instruction files; Windows clones check the link out as a one-line text file. |
| Delete `CLAUDE.md`, rely on the native fallback | Fails silently under the conditions in the table above; teammates on older versions get no instructions. |
| Substantive content in both files | Drift and conflicts. One canonical file. |
| `SessionStart` hook that prints `AGENTS.md` | Duplicates the content once native reading is active. Remove. |

## Authoring Procedure

**New directory instruction file**
1. Write the content in `AGENTS.md`, harness-neutral: no Claude-only tool names or mechanics in portable sections.
2. Create `CLAUDE.md` containing `@AGENTS.md`.
3. Verify in a fresh Claude Code session: `/context` → Memory files lists `AGENTS.md` via the import.

**Existing `CLAUDE.md` encountered or updated** (forward-only; no bulk sweeps unless asked)

| State found | Action |
|---|---|
| Substantive `CLAUDE.md`, no `AGENTS.md` | `git mv CLAUDE.md AGENTS.md` (preserves history), neutralise Claude-only wording or move it below the import, add the shim |
| Prose-pointer `CLAUDE.md` + substantive `AGENTS.md` | Replace the prose with `@AGENTS.md` |
| Substantive `AGENTS.md`, no `CLAUDE.md` | Add the shim |
| Both substantive | Flag the conflict and propose a merge into `AGENTS.md`; never merge or overwrite silently |
| Already compliant | Nothing |

In a shared or team repository the change affects every contributor's agents: propose it in the normal review flow rather than converting as a side effect of unrelated work.

## Writing Style

`AGENTS.md` inherits every rule for auto-loaded files: it loads in full every session on every harness, so keep it directive, terse, table-first, and within the project budget (under ~200 lines). `@import` is not lazy; the imported file loads in full.

`/init` writes `CLAUDE.md` by default; after running it, apply the first row of the table above.
