# Migration Guide: ESLint+Prettier to Oxlint+Biome

Reference for migrating TypeScript/JavaScript projects from ESLint + Prettier to the Oxlint + Biome + (residual ESLint) stack. Contains rationale, architecture comparison, and a CC-executable autonomous migration protocol.

---

## Why We Migrated

### Performance (50-100x faster)

Oxlint is written in Rust. It is 50-100x faster than ESLint on the same codebase. Biome (also Rust) is 25x faster than Prettier. On large projects, lint times drop from seconds to milliseconds. No caching required.

### Dependency Reduction

| Scenario | Before (ESLint+Prettier) | After (Oxlint+Biome) | Reduction |
|----------|--------------------------|----------------------|-----------|
| Bare minimum TS project | 13 packages | **3 packages** | -77% |
| React project | 16 packages | **3 packages** | -81% |
| Next.js project | 17 packages | **3 packages** | -82% |
| Vue project | 14 packages | **5 packages** | -64% |
| Next.js + Tailwind + Vitest | 19 packages | **7 packages** | -63% |
| Kitchen sink (all plugins) | 30 packages | **12 packages** | -60% |

Fewer dependencies means fewer version conflicts, faster installs, smaller lock files, and reduced supply chain risk.

### Simpler Architecture

The old stack required understanding ESLint's plugin ecosystem, parser configuration, and Prettier's integration quirks (eslint-config-prettier to disable conflicting rules, Prettier plugin ordering, etc.).

The new stack has a clean 4-layer separation:

| Layer | Tool | Responsibility |
|-------|------|----------------|
| 1 | **Oxlint** | All linting (668 rules, native plugins) |
| 2 | **Biome** | All formatting + import sorting |
| 3 | **Residual ESLint** | Gap plugins only (Vue templates, Astro, etc.) |
| 4 | **tsc** | Type checking (unchanged) |

Each tool does one job. No overlap, no conflict resolution needed.

### Native Plugin Architecture

Oxlint bundles 14 plugin equivalents with zero npm dependencies:

| Oxlint Plugin | Replaces | Rules |
|---------------|----------|-------|
| `eslint` (core) | ESLint core | ~200 |
| `typescript` | @typescript-eslint | ~90 |
| `unicorn` | eslint-plugin-unicorn | ~100 |
| `oxc` (deepscan) | eslint-plugin-sonarjs (partial) | ~30 |
| `import` | eslint-plugin-import | ~25 |
| `promise` | eslint-plugin-promise | ~15 |
| `react` + hooks | eslint-plugin-react + react-hooks | ~40 |
| `react-perf` | (new) | ~6 |
| `nextjs` | @next/eslint-plugin-next | ~15 |
| `jsx-a11y` | eslint-plugin-jsx-a11y | ~30 |
| `node` | eslint-plugin-n | ~20 |
| `vitest` | eslint-plugin-vitest | ~15 |
| `jest` | eslint-plugin-jest | ~25 |
| `jsdoc` | (optional) | ~20 |

To enable a plugin, add its name to the `plugins` array in `oxlint.json`. No `pnpm add -D` required.

### Prettier Elimination

Biome replaces Prettier entirely with:
- Prettier-compatible formatting settings (same output)
- Built-in import sorting (`assist.actions.source.organizeImports` in Biome 2.x) -- replaces `eslint-plugin-import` order rules and `@trivago/prettier-plugin-sort-imports`
- Linter disabled (Oxlint handles all linting, preventing any overlap)
- This also eliminates `eslint-config-prettier` (which existed solely to disable ESLint rules that conflicted with Prettier)

---

## Architecture Comparison

### Before: ESLint + Prettier (13+ core packages)

```
ESLint (monolithic linter)
  + @typescript-eslint/eslint-plugin
  + @typescript-eslint/parser
  + typescript-eslint
  + @stylistic/eslint-plugin
  + eslint-plugin-import
  + eslint-plugin-unicorn
  + eslint-plugin-sonarjs
  + eslint-plugin-promise
  + eslint-config-prettier
  + (conditional: react, react-hooks, jsx-a11y, @next, vue, vitest, jest, playwright, etc.)

Prettier (formatter)
  + prettier-plugin-tailwindcss
  + (other Prettier plugins)
```

### After: Oxlint + Biome (3 core packages)

