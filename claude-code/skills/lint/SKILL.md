---
name: lint
description: This skill should be used for setting up linting and formatting in projects, running lint commands, fixing lint errors, and configuring code quality tools. Covers TypeScript/JavaScript (ESLint, Prettier), Python (Ruff, mypy), Go (golangci-lint), .NET (Roslyn analyzers), Solidity (Solhint), Astro, and Obsidian plugins. Triggers on set up linting, configure eslint, run lint, fix lint errors, ruff, golangci-lint, dotnet format, code quality.
---

# Lint Skill

Code quality, linting, and formatting setup across all major ecosystems.

## Quick Reference Matrix

| Ecosystem | Linter | Formatter | Type Checker | Config File |
|-----------|--------|-----------|--------------|-------------|
| **TypeScript/JS** | ESLint + Plugins | Prettier | TypeScript | `eslint.config.mjs` |
| **Python** | Ruff | Ruff | mypy | `pyproject.toml` |
| **Go** | golangci-lint v2 | gofmt | Built-in | `.golangci.yml` |
| **.NET/C#** | Roslyn Analyzers | dotnet format | Built-in | `.editorconfig` |
| **CSS/SCSS** | Stylelint | Prettier | N/A | `.stylelintrc.json` |
| **Solidity** | Solhint | Prettier | N/A | `.solhint.json` |

## Modes of Operation

### SETUP Mode
Use when scaffolding new projects or adding linting to existing projects.

**Triggers:** "set up linting", "configure eslint", "add linting"

### OPERATIONS Mode
Use when running linting commands, fixing errors, or checking code quality.

**Triggers:** "run lint", "fix lint errors", "check formatting", "lint this"

---

## ESLint Plugin Architecture

### Core Plugins (Always Enabled)

These plugins are universally useful for all TypeScript/JavaScript projects:

| Plugin | Purpose | Key Rules |
|--------|---------|-----------|
| **@typescript-eslint** | TypeScript type checking | no-unsafe-*, no-explicit-any, strict-boolean-expressions |
| **@stylistic** | Code style | spacing, braces, semicolons |
| **eslint-plugin-import** | Import validation | order, no-duplicates, no-cycle |
| **eslint-plugin-unicorn** | Modern JS | prefer-modern-apis, no-array-reduce |
| **eslint-plugin-sonarjs** | Bug detection | no-duplicate-string, cognitive-complexity |
| **eslint-plugin-promise** | Async patterns | no-floating-promises, prefer-await-to-then |
| **eslint-config-prettier** | Disable conflicting rules | Must be last |

### Conditional Plugins (Enable Based on Project Type)

| Plugin | Trigger | Detection |
|--------|---------|-----------|
| **eslint-plugin-compat** | Frontend with browser targets | `browserslist` in package.json, or React/Vue/Next detected |
| **eslint-plugin-html** | HTML files with inline scripts | `*.html` files in project |
| **eslint-plugin-react** | React | `react` in dependencies |
| **eslint-plugin-react-hooks** | React | `react` in dependencies |
| **eslint-plugin-jsx-a11y** | React/JSX | `react` in dependencies |
| **@next/eslint-plugin-next** | Next.js | `next` in dependencies |
| **eslint-plugin-vue** | Vue | `vue` in dependencies |
| **eslint-plugin-n** | Node.js backend | `express`, `fastify`, `hono`, `koa` in deps |
| **eslint-plugin-vitest** | Vitest testing | `vitest` in devDependencies |
| **eslint-plugin-jest** | Jest testing | `jest` in devDependencies |
| **eslint-plugin-playwright** | Playwright E2E | `@playwright/test` in devDependencies |
| **eslint-plugin-obsidianmd** | Obsidian plugins | `manifest.json` with `minAppVersion`, or `obsidian` in deps |
| **eslint-plugin-tailwindcss** | Tailwind CSS | `tailwindcss` in dependencies |
| **Stylelint** | CSS/SCSS (no Tailwind) | `*.css/*.scss` files AND no `tailwindcss` in deps |

---

## Automated Setup Protocol (For AI Execution)

When user requests linting setup, execute these steps:

### Step 1: Detect Project Type
```bash
# Check for framework indicators
ls package.json next.config.* vite.config.* astro.config.* manifest.json 2>/dev/null
cat package.json | grep -E "next|react|vue|astro|express|fastify|hono|vitest|jest|playwright|obsidian"
# Check for Obsidian manifest
cat manifest.json 2>/dev/null | grep -E "minAppVersion"
```

