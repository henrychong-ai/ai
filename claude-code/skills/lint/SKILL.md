---
name: lint
description: Linting and formatting setup, running lint commands, fixing errors, and configuring code quality tools — TypeScript/JavaScript (Oxlint + Biome, residual ESLint for gap plugins), Python (Ruff, mypy), Go (golangci-lint), .NET (Roslyn analyzers), Solidity (Solhint + forge fmt).
---

# Lint Skill

Code quality, linting, and formatting setup across all major ecosystems.

**Version Policy:** Always use the latest minor/patch within the target major version. This skill specifies major versions only — install the latest available release within that major.

## Quick Reference Matrix

| Ecosystem | Linter | Formatter | Type Checker | Config Files |
|-----------|--------|-----------|--------------|--------------|
| **TypeScript/JS** | Oxlint (primary) + residual ESLint (gap plugins) | Biome (linter disabled) | TypeScript | `oxlint.json` + `biome.json` |
| **Python** | Ruff | Ruff | mypy | `pyproject.toml` |
| **Go** | golangci-lint v2 | gofumpt (via golangci-lint) | Built-in | `.golangci.yml` |
| **.NET/C#** | Roslyn Analyzers | dotnet format | Built-in | `.editorconfig` |
| **CSS** | Stylelint | Biome | N/A | `.stylelintrc.json` |
| **SCSS/Less** | Stylelint | (none — Biome CSS only) | N/A | `.stylelintrc.json` |
| **Solidity** | Solhint | forge fmt (Foundry) / Prettier (Hardhat) | N/A | `.solhint.json` |

## Modes of Operation

### SETUP Mode
Use when scaffolding new projects or adding linting to existing projects.

**Triggers:** "set up linting", "configure oxlint", "configure biome", "add linting"

### OPERATIONS Mode
Use when running linting commands, fixing errors, or checking code quality.

**Triggers:** "run lint", "fix lint errors", "check formatting", "lint this"

---

## Oxlint Plugin Architecture

### Layer 1 — Oxlint Built-in Plugins (ZERO npm dependencies)

Oxlint includes 668 rules across 14 native plugins. No npm install required.

| Plugin | Rules | Replaces | Trigger | Config |
|--------|-------|----------|---------|--------|
| `eslint` (core) | ~200 | ESLint core rules | Always | Default enabled |
| `typescript` | ~90 | @typescript-eslint | Always | Default enabled |
| `unicorn` | ~100 | eslint-plugin-unicorn | Always | Default enabled |
| `oxc` (deepscan) | ~30 | eslint-plugin-sonarjs (partial) | Always | Default enabled |
| `import` | ~25 | eslint-plugin-import | Always | Add to `plugins` |
| `promise` | ~15 | eslint-plugin-promise | Always | Add to `plugins` |
| `react` + hooks | ~40 | eslint-plugin-react + react-hooks | React detected | Add to `plugins` |
| `react-perf` | ~6 | (new — performance rules) | React detected | Add to `plugins` |
| `nextjs` | ~15 | @next/eslint-plugin-next | Next.js detected | Add to `plugins` |
| `jsx-a11y` | ~30 | eslint-plugin-jsx-a11y | JSX detected | Add to `plugins` |
| `node` | ~20 | eslint-plugin-n | Node.js backend detected | Add to `plugins` |
| `vitest` | ~15 | eslint-plugin-vitest | Vitest detected | Add to `plugins` |
| `jest` | ~25 | eslint-plugin-jest | Jest detected | Add to `plugins` |
| `jsdoc` | ~20 | (optional) | JSDoc usage | Add to `plugins` |

### Layer 2 — Biome Formatter (replaces Prettier)

- Format: JS/TS/JSX/TSX/CSS/JSON/JSONC/GraphQL/HTML/Svelte/Vue/Astro/Markdown/GritQL
- Import sorting via `assist.actions.source.organizeImports` (replaces eslint-plugin-import order rules)
- Linter **disabled** (oxlint handles all linting)
- Single npm dep: `@biomejs/biome`
- **Biome 2.x**: Uses `files.includes` with `!` negation (no `files.excludes` field), and `assist` block (not top-level `organizeImports`)
- **VCS integration required**: Must add `"vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true }` — without this, CI pipelines scan node_modules and fail