```
Oxlint (primary linter) .............. 668 built-in rules, 14 native plugins, ZERO npm deps
Biome (formatter only) ............... Prettier-compatible, import sorting, linter disabled
TypeScript (type checker) ............ Unchanged

Residual ESLint (gap plugins only) ... Only when Vue/Astro/Tailwind/Playwright/Obsidian/Compat needed
```

### What's Still ESLint (Residual Layer)

ESLint is only needed when a project uses one of these "gap" plugins:

| Plugin | When Needed | Why Not Oxlint |
|--------|-------------|----------------|
| `eslint-plugin-vue` | Vue projects | Oxlint lints `<script>` but not `<template>` directives |
| `eslint-plugin-astro` | Astro projects | Oxlint can't parse `.astro` files |
| `eslint-plugin-better-tailwindcss` | Tailwind v4 | No Tailwind rules in Oxlint; also replaces `prettier-plugin-tailwindcss` |
| `eslint-plugin-playwright` | Playwright E2E | Not yet ported to Oxlint |
| `eslint-plugin-obsidianmd` | Obsidian plugins | Too niche for Oxlint |
| `eslint-plugin-compat` | Frontend + browserslist | No browser compat rules in Oxlint |

When residual ESLint is used, `eslint-plugin-oxlint` automatically disables all ESLint rules that Oxlint already covers, preventing duplicate checking.

**For projects without these frameworks (plain TS, React, Next.js, Node.js, Vitest, Jest), ESLint is not installed at all.**

---

## CC Autonomous Migration Protocol

**Purpose**: Enable Claude Code to autonomously analyse and migrate any TypeScript/JavaScript repository from ESLint + Prettier to Oxlint + Biome + (residual ESLint).

**Execution Mode**: Follow phases sequentially. Each phase produces findings that inform the next. Present checkpoints to user before proceeding to destructive steps.

---

### Phase 1: Pre-Migration Analysis

#### 1.1 Detect ESLint Configuration

Read the project root to find which ESLint config format is in use:

```
PRIORITY ORDER:
1. eslint.config.js / eslint.config.mjs / eslint.config.cjs  →  "flat config"
2. .eslintrc.js / .eslintrc.cjs / .eslintrc.json / .eslintrc.yaml / .eslintrc.yml  →  "legacy config"
3. "eslintConfig" key in package.json  →  "inline config"
4. None found  →  "no config" (fresh setup)
```

Read the ESLint config file to extract:
- Installed plugins (from `plugins` array or extended configs)
- Custom rules (from `rules` object)
- Parser configuration
- Overrides and file-specific configs

#### 1.2 Detect Prettier Configuration

Search for Prettier config in this order:
- `.prettierrc` / `.prettierrc.json` / `.prettierrc.js` / `.prettierrc.cjs` / `.prettierrc.yaml` / `.prettierrc.yml`
- `prettier.config.js` / `prettier.config.cjs`
- `"prettier"` key in `package.json`

Also check for `.prettierignore`.

Read the Prettier config to extract formatting settings (these map to biome.json later).

#### 1.3 Analyse Dependencies

Read `package.json` devDependencies and dependencies. Extract all packages matching:
- `eslint*`
- `@typescript-eslint/*`
- `@stylistic/*`
- `@next/eslint-plugin-next`
- `prettier*`
- `@trivago/prettier-plugin-sort-imports`
- `@ianvs/prettier-plugin-sort-imports`

Count total ESLint/Prettier related packages for before/after comparison.

#### 1.4 Detect Frameworks and Tools

Analyse `package.json` dependencies and file structure:

| Check | Indicator | Framework |
|-------|-----------|-----------|
| `"react"` in deps | React detected | Enable oxlint `react`, `jsx-a11y` plugins |
| `"next"` in deps OR `next.config.*` exists | Next.js detected | Enable oxlint `react`, `jsx-a11y`, `nextjs` plugins |
| `"vue"` in deps | Vue detected | **Residual ESLint** needed for `eslint-plugin-vue` |
| `"astro"` in deps OR `astro.config.*` exists | Astro detected | **Residual ESLint** needed for `eslint-plugin-astro` |
| `"express"/"fastify"/"hono"/"koa"` in deps | Node.js backend | Enable oxlint `node` plugin |
| `"vitest"` in devDeps | Vitest detected | Enable oxlint `vitest` plugin |
| `"jest"` in devDeps | Jest detected | Enable oxlint `jest` plugin |
| `"@playwright/test"` in devDeps | Playwright detected | **Residual ESLint** needed for `eslint-plugin-playwright` |
| `"tailwindcss"` in deps | Tailwind detected | **Residual ESLint** needed for `eslint-plugin-better-tailwindcss` |
| `manifest.json` with `minAppVersion` | Obsidian plugin | **Residual ESLint** needed for `eslint-plugin-obsidianmd` |
| `"browserslist"` in package.json OR `.browserslistrc` | Browserslist | **Residual ESLint** needed for `eslint-plugin-compat` |