### Step 2: Install Core Dependencies
```bash
# Core (always install)
pnpm add -D eslint prettier typescript \
  typescript-eslint \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser \
  @stylistic/eslint-plugin \
  eslint-plugin-import \
  eslint-plugin-unicorn \
  eslint-plugin-sonarjs \
  eslint-plugin-promise \
  eslint-config-prettier
```

**Note:** `typescript-eslint` is the unified package required for `tseslint.config()` helper.

### Step 3: Install Conditional Dependencies
```bash
# Frontend with browserslist (if detected)
pnpm add -D eslint-plugin-compat

# HTML files with scripts (if detected)
pnpm add -D eslint-plugin-html

# React/Next.js (if detected)
pnpm add -D eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y

# Next.js specifically (if detected)
pnpm add -D @next/eslint-plugin-next

# Vue (if detected)
pnpm add -D eslint-plugin-vue

# Node.js backend (if express/fastify/hono/koa detected)
pnpm add -D eslint-plugin-n

# Vitest testing (if detected)
pnpm add -D eslint-plugin-vitest

# Playwright E2E (if detected)
pnpm add -D eslint-plugin-playwright

# Jest testing (if detected)
pnpm add -D eslint-plugin-jest

# Obsidian plugin (if detected)
pnpm add -D eslint-plugin-obsidianmd

# Tailwind CSS (if detected)
pnpm add -D eslint-plugin-tailwindcss

# Stylelint for CSS/SCSS (if CSS files exist AND no Tailwind)
pnpm add -D stylelint stylelint-config-standard
```

### Step 4: Create Config Files
Use templates from `templates/` directory:
- `eslint.config.mjs` - ESLint flat config (uncomment relevant sections)
- `.prettierrc` - Standard formatting config
- `tsconfig.json` - Strict TypeScript config (if not exists)

### Step 5: Add Package.json Scripts
```json
{
  "scripts": {
    "lint": "eslint . --max-warnings=0",
    "lint:fix": "eslint . --fix --max-warnings=0",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
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

# Create pre-commit hook
echo "npx lint-staged" > .husky/pre-commit

# Verify setup
git config core.hooksPath && test -x .husky/pre-commit && echo "✓ Husky configured"
```

