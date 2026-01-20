# Rules and Content Placement Guide

**Complete guide for placing content across CLAUDE.md, rules, skills, and project files**

---

## Overview

Claude Code supports multiple instruction file types with different loading behaviors and scopes. This guide helps you decide where to place different types of content for optimal organization, token efficiency, and team sharing.

**Key Insight:** The primary distinction is **auto-loading vs on-demand**:
- **Auto-loading**: CLAUDE.md files and rules always load every session
- **On-demand**: Skills and agents load when invoked or triggered

---

## Instruction Loading Hierarchy

Claude Code loads instructions in this order (later overrides earlier):

| Order | Source | Scope | Loading |
|-------|--------|-------|---------|
| 1 | `~/.claude/CLAUDE.md` | Global | Always |
| 2 | `~/.claude/rules/**/*.md` | Global | Always |
| 3 | `./CLAUDE.md` | Project | In project |
| 4 | `./.claude/rules/**/*.md` | Project | In project |
| 5 | `./CLAUDE.local.md` | Personal | In project |
| 6 | `./subdir/CLAUDE.md` | Subdirectory | When navigated |

**Critical Behaviors:**
- **Rules always fully load** - no lazy loading, no incremental loading
- **`@import` fully loads content** - it is NOT lazy, the entire imported file loads
- **Only nested subdirectory CLAUDE.md** provides conditional loading (when you navigate to that directory)
- Rules load alphabetically within directories

---

## Auto-Loading Content Types

### CLAUDE.md Files

**Behavior:** Always load based on scope (global, project, subdirectory)

**Best For:**
- Core user identity and preferences
- Behavioral instructions and communication style
- Critical conventions used every session
- Integration of other instruction sources

**Sizing Guidelines:**
| Type | Recommended Size | Maximum |
|------|-----------------|---------|
| Global CLAUDE.md | 800-1200 lines | ~1500 lines |
| Project CLAUDE.md | 100-300 lines | ~500 lines |
| CLAUDE.local.md | 50-150 lines | ~300 lines |

### Rules Files

**Behavior:** Always fully load when in scope (global or project)

**Location:** `~/.claude/rules/` (global) or `./.claude/rules/` (project)

**Best For:**
- Small, focused configuration (50-200 lines each)
- Cross-cutting concerns (credentials, paths, accounts)
- Reusable patterns across projects
- Team-shareable configurations

**Common Directory Patterns:**
```
~/.claude/rules/
├── environments/       # Cloud accounts, API configs
│   ├── cloudflare.md
│   ├── 1password-work.md
│   └── 1password-personal.md
├── languages/          # Language-specific conventions
│   ├── typescript.md
│   └── python.md
└── tools/              # Tool-specific configs
    └── git.md
```

**Benefits of Rules over Monolithic CLAUDE.md:**
- **Organization**: Logical grouping by category
- **Reusability**: Share specific rules across projects
- **Selective Sharing**: Include some rules in team repos, keep others private
- **Maintenance**: Update one rule file without touching others
- **Override Hierarchy**: Project rules override global rules

---

## On-Demand Content Types

### Skills

**Behavior:** Load via `/skill-name`, `Skill` tool, or semantic auto-trigger from description

**Loading Pattern:** Progressive disclosure
1. Skill description checked for auto-trigger matching
2. SKILL.md loads when skill is invoked
3. `references/` files load only when Claude determines they're needed

**Best For:**
- Large documentation (unlimited size in references/)
- Domain-specific knowledge bundles
- Bundled scripts and templates
- Token-efficient optional content

**Structure:**
```
skill-name/
├── SKILL.md           # Overview, quick reference (100-500 lines)
└── references/        # Detailed docs, load as needed (unlimited)
    ├── guide-1.md
    └── guide-2.md
```

### Agents

**Behavior:** Load via Task tool or auto-trigger from "Use PROACTIVELY" in description

**Best For:**
- Autonomous operations requiring delegation
- Complex multi-step workflows
- Business context integration
- Proactive monitoring and optimization

---

## Content Placement Decision Matrix

| Content Type | Recommended Location | Rationale |
|--------------|---------------------|-----------|
| **User identity/preferences** | Global CLAUDE.md | Core behavior, always needed |
| **Small cross-cutting config** (~50-100 lines) | `rules/environments/` | Always available, organized |
| **API keys, account IDs, paths** | `rules/environments/` | Cross-cutting, sensitive |
| **Large domain documentation** (>200 lines) | Skill `references/` | On-demand, token efficient |
| **Project-specific context** | Project CLAUDE.md | Scoped to project |
| **Project-specific patterns** | Project `rules/` | Organized, reusable within project |
| **Personal overrides** | CLAUDE.local.md | Gitignored, personal |
| **Team-shareable patterns** | Skills (sanitized) | Portable, versionable |
| **Sensitive credentials** | Global rules (not synced) | Protected from team sharing |

---

## Config/Environment Placement Patterns

### Cloud Provider Credentials

**Location:** `~/.claude/rules/environments/`