**Key determination**: Does this project need residual ESLint? Only if Vue, Astro, Tailwind, Playwright, Obsidian, or Compat is detected.

#### 1.5 Detect Tooling Integrations

Check for:
- **Pre-commit hooks**: `.husky/` directory, `"husky"` in package.json
- **lint-staged**: `"lint-staged"` in package.json, `.lintstagedrc*` files, `lint-staged.config.*` files
- **CI/CD**: `.github/workflows/*.yml`, `bitbucket-pipelines.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`
- **VSCode**: `.vscode/settings.json`
- **EditorConfig**: `.editorconfig`

#### 1.6 Generate Analysis Report

Present findings to user:

```
=== Pre-Migration Analysis ===

ESLint Config: [format] ([file])
Prettier Config: [file] (or "None")
Package Manager: pnpm | yarn | npm
Total ESLint/Prettier deps: [count]

Detected Frameworks: [list]
Oxlint Plugins to Enable: [list]

Residual ESLint Needed: YES/NO
  Gap Plugins: [list or "None"]

Tooling:
  Pre-commit: [husky + lint-staged / none]
  CI/CD: [files found]
  VSCode: [yes/no]

Custom ESLint Rules: [count] (will map in Phase 5)
```

**Checkpoint**: Present analysis. Confirm with user before proceeding.

---

### Phase 2: Plugin Mapping

Classify every installed ESLint/Prettier dependency into one of four actions:

#### REMOVE (replaced by Oxlint native plugins)