### Step 7: Add lint-staged Config to package.json

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.vue": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.{css,scss}": ["stylelint --fix", "prettier --write"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.go": ["golangci-lint run --fix"],
    "*.sol": ["solhint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

**What this enforces on every commit:**
- Linting with auto-fix (`eslint --fix`, `ruff check --fix`)
- Formatting (`prettier --write`, `ruff format`)
- Only staged files are processed (fast)

### Framework Detection Matrix

| Indicator | Framework | Additional Plugins |
|-----------|-----------|-------------------|
| `next.config.*` | Next.js | react, react-hooks, jsx-a11y, @next/eslint-plugin-next, compat |
| `"next"` in deps | Next.js | react, react-hooks, jsx-a11y, @next/eslint-plugin-next, compat |
| `"react"` in deps | React | react, react-hooks, jsx-a11y, compat |
| `vue.config.*` | Vue | eslint-plugin-vue, compat |
| `"vue"` in deps | Vue | eslint-plugin-vue, compat |
| `astro.config.*` | Astro | eslint-plugin-astro, compat |
| `"express"/"fastify"/"hono"/"koa"` | Node.js | eslint-plugin-n |
| `"vitest"` in devDeps | Testing | eslint-plugin-vitest |
| `"jest"` in devDeps | Testing | eslint-plugin-jest |
| `"@playwright/test"` in devDeps | E2E Testing | eslint-plugin-playwright |
| `manifest.json` with `minAppVersion` | Obsidian Plugin | eslint-plugin-obsidianmd |
| `"obsidian"` in deps | Obsidian Plugin | eslint-plugin-obsidianmd |
| `browserslist` in package.json | Frontend | eslint-plugin-compat |
| `*.html` files exist | HTML | eslint-plugin-html |
| `"tailwindcss"` in deps | Tailwind CSS | eslint-plugin-tailwindcss |
| `*.css/*.scss` files (no Tailwind) | CSS/SCSS | Stylelint (separate) |
| `hardhat.config.*` | Solidity | Solhint (separate) |

---

## TypeScript/JavaScript (Primary)

### Recommended Stack
- **ESLint** with typescript-eslint (strictTypeChecked)
- **Prettier** for formatting
- **Core plugins**: stylistic, import, unicorn, sonarjs, promise
- **Conditional plugins**: Based on project type (see above)

### Install Commands

**Core (all TypeScript projects):**
```bash
pnpm add -D \
  eslint \
  prettier \
  typescript \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser \
  @stylistic/eslint-plugin \
  eslint-plugin-import \
  eslint-plugin-unicorn \
  eslint-plugin-sonarjs \
  eslint-plugin-promise \
  eslint-config-prettier
```

**Add for Frontend (React/Vue/Next.js):**
```bash
pnpm add -D eslint-plugin-compat
```

**Add for React:**
```bash
pnpm add -D \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y
```

**Add for Next.js:**
```bash
pnpm add -D @next/eslint-plugin-next
```

**Add for Vue:**
```bash
pnpm add -D eslint-plugin-vue
```

**Add for Node.js backend:**
```bash
pnpm add -D eslint-plugin-n
```

**Add for Vitest testing:**
```bash
pnpm add -D eslint-plugin-vitest
```

**Add for Playwright E2E:**
```bash
pnpm add -D eslint-plugin-playwright
```

### Run Commands
```bash
pnpm lint              # Check for errors
pnpm lint --fix        # Auto-fix errors
pnpm format            # Format with Prettier
pnpm format:check      # Check formatting
pnpm typecheck         # TypeScript check
pnpm check             # All checks
```

**Reference:** `references/typescript-eslint.md` for full configuration.

### Framework Extensions

| Framework | Additional Setup |
|-----------|------------------|
| **Next.js** | `pnpm add -D eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y @next/eslint-plugin-next eslint-plugin-compat` |
| **Vue** | `pnpm add -D eslint-plugin-vue eslint-plugin-compat` |
| **Astro** | `pnpm add -D eslint-plugin-astro astro-eslint-parser eslint-plugin-compat prettier-plugin-astro` |
| **Obsidian** | `pnpm add -D eslint-plugin-obsidianmd` |
| **Solidity** | Use Solhint separately (not ESLint) |

**Reference:** `references/typescript-plugins.md` for plugin integration.

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

**Recommended Stack:** golangci-lint v2

### Quick Setup
```bash
brew install golangci-lint
```

### Configuration (.golangci.yml)
```yaml
version: "2"

linters:
  default: all
  disable:
    - depguard
    - exhaustruct

formatters:
  enable:
    - gofmt
    - goimports
```

### Run Commands
```bash
golangci-lint run           # Lint
golangci-lint run --fix     # Lint + auto-fix
go fmt ./...                # Format
```

**Reference:** `references/go-golangci-lint.md` for full configuration.

---

## .NET / C#

**Recommended Stack:** Roslyn Analyzers + dotnet format

### Quick Setup
```bash
dotnet add package Roslynator.Analyzers
dotnet add package StyleCop.Analyzers
dotnet add package SonarAnalyzer.CSharp
```

### Run Commands
```bash
dotnet format                    # Format
dotnet format --verify-no-changes # Check (CI)
dotnet build /warnaserror        # Build with strict warnings
```

**Reference:** `references/dotnet-roslyn.md` for full configuration.

---

## Solidity (Smart Contracts)

**Note:** Solidity uses Solhint (separate from ESLint).

### Quick Setup
```bash
pnpm add -D solhint prettier prettier-plugin-solidity
```

### Run Commands
```bash
npx solhint 'contracts/**/*.sol'           # Lint
npx prettier --write 'contracts/**/*.sol'  # Format
```

**Reference:** `references/typescript-plugins.md` (Solidity section).

---

## CSS/SCSS (Stylelint)

**Note:** Use Stylelint for CSS/SCSS projects WITHOUT Tailwind. For Tailwind projects, use `eslint-plugin-tailwindcss` instead.

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

### Package.json Scripts
```json
{
  "scripts": {
    "lint:css": "stylelint '**/*.css'",
    "lint:css:fix": "stylelint '**/*.css' --fix"
  }
}
```

---

## Pre-commit Hooks (Required)

Pre-commit hooks are **essential** for enforcing code quality. They run automatically on every `git commit`.

### What Gets Enforced

| File Type | Linting | Formatting |
|-----------|---------|------------|
| TypeScript/JS | `eslint --fix` | `prettier --write` |
| Vue | `eslint --fix` | `prettier --write` |
| CSS/SCSS | `stylelint --fix` | `prettier --write` |
| Python | `ruff check --fix` | `ruff format` |
| Go | `golangci-lint --fix` | (included) |
| Solidity | `solhint --fix` | `prettier --write` |
| JSON/MD/YAML | - | `prettier --write` |

### Setup (Husky + lint-staged)
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
echo "npx lint-staged" > .husky/pre-commit
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
    "*.{ts,tsx,js,jsx}": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.vue": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.{css,scss}": ["stylelint --fix", "prettier --write"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.go": ["golangci-lint run --fix"],
    "*.sol": ["solhint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

### Bypassing (Emergency Only)
```bash
git commit --no-verify -m "emergency fix"  # Skip pre-commit hook
```

**Warning:** Only bypass in emergencies. Skipping hooks defeats the purpose of enforced linting.
```

---

## CI/CD Integration

Use templates from `templates/` directory:
- **GitHub Actions**: `templates/.github/workflows/lint.yml`
- **Bitbucket Pipelines**: `templates/bitbucket-pipelines.yml`

Both templates include:
- TypeScript/JavaScript linting (ESLint + Prettier + TypeScript)
- **Test execution with coverage** (`pnpm test:coverage`)
- Commented sections for Python (Ruff + mypy) and Go (golangci-lint)
- Caching for faster builds
- Concurrency controls to cancel outdated runs

**Note:** Tests run after lint passes. Coverage thresholds are enforced in `vitest.config.ts` (see `/typescript` skill for test configuration templates).

---

## Reference Files

| File | Content |
|------|---------|
| `references/typescript-eslint.md` | Full ESLint + plugins configuration |
| `references/typescript-plugins.md` | Astro, Obsidian, Solidity plugins |
| `references/python-ruff-mypy.md` | Ruff + mypy strict configuration |
| `references/go-golangci-lint.md` | golangci-lint v2 setup |
| `references/dotnet-roslyn.md` | Roslyn analyzers + .editorconfig |

## Templates

| File | Content |
|------|---------|
| `templates/CLAUDE.md.template` | Project instructions snippet for Claude Code (delete unused sections!) |
| `templates/eslint.config.mjs` | Full ESLint flat config (core + conditional sections) |
| `templates/tsconfig.json` | Strict TypeScript config |
| `templates/.prettierrc` | Prettier config |
| `templates/.prettierignore` | Prettier ignore patterns |
| `templates/.vscode/settings.json` | VSCode format-on-save integration |
| `templates/.github/workflows/lint.yml` | GitHub Actions CI workflow |
| `templates/bitbucket-pipelines.yml` | Bitbucket Pipelines CI workflow |
| `templates/.husky/pre-commit` | Husky pre-commit hook |
| `templates/lint-staged.config.js` | Lint-staged JS config |
| `templates/pyproject.toml` | Python Ruff + mypy |
| `templates/.golangci.yml` | Go strict config |
| `templates/.editorconfig` | .NET style config |
| `templates/.solhint.json` | Solidity linting |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ESLint conflicts with Prettier | Ensure `eslint-config-prettier` is last in extends |
| Type errors in ESLint | Ensure `tsconfig.json` includes all linted files |
| Import sorting conflicts | Use eslint-plugin-import, disable IDE auto-sort |
| Slow linting | Add `.eslintcache` to speed up, use `--cache` flag |
| Compat plugin errors | Ensure `browserslist` is configured in package.json |
| `stylistic.configs['recommended-flat']` deprecated | Use `stylistic.configs.recommended` instead |
| Astro parser errors with `projectService` | Scope `projectService: true` to `**/*.ts, **/*.tsx` only; use `project: true` for astro files |
| Astro `no-unsafe-*` errors | Astro has limited type inference; disable strict TypeScript rules for `.astro` files |

### Performance Tips

1. **Use caching**: `eslint . --cache`
2. **Lint staged only**: Use `lint-staged` for pre-commit
3. **Incremental TypeScript**: `tsc --incremental`