**Pattern:** One file per account/provider
```markdown
# cloudflare-account-name.md

## Account Details
| Setting | Value |
|---------|-------|
| Account ID | `xxx` |
| Primary Zone | domain.com |

## API Tokens
| Token | Scope | Path |
|-------|-------|------|
| Read All | Read access | `op://Vault/Item/Field` |

## Usage Examples
[Code snippets]
```

**Why Rules:** Small (~50-100 lines), cross-cutting (needed in many projects), always available.

### Path Registries

**For Global Paths:** `~/.claude/rules/environments/paths.md`
```markdown
# paths.md
| Alias | Path |
|-------|------|
| mb | ~/Obsidian/memory-bank |
| repos | ~/repos |
```

**For Project Paths:** Project CLAUDE.md
```markdown
## Project Paths
- Source: `./src`
- Tests: `./tests`
```

### Infrastructure Documentation

**Location:** Skills with `references/`

**Example:** `infra-hc` skill
```
infra-hc/
├── SKILL.md                    # Quick reference, SSH commands
└── references/
    ├── hosts/                  # Host configurations
    ├── network/                # Network topology
    └── services/               # Service documentation
```

**Why Skill:** Large documentation (potentially 1000s of lines), load only when working on infrastructure.

### Project Tech Stack

**Recommendation:** Let Claude read actual config files

Instead of duplicating in skill references:
```markdown
# DON'T: Duplicate project config in skill
references/tech-stack/my-project.md  # 500 lines duplicating package.json
```

**DO:** Reference that Claude can read source files:
```markdown
# Project uses TypeScript + React
See package.json for dependencies, tsconfig.json for compiler options.
```

---

## Token Budget Guidelines

### Auto-Loading Budget

Since CLAUDE.md and rules always load, budget carefully:

| Component | Budget | Notes |
|-----------|--------|-------|
| Global CLAUDE.md | 800-1200 lines | Core identity only |
| Global rules (total) | 300-500 lines | Split across files |
| Project CLAUDE.md | 100-300 lines | Project context only |
| Project rules (total) | 100-200 lines | Project patterns |

**Total auto-load target:** <2000 lines

### On-Demand Budget

Skills have more flexibility since they load when needed:

| Component | Budget | Notes |
|-----------|--------|-------|
| SKILL.md | 100-500 lines | Overview + quick ref |
| Each reference file | Unlimited | Load as needed |

**Key Principle:** Keep auto-loading content lean. Move large documentation to skills.

---

## Decision Tree

```
Where should this content go?
│
├─ Needed EVERY session regardless of project?
│  ├─ YES, and it's core identity/behavior → Global CLAUDE.md
│  ├─ YES, and it's config/credentials → Global rules/environments/
│  └─ NO → Continue
│
├─ Project-specific?
│  ├─ YES, and essential context → Project CLAUDE.md
│  ├─ YES, and reusable pattern → Project rules/
│  └─ NO → Continue
│
├─ Large documentation (>200 lines)?
│  ├─ YES → Skill references/
│  └─ NO → Continue
│
├─ Domain-specific with related resources?
│  ├─ YES → Skill (SKILL.md + references/)
│  └─ NO → Continue
│
├─ Personal/private content?
│  ├─ YES → Global rules or CLAUDE.local.md
│  └─ NO → Continue
│
├─ Team-shareable?
│  ├─ YES → Skills (sanitized) in team repo
│  └─ NO → Global rules (not synced)
│
└─ Default: Start with smallest scope, expand only if needed
```

---

## Common Scenarios

### Scenario 1: API Credentials for Cloud Provider
**Decision:** Global `rules/environments/provider.md`
- Small (~50-100 lines)
- Needed across many projects
- Cross-cutting concern
- Keep with other environment configs

### Scenario 2: Infrastructure Documentation (Hosts, Networks, Services)
**Decision:** Skill with `references/`
- Large documentation (potentially 1000s of lines)
- Domain-specific bundle
- Load only when doing infrastructure work
- Progressive disclosure

### Scenario 3: Language Coding Standards
**Decision:** Skill (e.g., `typescript/`, `python/`)
- Bundled patterns and templates
- Reference documentation
- Load when working in that language
- Team-shareable

### Scenario 4: Project-Specific Tech Stack Context
**Decision:** Project CLAUDE.md
- Specific to one project
- Provides context for Claude
- Auto-loads when in project
- Consider: Claude can read package.json, pyproject.toml directly

### Scenario 5: Personal Project Documentation
**Decision:** Project CLAUDE.md in that repo
- NOT in global skills (keeps skills team-shareable)
- NOT in global rules (project-specific)
- Local to that project's context

### Scenario 6: Multi-Account Credentials (Work vs Personal)
**Decision:** Separate files in `rules/environments/`
- `1password-work.md` - work account defaults
- `1password-personal.md` - personal account with flags
- Clear separation, both always available

### Scenario 7: Rarely-Used Reference Documentation
**Decision:** Skill `references/` or delete
- If needed occasionally → skill reference
- If duplicates source files → delete (Claude reads source)
- Don't put in auto-loading locations

---

## Team Sharing Considerations

### Separation of Personal vs Shareable Content

| Personal (Keep Private) | Shareable (Sync to Team) |
|------------------------|-------------------------|
| Account IDs, API tokens | Generic patterns |
| Personal file paths | Templates with placeholders |
| Personal project references | Domain knowledge |
| Credential 1Password paths | Best practices |
| Personal preferences | Coding standards |

### Sanitization Checklist

Before syncing a skill to team repos:

- [ ] No personal file paths (e.g., `/Users/yourname/`)
- [ ] No personal account IDs or tokens
- [ ] No personal project references
- [ ] No personal 1Password/secret paths
- [ ] Generic examples, not personal data
- [ ] Placeholders for personal config (`YOUR_ACCOUNT_ID`)
- [ ] No personal preference specifics

### Where Personal Content Goes

| Content | Location | Why |
|---------|----------|-----|
| Personal credentials | Global `rules/environments/` | Never synced, always available |
| Personal paths | Global `rules/environments/paths.md` | Cross-cutting, private |
| Personal overrides | CLAUDE.local.md | Gitignored per project |
| Personal project context | That project's CLAUDE.md | Scoped appropriately |

---

## Duplication Avoidance Strategies

### Anti-Pattern: Same Content in Multiple Places
```
# DON'T
~/.claude/CLAUDE.md: Contains Cloudflare account config
~/.claude/rules/environments/cloudflare.md: Same Cloudflare config again
```

**Solution:** Pick one location, reference it if needed elsewhere.

### Anti-Pattern: Skill References Duplicate Source Files
```
# DON'T
skill/references/my-project-config.md: Copy of package.json info
```

**Solution:** Delete reference. Claude can read actual package.json.

### Anti-Pattern: Project Context in Global Files
```
# DON'T
~/.claude/skills/typescript/references/my-personal-project.md
```

**Solution:** Move to that project's CLAUDE.md.

### Audit Strategy

Periodically check for:
1. Overlap between CLAUDE.md and rules files
2. Skill references that duplicate actual project files
3. Global files containing project-specific content
4. Multiple copies of credentials/paths

---

## Migration Patterns

### CLAUDE.md → Rules

When CLAUDE.md becomes too large:

1. Identify focused sections (credentials, paths, tool configs)
2. Extract to `rules/environments/section-name.md`
3. Remove from CLAUDE.md
4. Verify rules load correctly

### CLAUDE.md → Skill

When documentation is too large for auto-loading:

1. Identify large reference sections (>200 lines)
2. Create skill with `references/` directory
3. Move documentation to skill references
4. Keep brief overview in CLAUDE.md or skill SKILL.md

### Skill → Rules

When small config should always load:

1. Identify small cross-cutting config in skill
2. Extract to `rules/environments/`
3. Remove from skill references
4. Update skill to reference rules location if needed

### Global → Project

When content is project-specific:

1. Identify project-specific content in global files
2. Move to project CLAUDE.md or project rules
3. Remove from global location
4. Verify project-specific behavior works

---

## Anti-Patterns to Avoid

**Mega CLAUDE.md (>2000 lines)**
- Split into focused rules files
- Move large documentation to skills
- Keep CLAUDE.md for core identity only

**Personal Content in Team Skills**
- Keep personal paths, accounts in global rules
- Use CLAUDE.local.md for project-specific personal overrides
- Sanitize skills before syncing to team repos

**Duplicating Actual Project Files**
- Delete skill references that copy package.json, pyproject.toml, etc.
- Claude can read source files directly
- Only document patterns/guidance, not config duplication

**Rules for Rarely-Needed Content**
- Move to skills for on-demand loading
- Rules always load, consuming token budget
- Reserve rules for frequently-needed small content

**All Config in CLAUDE.md**
- Split environment config to `rules/environments/`
- Organize by category (cloud providers, credentials, paths)
- Keep CLAUDE.md focused on behavior/identity

**Project Context in Global Files**
- Keep project-specific content in project scope
- Don't pollute global skills with personal projects
- Use project CLAUDE.md for project context

**Assuming @import is Lazy**
- `@import` fully loads content immediately
- There is NO lazy loading mechanism for @import
- For lazy/on-demand loading, use skills with references/

---

## Summary Table

| Instruction Type | Loading | Scope | Token Budget | Best For |
|-----------------|---------|-------|--------------|----------|
| Global CLAUDE.md | Always | All sessions | ~1000 lines | Core identity |
| Global rules | Always | All sessions | ~50-200 each | Cross-cutting config |
| Project CLAUDE.md | In project | One project | ~100-300 lines | Project context |
| Project rules | In project | One project | ~50-100 each | Project patterns |
| CLAUDE.local.md | In project | Personal | ~50-150 lines | Personal overrides |
| Skill SKILL.md | On invoke | When needed | ~100-500 lines | Overview + quick ref |
| Skill references | On demand | When needed | Unlimited | Large documentation |
| Agents | On trigger | When needed | ~200-500 lines | Autonomous delegation |

**Key Principle:** Auto-loading content should be lean and frequently-needed. Large or occasionally-needed content belongs in skills for on-demand loading.

---

**Last Updated:** 2026-01-20
**Use Case:** Content placement decisions for CLAUDE.md, rules, skills, and project files