#### Biome Format Coverage (vs Prettier)

| Format | Biome | Prettier | Notes |
|--------|-------|----------|-------|
| JS/TS/JSX/TSX | Yes | Yes | Full parity |
| JSON/JSONC | Yes | Yes | Full parity |
| CSS | Yes | Yes | Full parity |
| GraphQL | Yes | Yes | Full parity |
| HTML | Yes | Yes | Full parity |
| Markdown | Yes | Yes | Full parity |
| Svelte/Vue/Astro | Yes | Plugin | Biome native support |
| GritQL | Yes | No | Biome-only |
| **YAML** | **No** | Yes | On Biome 2026 roadmap, not yet shipped |
| **SCSS/Less** | **No** | Yes | Biome CSS only, no preprocessors |
| **TOML** | **No** | Plugin | Rust/Python configs |
| **XML** | **No** | Plugin | Config files, SVGs |
| **PHP/Ruby** | **No** | Plugin | Server-side languages |
| **Handlebars/EJS** | **No** | Yes | Template engines |

**Practical impact:** For most JS/TS projects, only **YAML** is a gap. No good standalone YAML formatter exists — most teams don't auto-format YAML (it's simple enough to hand-write). Do NOT include `yml`/`yaml` in lint-staged biome globs — biome reports "0 files processed" as an error, failing pre-commit hooks.

### Layer 3 — Residual ESLint (only when gap plugins needed)

Uses `eslint-plugin-oxlint` to disable all rules oxlint already covers.

| Plugin | Trigger | Why Not Oxlint |
|--------|---------|----------------|
| `eslint-plugin-vue` | Vue detected | Oxlint: script tags only, no template linting |
| `eslint-plugin-astro` | Astro detected | Oxlint: no .astro file support |
| `eslint-plugin-better-tailwindcss` | Tailwind v4 detected | Oxlint: no Tailwind rules; also replaces `prettier-plugin-tailwindcss` for class sorting |
| `eslint-plugin-react-refresh` | Vite + React detected | Oxlint: no react-refresh/HMR rules |
| `eslint-plugin-playwright` | Playwright detected | Oxlint: not ported yet |
| `eslint-plugin-obsidianmd` | Obsidian detected | Oxlint: too niche |
| `eslint-plugin-compat` | Frontend + browserslist | Oxlint: no browser compat rules |

**IMPORTANT: TypeScript parser requirement.** Residual ESLint cannot parse `.ts`/`.tsx` files without a TypeScript parser. When any gap plugin lints TypeScript files, you MUST also install `typescript-eslint` and configure its parser:
```bash
pnpm add -D typescript-eslint  # Required for TS parsing in residual ESLint
```
```javascript
// In eslint.config.js — add to any block with files: ['**/*.{ts,tsx}']
import tseslint from 'typescript-eslint';
// ...
languageOptions: { parser: tseslint.parser },
```
Note: Vue and Astro configs already include `typescript-eslint` for their parsers. For other gap plugins (react-refresh, playwright, compat, etc.), add it explicitly.

### Layer 4 — tsc (unchanged)

`tsc --noEmit` remains mandatory for type checking. No alternatives.

---

## Automated Setup Protocol (For AI Execution)

When user requests linting setup, execute these steps:

### Step 1: Detect Project Type
```bash
# Check for framework indicators
ls package.json next.config.* vite.config.* astro.config.* manifest.json 2>/dev/null
cat package.json | grep -E "next|react|vue|astro|express|fastify|hono|vitest|jest|playwright|obsidian|tailwindcss"
# Check for Obsidian manifest
cat manifest.json 2>/dev/null | grep -E "minAppVersion"
```

### Step 2: Install Core Dependencies
```bash
# Core (always install) — only 3 packages!
pnpm add -D oxlint @biomejs/biome typescript
```

