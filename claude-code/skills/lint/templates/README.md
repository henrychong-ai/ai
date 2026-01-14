# Lint Skill Templates

Ready-to-copy configuration files for linting and formatting.

## Template Selection by Ecosystem

### TypeScript/JavaScript (All Projects)

**Always copy:**
```bash
cp eslint.config.mjs tsconfig.json .prettierrc .prettierignore /your/project/
```

**Uncomment sections in `eslint.config.mjs` based on your project:**

| Project Type | Sections to Uncomment |
|--------------|----------------------|
| Frontend with `browserslist` | compat |
| HTML files with inline scripts | html |
| React | react, react-hooks, jsx-a11y, compat |
| Next.js | react, react-hooks, jsx-a11y, @next/next, compat |
| Vue | vue, compat |
| Node.js backend | n |
| Vitest testing | vitest |
| Playwright E2E | playwright |

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
cp .solhint.json .prettierrc /your/project/
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

### Pre-commit Hooks

```bash
mkdir -p .husky && cp .husky/pre-commit /your/project/.husky/
cp lint-staged.config.js /your/project/
```

Then run:
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
```

### Claude Code Project Instructions

```bash
cp CLAUDE.md.template /your/project/CLAUDE.md
```

**Important:** Edit CLAUDE.md and delete unused sections to save tokens.

## Template List

| File | Ecosystem | Purpose |
|------|-----------|---------|
| `CLAUDE.md.template` | All | Project instructions for Claude Code |
| `eslint.config.mjs` | TS/JS | ESLint flat config with plugins |
| `tsconfig.json` | TS/JS | Strict TypeScript compiler options |
| `.prettierrc` | TS/JS | Prettier formatting rules |
| `.prettierignore` | TS/JS | Prettier ignore patterns |
| `.vscode/settings.json` | All | VSCode format-on-save |
| `.github/workflows/lint.yml` | All | GitHub Actions CI |
| `bitbucket-pipelines.yml` | All | Bitbucket Pipelines CI |
| `.husky/pre-commit` | All | Pre-commit hook |
| `lint-staged.config.js` | All | Lint-staged configuration |
| `pyproject.toml` | Python | Ruff + mypy config |
| `.golangci.yml` | Go | golangci-lint v2 config |
| `.editorconfig` | .NET | Roslyn analyzer settings |
| `.solhint.json` | Solidity | Solhint rules |
