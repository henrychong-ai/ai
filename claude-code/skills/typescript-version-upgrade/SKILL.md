---
name: typescript-version-upgrade
description: This skill should be used for upgrading Node.js, TypeScript, and framework versions with production-grade safety protocols. Use for CVE remediation, LTS upgrades, TypeScript migrations, Next.js upgrades, and multi-repository version standardization. Triggers on version upgrade, node upgrade, typescript migration, CVE patch, security update, framework migration.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# TypeScript Version Upgrade Skill

Comprehensive version upgrade orchestration for Node.js, TypeScript, and framework migrations with production-grade safety protocols.

## When to Use This Skill

- Upgrading Node.js versions (especially for CVE remediation)
- Legacy Node.js migrations (12.x, 14.x, 16.x EOL systems)
- Migrating TypeScript versions (4.x → 5.x)
- Upgrading framework versions (Next.js, React, etc.)
- Multi-repository version standardization
- Security-critical production application upgrades

## CRITICAL: Production Safety Warning

**This skill handles upgrades for live production applications involving financial transactions and cryptocurrency operations.**

### Mandatory Safety Requirements

1. **NEVER skip testing phases** - Every upgrade must pass full test suite
2. **ALWAYS create rollback plan** before any changes
3. **REQUIRE explicit user approval** before committing changes
4. **VALIDATE no behavior changes** in business-critical logic
5. **CHECK CI/CD pipelines** pass before considering upgrade complete

## Operation Modes

### Mode 1: ANALYZE (Default)
Assess repository for upgrade requirements without making changes.

**Outputs:**
- Current version inventory
- Required upgrades with rationale
- Risk assessment
- Estimated effort

### Mode 2: PLAN
Create detailed upgrade plan with specific steps.

**Outputs:**
- Ordered upgrade sequence
- File-by-file change inventory
- Testing checkpoints
- Rollback procedures

### Mode 3: EXECUTE
Perform upgrades with validation gates.

**Requires:** User approval at each critical checkpoint

## Detection Matrix

| Trigger | Detection Method | Action |
|---------|------------------|--------|
| `.nvmrc` present | Read file | Check if version < target |
| `.node-version` present | Read file | Check if version < target |
| `package.json engines.node` | Parse JSON | Check version constraint |
| `Dockerfile FROM node:` | Grep pattern | Check base image version |
| `tsconfig.json` | Parse JSON | Check TypeScript settings |
| `next.config.js/ts` | Read file | Check Next.js patterns |

## Upgrade Execution Protocol

### Phase 1: Pre-Flight Checks

```bash
# 1. Verify clean git state
git status --porcelain

# 2. Create safety branch
git checkout -b upgrade/node-XX-to-YY-$(date +%Y%m%d)

# 3. Document current state
node --version > .upgrade-baseline
npm test 2>&1 | tee .upgrade-test-baseline
```

### Phase 2: Version File Updates

**Priority Order:**
1. `.nvmrc` - Primary version specification
2. `.node-version` - Secondary version specification
3. `package.json engines` - Constraint validation
4. `Dockerfile` - Container builds
5. CI/CD pipelines - Build environments

### Phase 3: Dependency Resolution

```bash
# Clear node_modules and lockfile
rm -rf node_modules pnpm-lock.yaml

# Reinstall with new Node version
nvm use && pnpm install

# Check for peer dependency warnings
pnpm install 2>&1 | grep -i "peer"
```

### Phase 4: Code Migration

Load version-specific guide from `references/`:
- Node upgrades: `references/node/node-{FROM}-to-{TO}.md`
- TypeScript upgrades: `references/typescript/typescript-{VERSION}.md`
- Framework upgrades: `references/frameworks/{framework}-migrations.md`

### Phase 5: Validation Gates

**Gate 1: Compilation**
```bash
pnpm build
# Must exit 0 with no errors
```

**Gate 2: Type Checking**
```bash
pnpm exec tsc --noEmit
# Must exit 0 with no errors
```

**Gate 3: Linting**
```bash
pnpm lint
# Must exit 0 with no errors
```

**Gate 4: Unit Tests**
```bash
pnpm test
# Must pass all tests
# Compare coverage to baseline
```

**Gate 5: Integration Tests (if applicable)**
```bash
pnpm test:integration
# Must pass all tests
```

### Phase 6: User Approval Checkpoint

**STOP AND REPORT:**
- Changes made (file diff summary)
- Test results comparison
- Any warnings or deprecations
- Recommendation to proceed or rollback

**Wait for explicit user approval before committing.**

### Phase 7: Commit and Document