### Step 3: Install Residual ESLint (only if gap plugins needed)
```bash
# Core residual ESLint (always required when using gap plugins)
pnpm add -D eslint eslint-plugin-oxlint

# TypeScript parser (required when gap plugins lint .ts/.tsx files)
# Vue and Astro already include this, but other gap plugins need it explicitly
pnpm add -D typescript-eslint

# Vite + React HMR (if Vite + React detected)
pnpm add -D eslint-plugin-react-refresh typescript-eslint

# Vue templates (if Vue detected)
pnpm add -D eslint-plugin-vue typescript-eslint

# Astro .astro files (if Astro detected)
pnpm add -D eslint-plugin-astro typescript-eslint

# Tailwind CSS v4 class validation + sorting (if Tailwind detected)
# NOTE: Replaces prettier-plugin-tailwindcss since Prettier is removed
pnpm add -D eslint-plugin-better-tailwindcss

# Playwright E2E (if detected)
pnpm add -D eslint-plugin-playwright

# Obsidian plugin (if detected)
pnpm add -D eslint-plugin-obsidianmd

# Browser compatibility (if frontend + browserslist)
pnpm add -D eslint-plugin-compat

# Stylelint for CSS/SCSS (if CSS files exist AND no Tailwind)
pnpm add -D stylelint stylelint-config-standard
```

### Step 4: Create Config Files
Use templates from `templates/` directory:
- `oxlint.json` — Oxlint config (enable framework plugins via `plugins` array)
- `biome.json` — Biome formatter (linter disabled)
- `tsconfig.json` — Strict TypeScript config (if not exists)
- `eslint.config.mjs` — Residual ESLint (only if gap plugins needed — uncomment relevant sections)

### Step 5: Add Package.json Scripts

**Standard (no residual ESLint needed):**
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

### Step 6: Setup Pre-commit Hooks (Required)

**IMPORTANT:** Pre-commit hooks are required to enforce linting and formatting on every commit.

```bash
# Install husky + lint-staged
pnpm add -D husky lint-staged

# Initialize husky (creates .husky/ and configures git)
pnpm exec husky init

# Create pre-commit hook — copy the template (runs gitleaks secret-scan + lint-staged)
cp ~/.claude/skills/lint/templates/.husky/pre-commit .husky/pre-commit
# Drop the canonical gitleaks config at the repo root (blocks secrets + .env)
cp ~/.claude/skills/lint/templates/.gitleaks.toml .gitleaks.toml

# Verify setup
git config core.hooksPath && test -x .husky/pre-commit && echo "✓ Husky configured"
```