| Old Package | Oxlint Replacement |
|-------------|-------------------|
| `eslint` | Oxlint core |
| `@typescript-eslint/eslint-plugin` | Oxlint `typescript` plugin |
| `@typescript-eslint/parser` | Oxlint's own parser |
| `typescript-eslint` | Oxlint `typescript` plugin |
| `@stylistic/eslint-plugin` | Oxlint style categories |
| `@stylistic/eslint-plugin-js` | Oxlint style categories |
| `@stylistic/eslint-plugin-ts` | Oxlint style categories |
| `eslint-plugin-import` | Oxlint `import` plugin + Biome `organizeImports` |
| `eslint-plugin-unicorn` | Oxlint `unicorn` plugin |
| `eslint-plugin-sonarjs` | Oxlint `oxc`/deepscan plugin (partial) |
| `eslint-plugin-promise` | Oxlint `promise` plugin |
| `eslint-plugin-react` | Oxlint `react` plugin |
| `eslint-plugin-react-hooks` | Oxlint `react` plugin (includes hooks) |
| `eslint-plugin-jsx-a11y` | Oxlint `jsx-a11y` plugin |
| `@next/eslint-plugin-next` | Oxlint `nextjs` plugin |
| `eslint-plugin-n` | Oxlint `node` plugin |
| `eslint-plugin-node` | Oxlint `node` plugin |
| `eslint-plugin-vitest` | Oxlint `vitest` plugin |
| `eslint-plugin-jest` | Oxlint `jest` plugin |
| `eslint-plugin-jsdoc` | Oxlint `jsdoc` plugin |
| `eslint-config-prettier` | Eliminated (Biome doesn't conflict with Oxlint) |

#### ELIMINATE (no replacement needed)

| Old Package | Why |
|-------------|-----|
| `prettier` | Replaced by Biome |
| `eslint-plugin-html` | Biome formats HTML |
| `@trivago/prettier-plugin-sort-imports` | Biome `organizeImports` |
| `@ianvs/prettier-plugin-sort-imports` | Biome `organizeImports` |
| `prettier-plugin-organize-imports` | Biome `organizeImports` |
| `prettier-plugin-packagejson` | Biome handles JSON |

#### RESIDUAL (keep ESLint only for these gap plugins)

| Old Package | Reason |
|-------------|--------|
| `eslint-plugin-vue` | Oxlint can't lint Vue `<template>` blocks |
| `eslint-plugin-astro` | Oxlint can't parse `.astro` files |
| `eslint-plugin-better-tailwindcss` | Oxlint has no Tailwind rules |
| `eslint-plugin-playwright` | Not yet ported to Oxlint |
| `eslint-plugin-obsidianmd` | Too niche for Oxlint |
| `eslint-plugin-compat` | No browser compat rules in Oxlint |

#### REPLACE (swap for new equivalent)

| Old Package | New Package | Why |
|-------------|-------------|-----|
| `prettier-plugin-tailwindcss` | `eslint-plugin-better-tailwindcss` | Prettier removed; class sorting moves to ESLint |
| `eslint-plugin-tailwindcss` | `eslint-plugin-better-tailwindcss` | Old plugin incompatible with Tailwind v4 |

#### Generate Migration Plan

Present to user:
```
=== Plugin Migration Plan ===

REMOVE ([count] packages): [list]
ELIMINATE ([count] packages): [list]
RESIDUAL ([count] packages): [list]
REPLACE ([count] packages): [old → new list]

New packages to ADD:
  - oxlint
  - @biomejs/biome
  [if residual needed:]
  - eslint-plugin-oxlint
  [gap plugin additions]

Oxlint plugins to enable: [list based on detected frameworks]
```

---

### Phase 3: Execution

Execute migration steps. Use the project's detected package manager for all install/remove commands.

#### 3.1 Install New Core Dependencies

```bash
pnpm add -D oxlint @biomejs/biome
```

If residual ESLint is needed:
```bash
pnpm add -D eslint eslint-plugin-oxlint
```

Install any gap plugins or replacement plugins identified in Phase 2.

#### 3.2 Create oxlint.json

Use the template from `templates/oxlint.json`. Customise the `plugins` array based on detected frameworks:

**Always include**: `"import"`, `"promise"` (core `eslint`, `typescript`, `unicorn`, `oxc` are enabled by default)

**Add based on framework detection**:
- React: add `"react"`, `"jsx-a11y"`
- React + perf: add `"react"`, `"jsx-a11y"`, `"react-perf"`
- Next.js: add `"react"`, `"jsx-a11y"`, `"nextjs"`
- Node.js backend: add `"node"`
- Vitest: add `"vitest"`
- Jest: add `"jest"`

Preserve any custom rule overrides from the old ESLint config where Oxlint has equivalents (see Phase 5).

#### 3.3 Create biome.json

Use the template from `templates/biome.json`. **Preserve the user's existing Prettier settings** by mapping:

| Prettier Setting | Biome Equivalent | Default |
|-----------------|------------------|---------|
| `printWidth` | `formatter.lineWidth` | `100` |
| `tabWidth` | `formatter.indentWidth` | `2` |
| `useTabs: true` | `formatter.indentStyle: "tab"` | `"space"` |
| `semi: true` | `javascript.formatter.semicolons: "always"` | `"always"` |
| `semi: false` | `javascript.formatter.semicolons: "asNeeded"` | |
| `singleQuote: true` | `javascript.formatter.quoteStyle: "single"` | `"single"` |
| `singleQuote: false` | `javascript.formatter.quoteStyle: "double"` | |
| `trailingComma: "all"` | `javascript.formatter.trailingCommas: "all"` | `"all"` |
| `trailingComma: "es5"` | `javascript.formatter.trailingCommas: "es5"` | |
| `trailingComma: "none"` | `javascript.formatter.trailingCommas: "none"` | |
| `arrowParens: "always"` | `javascript.formatter.arrowParentheses: "always"` | `"asNeeded"` |
| `arrowParens: "avoid"` | `javascript.formatter.arrowParentheses: "asNeeded"` | |
| `endOfLine: "lf"` | `formatter.lineEnding: "lf"` | `"lf"` |

**Critical**: `linter.enabled` must be `false`. Biome is formatter-only in our stack.

Also merge `.prettierignore` patterns into `biome.json` `files.includes` array using `!` negation (e.g. `"!**/dist/**"`).

**CRITICAL**: Always add the `vcs` block to enable `.gitignore` integration. Without this, CI pipelines (Docker-based) will scan `node_modules/` and fail with hundreds of formatting errors:
```json
{
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  }
}
```

#### 3.4 Create/Update eslint.config.mjs (if residual needed)

Only if gap plugins were detected. Use the template from `templates/eslint.config.mjs`.

**Critical**: `eslint-plugin-oxlint` must be **last** in the config to disable all rules Oxlint covers:

```javascript
import oxlint from 'eslint-plugin-oxlint';

// ... gap plugin imports and configs ...

export default [
  { ignores: ['dist/', 'build/', 'node_modules/', '.next/', 'coverage/'] },

  // ... gap plugin configurations ...

  // MUST be last — disables rules oxlint covers
  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

Uncomment only the sections relevant to the detected gap plugins.

If no residual ESLint is needed, delete any existing `eslint.config.*` files.

#### 3.5 Update package.json Scripts

**Standard (no residual ESLint):**
```json
{
  "scripts": {
    "lint": "oxlint --max-warnings=0",
    "lint:fix": "oxlint --fix --max-warnings=0",
    "format": "biome format --write .",
    "format:check": "biome format .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

**With residual ESLint:**
```json
{
  "scripts": {
    "lint": "oxlint --max-warnings=0 && eslint . --max-warnings=0",
    "lint:fix": "oxlint --fix --max-warnings=0 && eslint . --fix --max-warnings=0",
    "format": "biome format --write .",
    "format:check": "biome format .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

Remove any old `eslint` or `prettier` references from other scripts (e.g. `"lint:eslint"`, `"format:prettier"`).

#### 3.6 Update lint-staged Configuration

If lint-staged exists, update to new commands:

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.vue": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.css": ["biome format --write"],
    "*.{json,md}": ["biome format --write"]
  }
}
```

With residual ESLint, add `"eslint --fix --max-warnings=0"` to the relevant file patterns.

#### 3.7 Update CI/CD Files

For each detected CI/CD file, replace old ESLint/Prettier commands:

| Old Command | New Command |
|-------------|-------------|
| `eslint .` / `eslint . --max-warnings=0` | `oxlint --max-warnings=0` |
| `prettier --check .` / `prettier --check "src/**/*.ts"` | `biome format .` |
| `prettier --write .` | `biome format --write .` |

If residual ESLint is needed, add `eslint . --max-warnings=0` after `oxlint` in lint steps.

**Flag for manual review**: CI/CD changes should be reviewed by user before committing.

#### 3.8 Update .vscode/settings.json

If `.vscode/settings.json` exists, update:

```jsonc
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "editor.codeActionsOnSave": {
    "source.fixAll.oxc": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

Remove old ESLint/Prettier-related settings:
- `"eslint.validate"`, `"eslint.format.enable"`, `"eslint.codeActionsOnSave"`
- `"prettier.enable"`, `"editor.defaultFormatter": "esbenp.prettier-vscode"`

Recommend extensions: `biomejs.biome` + `oxc.oxc-vscode` (replaces `dbaeumer.vscode-eslint` + `esbenp.prettier-vscode`).

#### 3.9 Remove Old Dependencies

Build a single removal command with all packages classified as REMOVE or ELIMINATE in Phase 2:

```bash
pnpm remove eslint prettier \
  @typescript-eslint/eslint-plugin @typescript-eslint/parser typescript-eslint \
  @stylistic/eslint-plugin eslint-plugin-import eslint-plugin-unicorn \
  eslint-plugin-sonarjs eslint-plugin-promise eslint-config-prettier \
  eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y \
  @next/eslint-plugin-next eslint-plugin-n eslint-plugin-vitest \
  eslint-plugin-jest eslint-plugin-compat eslint-plugin-html \
  prettier-plugin-tailwindcss \
  [... any other detected old packages]
```

Only include packages that are actually installed. Do NOT remove packages classified as RESIDUAL.

If residual ESLint is not needed, also remove `eslint` itself.

#### 3.10 Remove Old Configuration Files

Delete:
- `.eslintrc` / `.eslintrc.js` / `.eslintrc.cjs` / `.eslintrc.json` / `.eslintrc.yaml` / `.eslintrc.yml`
- `.eslintignore`
- `.prettierrc` / `.prettierrc.json` / `.prettierrc.js` / `.prettierrc.cjs` / `.prettierrc.yaml` / `.prettierrc.yml`
- `prettier.config.js` / `prettier.config.cjs`
- `.prettierignore`

If no residual ESLint, also delete `eslint.config.js` / `eslint.config.mjs` / `eslint.config.cjs`.

Remove `"prettier"` and `"eslintConfig"` keys from `package.json` if present.

---

### Phase 4: Prettier Config Preservation Verification

After creating `biome.json`, verify the Prettier settings were correctly mapped:

```
=== Prettier → Biome Setting Verification ===

Old Prettier:                    New Biome:
  printWidth: 100         →       lineWidth: 100
  tabWidth: 2             →       indentWidth: 2
  useTabs: false          →       indentStyle: "space"
  semi: true              →       semicolons: "always"
  singleQuote: true       →       quoteStyle: "single"
  trailingComma: "all"    →       trailingCommas: "all"
  arrowParens: "avoid"    →       arrowParentheses: "asNeeded"
  endOfLine: "lf"         →       lineEnding: "lf"
```

Run `biome format --write .` on the codebase and review the diff to confirm formatting output matches expectations. If there are unexpected formatting changes, adjust `biome.json` settings accordingly.

---

### Phase 5: Custom Rule Mapping

#### 5.1 Extract Custom Rules

Read the old ESLint config and extract all entries from the `rules` object. Separate into:
- **Plugin rules** (prefixed with plugin name, e.g. `@typescript-eslint/no-explicit-any`)
- **Core rules** (no prefix, e.g. `no-console`)

#### 5.2 Map to Oxlint Equivalents

Most ESLint rules have identical names in Oxlint. Check each custom rule:

1. **Same name exists in Oxlint** → Add to `oxlint.json` `rules` section with same severity
2. **Different name in Oxlint** → Map using common equivalences:
   - `@typescript-eslint/X` → `typescript/X` in Oxlint
   - `import/X` → `import/X` in Oxlint
   - `react/X` → `react/X` in Oxlint
   - `react-hooks/X` → `react/X` in Oxlint (hooks rules merged into react plugin)
3. **No Oxlint equivalent** → Three options:
   - Accept the gap (if rule is non-critical)
   - Move to residual ESLint (if rule is important)
   - Flag for user review

#### 5.3 Rule Severity Mapping

| ESLint | Oxlint |
|--------|--------|
| `"error"` or `2` | `"error"` |
| `"warn"` or `1` | `"warn"` |
| `"off"` or `0` | `"off"` or omit |

For rules with options (arrays), map the options directly:
```
ESLint:  "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
Oxlint:  "no-unused-vars": ["error", { "argsIgnorePattern": "^_", "varsIgnorePattern": "^_" }]
```

#### 5.4 Present Custom Rule Report

```
=== Custom Rule Migration ===

Mapped to Oxlint ([count]):
  [rule] → oxlint [equivalent]
  ...

No Oxlint equivalent ([count]):
  [rule] — [recommendation: accept gap / move to residual / user review]
  ...

Added to oxlint.json rules: [count]
```

---

### Phase 6: Verification

#### 6.1 Run Full Lint Stack

Execute each tool and capture results:

```bash
# 1. Oxlint
oxlint --max-warnings=0

# 2. Residual ESLint (if applicable)
eslint . --max-warnings=0

# 3. Biome format check
biome format .

# 4. TypeScript type check
tsc --noEmit
```

If any tool fails, attempt auto-fix first:
```bash
oxlint --fix --max-warnings=0
eslint . --fix --max-warnings=0    # if residual
biome format --write .
```

Re-run checks after fixes.

#### 6.2 Test Pre-Commit Hooks

If husky + lint-staged is configured:
```bash
npx lint-staged --dry-run
```

Verify it runs the new oxlint/biome commands, not old eslint/prettier.

#### 6.3 Show Dependency Comparison

```
=== Before/After ===

Old ESLint/Prettier packages: [count]
New Oxlint/Biome packages: [count]
Net reduction: [difference] packages (-[percentage]%)

New lint stack:
  - oxlint
  - @biomejs/biome
  [if residual:]
  - eslint
  - eslint-plugin-oxlint
  [gap plugins]
```

#### 6.4 Present Final Summary

```
=== Migration Complete ===

Config files created: oxlint.json, biome.json [, eslint.config.mjs]
Config files removed: [list of deleted old configs]
Dependencies removed: [count]
Dependencies added: [count]
Net reduction: [count] packages

Verification:
  Oxlint:          PASS/FAIL
  Residual ESLint: PASS/FAIL/N/A
  Biome Format:    PASS/FAIL
  TypeScript:      PASS/FAIL

[If all pass]: Ready to commit.
[If failures]:  Review issues above before committing.
```

---

## Troubleshooting

### Oxlint reports too many warnings

Adjust category severity in `oxlint.json`. Start permissive and tighten:
```jsonc
{
  "categories": {
    "correctness": "error",
    "suspicious": "warn",
    "pedantic": "off",       // Start off, enable gradually
    "style": "warn",
    "restriction": "off",
    "nursery": "off"
  }
}
```

### Biome formatting differs from old Prettier output

Check that all Prettier settings were mapped correctly (see Phase 4). Common mismatches:
- `trailingComma: "es5"` in Prettier → `trailingCommas: "es5"` in Biome (Biome 2.x supports "all", "es5", and "none")
- `arrowParens: "avoid"` in Prettier → `arrowParentheses: "asNeeded"` in Biome

### Residual ESLint rules duplicating Oxlint

Ensure `...oxlint.buildFromOxlintConfigFile('./oxlint.json')` is **last** in `eslint.config.mjs`. This reads the oxlint.json and disables all overlapping ESLint rules.

### Import sorting behaves differently

Biome's import sorting (`assist.actions.source.organizeImports`) groups imports as: built-in → external → internal → relative. For more complex sorting (e.g. custom group ordering), this is a trade-off of the migration. Accept Biome's grouping or keep `eslint-plugin-import` order rules in residual ESLint if sorting is critical.

### CI/CD fails with "command not found"

Ensure CI installs dependencies before running lint. Use `npx` if tools aren't on PATH:
```bash
npx oxlint --max-warnings=0
npx biome format .
```

### VSCode not using Biome formatter

Install the Biome extension (`biomejs.biome`) and reload VSCode. Verify `.vscode/settings.json` has `"editor.defaultFormatter": "biomejs.biome"`.

### Biome CI: Hundreds of formatting errors in node_modules

**Symptom**: `biome format .` passes locally but fails in CI (Bitbucket Pipelines, GitHub Actions) with hundreds of errors in `node_modules/.pnpm/` paths.

**Root cause**: Biome's VCS integration is **off by default**. Locally, built-in node_modules exclusion masks the issue. In CI Docker containers, file discovery differs and `files.includes` negation patterns for directories are unreliable ([Biome bug #7279](https://github.com/biomejs/biome/issues/7279)).

**Fix**: Add `vcs` config to `biome.json`:
```json
{
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  }
}
```

Also ensure negation patterns use `/**` suffix for directories: `"!**/dist/**"` not `"!**/dist"`.

### Biome CI: pnpm store scanned by formatter

**Symptom**: VCS integration is enabled and `.gitignore` excludes `node_modules/`, but CI still fails with hundreds of formatting errors in `.pnpm-store/v10/index/` JSON files.

**Root cause**: `pnpm install` creates a `.pnpm-store/` content-addressable store in the build root when the global store cache misses (common on first CI runs or cold caches). This directory is not in a typical `.gitignore`, so VCS integration doesn't exclude it.

**Fix**: Add `.pnpm-store/` to both `.gitignore` and `biome.json`:
```
# .gitignore
.pnpm-store/
```
```json
// biome.json files.includes
"!.pnpm-store/**"
```

### Biome: No `files.excludes` field

Biome v2.3.15 does NOT have a `files.excludes` key. The valid keys under `files` are: `maxSize`, `ignoreUnknown`, `includes`, `experimentalScannerIgnores`. Use `!` negation patterns in `files.includes` for exclusions, combined with VCS integration.

### Monorepo considerations

- Place `oxlint.json` and `biome.json` at workspace root
- Oxlint respects `.gitignore` by default; Biome requires `vcs.enabled: true` + `vcs.useIgnoreFile: true`
- Per-package overrides can be added via Oxlint `overrides` and Biome `overrides` sections
- Update root workspace scripts: `"lint": "oxlint --max-warnings=0"` (Oxlint walks directories)

### eslint-plugin-tailwindcss errors with Tailwind v4

The old `eslint-plugin-tailwindcss` requires Tailwind v3's JavaScript config file (`tailwind.config.js`). Tailwind v4 uses CSS-first configuration. Replace with `eslint-plugin-better-tailwindcss` which supports v4 natively.

### Astro parser errors with projectService

When using residual ESLint with `eslint-plugin-astro`, scope `projectService: true` to `**/*.ts` and `**/*.tsx` files only. Use `project: true` for `.astro` files instead. See `typescript-residual-eslint.md` for the exact config.