```bash
git add -A
git commit -m "chore: upgrade Node.js from X to Y

- Updated .nvmrc to Y
- Updated package.json engines constraint
- Updated Dockerfile base image
- Resolved [N] deprecation warnings
- All tests passing

Addresses: CVE-XXXX-XXXXX (if applicable)"
```

## AI Safety Guardrails

**Load `references/safety/ai-guardrails.md` for detailed protocols.**

### Known AI Refactoring Risks

| Risk | Mitigation |
|------|------------|
| Hallucinated APIs | Verify every API call against official docs |
| Context limit issues | Process files individually, not bulk |
| Business logic drift | Assert "no behavior change" explicitly |
| Missing edge cases | Review test coverage before/after |
| Optimistic transformations | Conservative approach, minimal changes |

### Prohibited Actions

1. **NEVER** refactor business logic during version upgrade
2. **NEVER** change function signatures unless required by upgrade
3. **NEVER** remove tests or reduce coverage
4. **NEVER** skip failing tests with comments
5. **NEVER** commit without user approval

### Required Assertions

Before any code change, state explicitly:
- "This change is required for [version] compatibility because [reason]"
- "This change does NOT modify business logic"
- "Existing tests cover this change"

## Reference Files

Load as needed based on upgrade type:

### Node.js Migrations
- `references/node/migration-overview.md` - General Node.js upgrade principles
- `references/node/node-12-to-24.md` - **Node 12 → 24 (EXTREMELY CRITICAL EOL migration, 12 major versions, 3+ years EOL)**
- `references/node/node-16-to-24.md` - **Node 16 → 24 (CRITICAL EOL migration, 8 major versions)**
- `references/node/node-20-to-22.md` - Node 20 → 22 specific changes
- `references/node/node-22-to-24.md` - Node 22 → 24 specific changes

### React Migrations
- `references/react/react-16-to-19.md` - **React 16 → 19 (major migration, 3 versions)**
- `references/react/react-17-to-19.md` - React 17 → 19 (2 version jump)
- `references/react/react-18-to-19.md` - React 18 → 19 (focused upgrade)

### TypeScript Migrations
- `references/typescript/typescript-4-to-5.md` - TS 4.x → 5.x migration

### Framework Migrations
- `references/frameworks/nextjs-migrations.md` - Next.js version upgrades

### Safety Protocols
- `references/safety/ai-guardrails.md` - AI-specific safety protocols
- `references/safety/testing-protocols.md` - Testing requirements

## Quick Reference: Version Targets

### Node.js (CVE-2025-59466 Compliant)
| LTS Line | Minimum Safe Version |
|----------|---------------------|
| v24.x | 24.13.0+ |
| v22.x | 22.22.0+ |
| v20.x | 20.20.0+ |
| v18.x | EOL - Must upgrade |
| v16.x | EOL - Critical upgrade |
| v14.x | EOL (Apr 2023) - Critical upgrade |
| v12.x | EOL (Apr 2022) - EMERGENCY upgrade |

### TypeScript
| Target | Minimum Version |
|--------|-----------------|
| Modern | 5.0+ |
| Legacy | 4.9.x (deprecated) |

### React
| From Version | Target | Migration Complexity |
|--------------|--------|---------------------|
| React 16.x | 19.x | 🔴 High - Major APIs removed |
| React 17.x | 19.x | 🟠 Medium - createRoot + defaults |
| React 18.x | 19.x | 🟢 Low - Focused changes |

### Fusang Repo Version Inventory
| Repository | Node | React | Priority |
|------------|------|-------|----------|
| fusang-swap-v2-info | 16 (EOL!) | 16.9 | 🔴 CRITICAL |
| fusang-swap-v2-interface | - | 17.0 | 🟠 HIGH |
| web3auth_core_kit_example | - | 18.3 | 🟡 MEDIUM |
| styx | - | 19.0 | ✅ Current |

## Example Usage

### Analyze Repository
```
Use typescript-version-upgrade skill to analyze this repository for version upgrades needed.
```

### Plan Upgrade
```
Use typescript-version-upgrade skill to plan Node.js upgrade from 20 to 24 for this project.
```

### Execute Upgrade
```
Use typescript-version-upgrade skill to execute the planned Node.js upgrade with full testing.
```

## Integration Notes

- Works with `/lint` skill for post-upgrade linting setup
- References `/typescript` skill patterns for code conventions
- Uses TodoWrite for tracking multi-step upgrade progress
- Creates backup branch before any modifications

---

**Remember: Financial applications require zero tolerance for upgrade-induced bugs. When in doubt, do less and verify more.**