### Step 7: Add lint-staged Config to package.json

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.vue": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.css": ["biome format --write"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.go": ["golangci-lint run --fix"],
    "*.sol": ["solhint --fix", "forge fmt"],
    "*.{json,md}": ["biome format --write"]
  }
}
```

### Framework Detection Matrix

| Indicator | Framework | Oxlint Plugins | Residual ESLint? |
|-----------|-----------|----------------|------------------|
| `next.config.*` or `"next"` in deps | Next.js | react, jsx-a11y, nextjs | No |
| `"react"` in deps | React | react, jsx-a11y | No |
| `vite.config.*` + `"react"` in deps | Vite + React | react, jsx-a11y | Yes — `eslint-plugin-react-refresh` |
| `vue.config.*` or `"vue"` in deps | Vue | (default) | Yes — `eslint-plugin-vue` |
| `astro.config.*` | Astro | (default) | Yes — `eslint-plugin-astro` |
| `"express"/"fastify"/"hono"/"koa"` | Node.js | node | No |
| `"vitest"` in devDeps | Testing | vitest | No |
| `"jest"` in devDeps | Testing | jest | No |
| `"@playwright/test"` in devDeps | E2E Testing | (default) | Yes — `eslint-plugin-playwright` |
| `manifest.json` with `minAppVersion` | Obsidian Plugin | (default) | Yes — `eslint-plugin-obsidianmd` |
| `"tailwindcss"` in deps | Tailwind CSS | (default) | Yes — `eslint-plugin-better-tailwindcss` |
| `browserslist` in package.json | Frontend | (default) | Yes — `eslint-plugin-compat` |
| `*.css/*.scss` files (no Tailwind) | CSS/SCSS | (default) | No — Stylelint separate |
| `hardhat.config.*` or `foundry.toml` | Solidity | (default) | No — Solhint separate |

---

## TypeScript/JavaScript (Primary)

### Recommended Stack
- **Oxlint** — Primary linter with 668 built-in rules, native plugins (React, Next.js, Vitest, Jest, Node.js, jsx-a11y, import, promise, unicorn, typescript)
- **Biome** — Formatter only (linter disabled), Prettier-compatible settings, import sorting
- **Residual ESLint** — Only for gap plugins (Vue templates, Astro, Tailwind, Playwright, Obsidian, Compat) via `eslint-plugin-oxlint`
- **tsc** — Type checking (unchanged)

### Install Commands

**Core (all TypeScript projects) — 3 packages:**
```bash
pnpm add -D oxlint @biomejs/biome typescript
```

**Add for Vue (residual ESLint for templates):**
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-vue typescript-eslint
```

**Add for Tailwind CSS v4 (class validation + sorting):**
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-better-tailwindcss
```

**Add for Astro:**
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-astro typescript-eslint
```

**Add for Playwright E2E:**
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-playwright
```

### Dependency Reduction

| Scenario | Before (ESLint+Prettier) | After (Oxlint+Biome) |
|----------|--------------------------|----------------------|
| Bare minimum (TS project) | 13 packages | **3 packages** |
| React project | 16 packages | **3 packages** |
| Next.js project | 17 packages | **3 packages** |
| Vue project | 14 packages | **5 packages** |
| Next.js + Tailwind + Vitest | 19 packages | **7 packages** |
| Kitchen sink (all plugins) | 30 packages | **12 packages** |

### Run Commands
```bash
pnpm lint              # Oxlint check (+ residual ESLint if configured)
pnpm lint:fix          # Oxlint auto-fix (+ residual ESLint if configured)
pnpm format            # Biome format
pnpm format:check      # Biome format check (CI)
pnpm typecheck         # TypeScript check
pnpm check             # All checks combined
```

**Reference:** `references/typescript-oxlint-biome.md` for full configuration.

### Framework Extensions

| Framework | Additional Setup |
|-----------|------------------|
| **React** | Add `"react", "jsx-a11y"` to oxlint.json plugins — no extra npm deps |
| **Vite + React** | Add `"react", "jsx-a11y"` to oxlint.json plugins + Residual ESLint: `pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-react-refresh typescript-eslint` |
| **Next.js** | Add `"react", "jsx-a11y", "nextjs"` to oxlint.json plugins — no extra npm deps |
| **Node.js** | Add `"node"` to oxlint.json plugins — no extra npm deps |
| **Vitest** | Add `"vitest"` to oxlint.json plugins — no extra npm deps |
| **Jest** | Add `"jest"` to oxlint.json plugins — no extra npm deps |
| **Vue** | Residual ESLint: `pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-vue typescript-eslint` |
| **Astro** | Residual ESLint: `pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-astro typescript-eslint` |
| **Tailwind CSS** | Residual ESLint: `pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-better-tailwindcss` |
| **Obsidian** | Residual ESLint: `pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-obsidianmd` |

**Reference:** `references/typescript-residual-eslint.md` for gap plugin integration.

---

## Python

**Recommended Stack:** Ruff + mypy

### Quick Setup
```bash
uv add --dev ruff mypy
```

### Configuration (pyproject.toml)
```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM", "TCH", "RUF"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.12"
strict = true
```

### Run Commands
```bash
ruff check .           # Lint
ruff check . --fix     # Lint + auto-fix
ruff format .          # Format
mypy .                 # Type check
```

**Reference:** `references/python-ruff-mypy.md` for full configuration.

---

## Go

**Recommended Stack:** golangci-lint v2 (includes gofumpt — no standalone formatter needed)

### Quick Setup
```bash
brew install golangci-lint
```

### Configuration (.golangci.yml)

Based on [google/osv-scanner](https://github.com/google/osv-scanner), [google/go-github](https://github.com/google/go-github), and industry standards. See `references/go-golangci-lint.md` for full config.

```yaml
version: "2"

linters:
  default: all  # Same approach as google/osv-scanner
  disable:
    - depguard          # Enable per-project with custom deny rules
    - exhaustruct       # Too strict
    - ireturn           # Too opinionated
    - varnamelen        # Too strict for idiomatic Go
    - wrapcheck         # Handled manually
    - nlreturn          # Style opinion
    - wsl               # Style opinion
    - godox             # Noisy during development
    - err113            # Conflicts with fmt.Errorf
    - testpackage       # Blocks white-box testing
    - paralleltest      # Not always appropriate
    - thelper           # Too strict
    - cyclop            # Redundant with gocyclo/gocognit
    - forcetypeassert   # Checked by errcheck
    - tagliatelle       # Too opinionated
    - nonamedreturns    # Named returns useful for docs
    - mnd               # Too noisy
    - funlen            # Use gocognit instead
    - lll               # gofumpt handles formatting

formatters:
  enable:
    - gofumpt
    - goimports

linters-settings:
  gofumpt:
    extra-rules: true
```

### Run Commands
```bash
golangci-lint run           # Lint + check formatting
golangci-lint run --fix     # Lint + auto-fix + format
```

**Reference:** `references/go-golangci-lint.md` for full configuration.

---

## .NET / C#

**Recommended Stack:** Roslyn Analyzers + dotnet format

### Quick Setup
- `Directory.Build.props`: `AnalysisLevel` `latest-recommended` (default; `latest-all` is an opt-in strict profile), `EnforceCodeStyleInBuild` and `TreatWarningsAsErrors` `true`
- `Directory.Packages.props` (Central Package Management): StyleCop.Analyzers, Roslynator.Analyzers and SonarAnalyzer.CSharp as `GlobalPackageReference`; no `Version=` on `PackageReference` (NU1008)
- CA2007 (ConfigureAwait) off at the solution root; libraries opt in via a nested `.editorconfig`

### Run Commands
```bash
dotnet format                     # Format
dotnet format --verify-no-changes # Check (CI)
dotnet build -warnaserror         # Build; analyzers run as part of it
```

**Reference:** `references/dotnet-roslyn.md` for full configuration; full .NET conventions in the `/dotnet` skill (`references/coding-standards/tooling.md`) where installed.

---

## Solidity (Smart Contracts)

**Note:** Solidity uses Solhint for linting and **forge fmt** (Foundry) for formatting — completely separate from the Oxlint/Biome stack.

### Quick Setup (Foundry projects)
```bash
pnpm add -D solhint
# forge fmt is included with Foundry (forge)
```

### Quick Setup (Hardhat projects — Prettier fallback)
```bash
pnpm add -D solhint prettier prettier-plugin-solidity
```

### Run Commands
```bash
# Linting
npx solhint 'contracts/**/*.sol'

