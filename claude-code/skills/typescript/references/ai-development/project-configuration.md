# Claude Code Project Configuration Patterns

Patterns for structuring Claude Code configuration across multi-environment TypeScript projects.

---

## Memory Hierarchy

Claude Code loads configuration in this order (highest to lowest priority):

| Priority | Location | Scope | Git Status |
|----------|----------|-------|------------|
| 1 | Enterprise policy | Org-wide | N/A |
| 2 | `./CLAUDE.md` | Project | Tracked |
| 3 | `./.claude/rules/*.md` | Project | Tracked |
| 4 | `~/.claude/CLAUDE.md` | User | N/A |
| 5 | `~/.claude/rules/*.md` | User | N/A |
| 6 | `./CLAUDE.local.md` | Project local | **Auto-ignored** |

**Key principle:** Higher priority items override lower. Project rules override user rules.

---

## Project Rules Structure

### Basic Setup

```
my-project/
├── CLAUDE.md                    # Shared project docs (git-tracked)
├── .claude/
│   ├── CLAUDE.local.md          # Environment-specific (AUTO-GITIGNORED)
│   ├── CLAUDE.local.md.example  # Template for new clones (git-tracked)
│   └── rules/
│       ├── architecture.md      # Shared rules (git-tracked)
│       ├── api-patterns.md
│       └── testing.md
└── .gitignore
```

### Content Split

**CLAUDE.md (git-tracked):**
- Project overview, tech stack
- Architecture, patterns
- Development commands (generic)
- Code structure documentation

**CLAUDE.local.md (auto-gitignored):**
- Account IDs, API endpoints
- 1Password paths
- Environment-specific secrets
- Local deployment commands

---

## User-Level Environment Configs

### Setup

Create environment-specific configs at user level for reuse across projects:

```
~/.claude/
├── CLAUDE.md                          # Global preferences
└── rules/
    └── environments/
        ├── cloudflare-personal.md     # Personal Cloudflare
        ├── cloudflare-work.md         # Work Cloudflare
        └── aws-personal.md            # Personal AWS
```

### Example Environment File

```markdown
# ~/.claude/rules/environments/cloudflare-personal.md

# Personal Cloudflare Environment

## Account Details
| Setting | Value |
|---------|-------|
| Account | Your Name (Personal) |
| Account ID | `<your-cloudflare-account-id>` |

## 1Password Paths
| Secret | Path |
|--------|------|
| API Token | `op://<vault>/<item>/API Token` |
| Admin Key | `op://<vault>/<item>/Admin Key` |

## Deployment
\`\`\`bash
CLOUDFLARE_API_TOKEN=$(op read "op://<vault>/<item>/API Token" --account <your-account>.1password.com) \
CLOUDFLARE_ACCOUNT_ID="<your-cloudflare-account-id>" \
pnpm run deploy
\`\`\`
```

---

## @import Pattern

Import environment configs into project-local files:

### In CLAUDE.local.md

```markdown
# Local Environment Configuration

@~/.claude/rules/environments/cloudflare-personal.md
```

### In CLAUDE.md (for always-on imports)

```markdown
# Project Documentation

## Overview
...

## Environment Setup
@~/.claude/rules/environments/cloudflare-personal.md
```

### Import Rules

- Max 5 hops for recursive imports
- Paths can be absolute or relative
- `~` expands to home directory
- Missing files are skipped gracefully

---

## Path-Specific Rules

Make rules conditional with YAML frontmatter:

### Syntax

```markdown
---
paths: src/**/*.ts
---

# TypeScript Rules

These rules ONLY apply to .ts files in src/
```

### Glob Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.ts` | All TypeScript files |
| `src/**/*` | All files under src/ |
| `*.md` | Markdown in root only |
| `**/*.{ts,tsx}` | Both .ts and .tsx |
| `{src,lib}/**/*.ts` | TypeScript in src/ OR lib/ |
| `tests/**/*.test.ts` | Test files only |

### Examples

**API endpoint rules:**
```markdown
---
paths: src/api/**/*.ts
---

# API Development Rules

- Validate all inputs with Zod
- Return typed responses
- Include error handling
```

**Component rules:**
```markdown
---
paths: src/components/**/*.tsx
---

# React Component Rules

- Functional components only
- Export props interface
- One component per file
```

---

## Multi-Repo Workflow

For projects shared between personal and work repos:

### Single Local Repo, Multiple Remotes

```bash
# Setup
git remote add personal git@github.com:your-username/my-project.git
git remote add work git@github.com:your-org/my-project.git

# Push to both (code syncs, CLAUDE.local.md stays local)
git push personal main
git push work main
```

### Structure

```
my-project/
├── CLAUDE.md                    # Shared (git-tracked, pushed to both)
├── .claude/
│   ├── CLAUDE.local.md          # Environment-specific (auto-gitignored)
│   ├── CLAUDE.local.md.example  # Template (git-tracked)
│   └── rules/                   # Shared rules (git-tracked)
```

### Workflow

1. **Personal clone:** Create `.claude/CLAUDE.local.md` with personal config
2. **Work clone:** Create `.claude/CLAUDE.local.md` with work config
3. **Both use @import:** `@~/.claude/rules/environments/[appropriate-env].md`

---

## Symlinks

Share rules across projects with symlinks:

### Directory Symlink

```bash
# Share entire rules directory
ln -s ~/shared-claude-rules ~/.claude/rules/shared
```

### File Symlink

```bash
# Share individual rule
ln -s ~/.claude/rules/environments/cloudflare-personal.md \
      ~/projects/my-project/.claude/rules/environment.md
```

### Notes

- Circular symlinks handled gracefully
- Missing targets skipped
- Works across projects

---

## Quick Reference

| What | Where | Git Status |
|------|-------|------------|
| Shared project docs | `./CLAUDE.md` | Tracked |
| Shared project rules | `./.claude/rules/*.md` | Tracked |
| Environment secrets | `./.claude/CLAUDE.local.md` | **Auto-ignored** |
| Setup template | `./.claude/CLAUDE.local.md.example` | Tracked |
| User defaults | `~/.claude/rules/*.md` | N/A |
| Environment configs | `~/.claude/rules/environments/*.md` | N/A |

---

*Patterns for TypeScript/Cloudflare Workers projects with multi-environment support.*
*Last updated: 2026-01-10*
