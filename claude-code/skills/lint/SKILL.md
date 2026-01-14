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
| **eslint-plugin-playwright** | Playwright E2E | `@playwright/test` in devDependencies |

---

## Automated Setup Protocol (For AI Execution)

When user requests linting setup, execute these steps:

### Step 1: Detect Project Type
```bash
# Check for framework indicators
ls package.json next.config.* vite.config.* astro.config.* 2>/dev/null
cat package.json | grep -E "next|react|vue|astro|express|fastify|hono|vitest|playwright"
```

### Step 2: Install Core Dependencies
```bash
# Core (always install)
pnpm add -D eslint prettier typescript \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser \
  @stylistic/eslint-plugin \
  eslint-plugin-import \
  eslint-plugin-unicorn \
  eslint-plugin-sonarjs \
  eslint-plugin-promise \
  eslint-config-prettier
```

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

### Step 6: Setup Pre-commit Hooks (Optional)
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
echo "npx lint-staged" > .husky/pre-commit
```

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
| `"@playwright/test"` in devDeps | E2E Testing | eslint-plugin-playwright |
| `browserslist` in package.json | Frontend | eslint-plugin-compat |
| `*.html` files exist | HTML | eslint-plugin-html |
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
| **Astro** | `pnpm add -D eslint-plugin-astro astro-eslint-parser eslint-plugin-compat` |
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
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM", "TCH", "RUF"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
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

## Pre-commit Hooks

### Setup (Husky + lint-staged)
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
echo "npx lint-staged" > .husky/pre-commit
```

### lint-staged Config (package.json)
```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.vue": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.go": ["golangci-lint run --fix"],
    "*.cs": ["dotnet format --include"],
    "*.sol": ["solhint", "prettier --write"],
    "*.{json,md,yml,yaml,css,scss}": ["prettier --write"]
  }
}
```

---

## CI/CD Integration

Use templates from `templates/` directory:
- **GitHub Actions**: `templates/.github/workflows/lint.yml`
- **Bitbucket Pipelines**: `templates/bitbucket-pipelines.yml`

Both templates include:
- TypeScript/JavaScript linting (ESLint + Prettier + TypeScript)
- Commented sections for Python (Ruff + mypy) and Go (golangci-lint)
- Caching for faster builds
- Concurrency controls to cancel outdated runs

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

### Performance Tips

1. **Use caching**: `eslint . --cache`
2. **Lint staged only**: Use `lint-staged` for pre-commit
3. **Incremental TypeScript**: `tsc --incremental`