# Formatting (Foundry — preferred)
forge fmt

# Formatting (Hardhat — Prettier fallback)
npx prettier --write 'contracts/**/*.sol'
```

---

## CSS/SCSS (Stylelint)

**Note:** Use Stylelint for CSS/SCSS projects WITHOUT Tailwind. For Tailwind projects, use `eslint-plugin-better-tailwindcss` (residual ESLint) for class validation and sorting. Formatting for CSS is handled by Biome. SCSS/Less formatting is NOT supported by Biome — if needed, keep Prettier for SCSS only.

### Quick Setup
```bash
pnpm add -D stylelint stylelint-config-standard
# For SCSS:
pnpm add -D stylelint-config-standard-scss
```

### Configuration (.stylelintrc.json)
```json
{
  "extends": ["stylelint-config-standard"],
  "rules": {
    "declaration-block-no-redundant-longhand-properties": true,
    "color-hex-length": "short",
    "selector-class-pattern": null
  }
}
```

### Run Commands
```bash
npx stylelint "**/*.css"              # Lint
npx stylelint "**/*.css" --fix        # Lint + auto-fix
```

---

## Tailwind CSS (v4)

Since Prettier is removed, `prettier-plugin-tailwindcss` cannot be used for class sorting. Use `eslint-plugin-better-tailwindcss` as a residual ESLint plugin instead.

**WARNING:** Do NOT use `eslint-plugin-tailwindcss` (the old v3 plugin) with Tailwind v4. It requires Tailwind's legacy JS config and is incompatible with v4's CSS-first configuration.

### Quick Setup
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-better-tailwindcss
```

### Available Configs

| Config | Includes | Use When |
|--------|----------|----------|
| `recommended` | Stylistic + correctness rules | Default (most projects) |
| `stylistic` | Class sorting, multiline only | Want sorting without validation |
| `correctness` | Invalid classes, duplicates only | Want validation without sorting |

