# Lint Skill Templates

Ready-to-copy configuration files for linting and formatting.

## Template Selection by Ecosystem

### TypeScript/JavaScript (All Projects)

**Always copy:**
```bash
cp oxlint.json biome.json tsconfig.json /your/project/
```

**If residual ESLint needed (Vue templates, Astro, Tailwind, Playwright, Obsidian, Compat):**
```bash
cp eslint.config.mjs /your/project/
```
Uncomment relevant sections in `eslint.config.mjs`.

| Project Type | Residual ESLint Needed? | Sections to Uncomment |
|--------------|------------------------|----------------------|
| React | No (oxlint built-in) | - |
| Next.js | No (oxlint built-in) | - |
| Node.js | No (oxlint built-in) | - |
| Vitest/Jest | No (oxlint built-in) | - |
| Vue | Yes | vue |
| Astro | Yes | astro |
| Tailwind CSS | Yes | better-tailwindcss |
| Playwright | Yes | playwright |
| Obsidian | Yes | obsidianmd |
| Browser compat | Yes | compat |

### Python

```bash
cp pyproject.toml /your/project/
```

### Go

```bash
cp .golangci.yml /your/project/
```

### .NET/C#

```bash
cp .editorconfig /your/project/
```

### Solidity

```bash
cp .solhint.json /your/project/
```

## Optional Templates

### IDE Integration

```bash
mkdir -p .vscode && cp .vscode/settings.json /your/project/.vscode/
```

### CI/CD Workflows

| Platform | Command |
|----------|---------|
| GitHub Actions | `mkdir -p .github/workflows && cp .github/workflows/lint.yml /your/project/.github/workflows/` |
| Bitbucket | `cp bitbucket-pipelines.yml /your/project/` |

### Pre-commit Hooks (lint-staged + gitleaks secret scan)

```bash
mkdir -p .husky && cp .husky/pre-commit /your/project/.husky/
cp lint-staged.config.js /your/project/
cp .gitleaks.toml /your/project/          # canonical secret-scan config (repo root)
```

Then run:
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
brew install gitleaks                      # the hook calls gitleaks; CI enforces it too
```

The hook runs **gitleaks** (blocks secrets + `.env` files) before lint-staged. The same `.gitleaks.toml` is auto-discovered by a gitleaks secret-scan step in your CI pipeline — single source, no drift.

### Project Instructions (AGENTS.md + CLAUDE.md shim)

```bash
cp AGENTS.md.template /your/project/AGENTS.md
printf '@AGENTS.md\n' > /your/project/CLAUDE.md   # import shim for Claude Code
```

**Important:** Edit AGENTS.md and delete unused sections to save tokens.

## Template List

| File | Ecosystem | Purpose |
|------|-----------|---------|
| `AGENTS.md.template` | All | Project instructions (`AGENTS.md`, imported by a `CLAUDE.md` `@AGENTS.md` shim) |
| `oxlint.json` | TS/JS | Oxlint config with plugin sections |
| `biome.json` | TS/JS | Biome formatter (linter disabled) |
| `eslint.config.mjs` | TS/JS | Residual ESLint (gap plugins only) |
| `tsconfig.json` | TS/JS | Strict TypeScript compiler options |
| `.vscode/settings.json` | All | VSCode format-on-save (Biome + Oxlint) |
| `.github/workflows/lint.yml` | All | GitHub Actions CI |
| `bitbucket-pipelines.yml` | All | Bitbucket Pipelines CI |
| `.husky/pre-commit` | All | Pre-commit hook (gitleaks secret-scan + lint-staged) |
| `.gitleaks.toml` | All | Canonical gitleaks config — blocks secrets + .env (copy to repo root) |
| `lint-staged.config.js` | All | Lint-staged configuration |
| `pyproject.toml` | Python | Ruff + mypy config |
| `.golangci.yml` | Go | golangci-lint v2 config |
| `.editorconfig` | .NET | Roslyn analyzer settings |
| `.solhint.json` | Solidity | Solhint rules |