### Key Rules

| Rule | Purpose |
|------|---------|
| `sort-classes` | Automatic class sorting (replaces `prettier-plugin-tailwindcss`) |
| `no-duplicate-classes` | Detect duplicate classes |
| `no-conflicting-classes` | Detect contradicting classes |
| `no-custom-classname` | Warn on non-Tailwind classes |
| `multiline` | Multi-line class formatting |

### Detection
- `tailwindcss` ^4.x in dependencies
- CSS files with `@import "tailwindcss"` or `@theme` directives
- Absence of `tailwind.config.js` (v4 doesn't use it)

**Reference:** `references/typescript-residual-eslint.md` (Tailwind section).

---

## Pre-commit Hooks (Required)

Pre-commit hooks are **essential** for enforcing code quality. They run automatically on every `git commit`.

**Secret scanning:** the template hook (`templates/.husky/pre-commit`) runs **gitleaks** before lint-staged — blocking any commit that contains a secret or a `.env` file (`.env.example`/`.sample`/`.template` are allowed). It uses the canonical `templates/.gitleaks.toml`, which must be copied to the repo root. Run the same scan in CI (a gitleaks secret-scan step), so `--no-verify` won't get it merged.

### What Gets Enforced

| File Type | Linting | Formatting |
|-----------|---------|------------|
| TypeScript/JS | `oxlint --fix` | `biome format --write` |
| Vue | `oxlint --fix` | `biome format --write` |
| CSS | - | `biome format --write` |
| Python | `ruff check --fix` | `ruff format` |
| Go | `golangci-lint --fix` | (included) |
| Solidity | `solhint --fix` | `forge fmt` |
| JSON/MD | - | `biome format --write` |

### Setup (Husky + lint-staged)
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
# Copy the template hook (gitleaks secret-scan → lint-staged) + canonical config
cp ~/.claude/skills/lint/templates/.husky/pre-commit .husky/pre-commit
cp ~/.claude/skills/lint/templates/.gitleaks.toml .gitleaks.toml
brew install gitleaks   # the hook calls gitleaks; CI enforces it too
```

### Verify Setup
```bash
# Check git hooks path is configured
git config core.hooksPath  # Should output: .husky

# Check pre-commit hook is executable
test -x .husky/pre-commit && echo "✓ Hook executable"

# Test lint-staged (dry run)
npx lint-staged --dry-run
```

### lint-staged Config (package.json)
```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.vue": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.css": ["biome format --write"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.go": ["golangci-lint run --fix"],
    "*.sol": ["solhint --fix", "forge fmt"],
    "*.{json,md}": ["biome format --write"]
  }
}
```

### Bypassing (Emergency Only)
```bash
git commit --no-verify -m "emergency fix"  # Skip pre-commit hook
```

**Warning:** Only bypass in emergencies. Skipping hooks defeats the purpose of enforced linting.

---

## CI/CD Integration

Use templates from `templates/` directory:
- **GitHub Actions**: `templates/.github/workflows/lint.yml`
- **Bitbucket Pipelines**: `templates/bitbucket-pipelines.yml`

Both templates include:
- TypeScript/JavaScript linting (Oxlint + Biome + TypeScript)
- **Test execution with coverage** (`pnpm test:coverage`)
- Commented sections for residual ESLint, Python (Ruff + mypy) and Go (golangci-lint)
- Caching for faster builds
- Concurrency controls to cancel outdated runs

**Note:** Tests run after lint passes. Coverage thresholds are enforced in `vitest.config.ts` (see `/typescript` skill for test configuration templates).

---

## Reference Files

| File | Content |
|------|---------|
| `references/typescript-oxlint-biome.md` | Full Oxlint + Biome configuration, plugin coverage, migration guide |
| `references/typescript-residual-eslint.md` | Gap plugins: Vue, Astro, Tailwind, Playwright, Obsidian, Compat |
| `references/migration-eslint-prettier-to-oxlint-biome.md` | Migration protocol: analyse existing ESLint+Prettier repo and migrate to Oxlint+Biome |
| `references/python-ruff-mypy.md` | Ruff + mypy strict configuration |
| `references/go-golangci-lint.md` | golangci-lint v2 setup |
| `references/dotnet-roslyn.md` | Roslyn analyzers + .editorconfig |

## Templates

| File | Content |
|------|---------|
| `templates/AGENTS.md.template` | Project instructions snippet: copy as `AGENTS.md` plus a one-line `@AGENTS.md` `CLAUDE.md` shim (delete unused sections!) |
| `templates/oxlint.json` | Oxlint config with plugin sections to enable per project type |
| `templates/biome.json` | Biome formatter config (Prettier-compatible, linter disabled) |
| `templates/eslint.config.mjs` | Residual ESLint (gap plugins only — uncomment relevant sections) |
| `templates/tsconfig.json` | Strict TypeScript config |
| `templates/.vscode/settings.json` | VSCode format-on-save (Biome + Oxlint) |
| `templates/.github/workflows/lint.yml` | GitHub Actions CI workflow |
| `templates/bitbucket-pipelines.yml` | Bitbucket Pipelines CI workflow |
| `templates/.husky/pre-commit` | Husky pre-commit hook (gitleaks secret-scan + lint-staged) |
| `templates/.gitleaks.toml` | Canonical gitleaks config — copy to repo root; blocks secrets + `.env` files |
| `templates/lint-staged.config.js` | Lint-staged JS config (Oxlint + Biome) |
| `templates/pyproject.toml` | Python Ruff + mypy |
| `templates/.golangci.yml` | Go strict config |
| `templates/.editorconfig` | .NET style config |
| `templates/.solhint.json` | Solidity linting |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Oxlint not finding config | Ensure `oxlint.json` is in project root; use `oxlint -c oxlint.json` if needed |
| Biome format conflicts with oxlint | Biome's linter must be `"enabled": false` — only use Biome for formatting |
| Import sorting conflicts | Biome handles sorting (`assist.actions.source.organizeImports`); oxlint handles correctness (`import/no-duplicates`) |
| Residual ESLint rules duplicating oxlint | Ensure `...oxlint.buildFromOxlintConfigFile('./oxlint.json')` is **last** in eslint.config.mjs |
| Type errors in oxlint | Ensure `tsconfig.json` includes all linted files |
| `eslint-plugin-tailwindcss` errors with Tailwind v4 | Replace with `eslint-plugin-better-tailwindcss` (the old plugin requires Tailwind v3 JS config) |
| Astro parser errors with `projectService` | Scope `projectService: true` to `**/*.ts, **/*.tsx` only; use `project: true` for .astro files |
| Residual ESLint: "Unexpected token" on .ts/.tsx | ESLint can't parse TypeScript natively — add `typescript-eslint` and configure `parser: tseslint.parser` |
| Biome: "Tailwind-specific syntax is disabled" | Add `"css": { "parser": { "tailwindDirectives": true } }` to biome.json |
| Biome CI: hundreds of formatting errors in node_modules | Add `"vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true }` to biome.json — VCS is OFF by default, so CI Docker containers don't respect .gitignore |
| Biome CI: formatting errors in .pnpm-store after VCS fix | `pnpm install` creates `.pnpm-store/` in build root on cache miss — add `.pnpm-store/` to `.gitignore` AND `"!.pnpm-store/**"` to biome.json negation patterns |
| Biome: `excludes` is not a valid key | Biome v2.3.15 has no `files.excludes` field. Use negation patterns in `files.includes` (e.g. `"!**/dist/**"`) + VCS integration as primary defence |
| Biome: negation patterns not excluding directories | Use `/**` suffix (e.g. `!**/dist/**` not `!**/dist`) — bare directory negations are buggy ([#7279](https://github.com/biomejs/biome/issues/7279)) |
| Slow linting | Oxlint is 50-100x faster than ESLint — if still slow, check `ignorePatterns` in oxlint.json |

### Performance Tips

1. **Oxlint is fast**: ~50-100x faster than ESLint. No caching needed.
2. **Biome is fast**: ~25x faster than Prettier. No caching needed.
3. **Lint staged only**: Use `lint-staged` for pre-commit (only changed files)
4. **Incremental TypeScript**: `tsc --incremental` for faster type checking
5. **Parallel execution**: `pnpm lint && pnpm format:check` can be parallelised with `concurrently` if desired
