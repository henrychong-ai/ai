---
name: lint
description: Linting, formatting and git-hook standards — sets up, runs and fixes code-quality tooling for TypeScript/JavaScript (Oxlint + Biome, residual ESLint for Vue/Astro/Tailwind/Playwright gaps), Python (Ruff, mypy), Go (golangci-lint v2), .NET (Roslyn analyzers, dotnet format) and Solidity (Solhint + Prettier or forge fmt), plus pre-commit hooks (Husky, lint-staged, gitleaks secret scan) and the commitlint commit-msg hook. Use when adding or configuring linting, fixing lint or format errors, setting up pre-commit or commit-msg hooks, or migrating ESLint + Prettier to Oxlint + Biome.
---

# Lint Skill

Standard code-quality tooling: which linter and formatter each language uses, the config templates, and the git hooks that enforce them.

**Versions:** Node, TypeScript, pnpm and JS/TS tool version policy is owned by `/typescript` → `references/tech-stack/version-policy.md`. Check live versions before pinning (`npm view oxlint version`, `npm view @biomejs/biome version`) rather than relying on numbers written here.

**Paths:** `templates/` and `references/` below are relative to this skill's directory.

## Stack by Language

| Language | Lint | Format | Types | Config |
|----------|------|--------|-------|--------|
| TypeScript/JS | Oxlint (+ residual ESLint for gap plugins) | Biome (linter off) | `tsc --noEmit` | `.oxlintrc.json`, `biome.json` |
| Python | Ruff | Ruff | mypy | `pyproject.toml` |
| Go | golangci-lint v2 | gofmt + goimports (baseline) or gofumpt (strict), via golangci-lint | compiler | `.golangci.yml` |
| .NET/C# | Roslyn analyzers | `dotnet format` | compiler | `.editorconfig`, `Directory.Build.props` |
| Solidity | Solhint | Prettier + `prettier-plugin-solidity` (Hardhat) or `forge fmt` (Foundry) | compiler | `.solhint.json`, `.prettierrc.json` |

Every repo also gets the git hooks: gitleaks + lint-staged on pre-commit, commitlint on commit-msg (`references/git-hooks.md`).

## TypeScript/JavaScript Setup

1. **Detect the project** from package.json and config files:

   | Indicator | Oxlint `plugins` to add | Residual ESLint plugin |
   |-----------|-------------------------|------------------------|
   | Any TS/JS | `typescript`, `unicorn`, `oxc`, `import`, `promise` | — |
   | `react` (incl. Vite + React) | `react`, `jsx-a11y` | — |
   | `next` / `next.config.*` | `react`, `jsx-a11y`, `nextjs` | — |
   | `express` / `fastify` / `hono` / `koa` | `node` | — |
   | `vitest` / `jest` | `vitest` / `jest` | — |
   | `vue` | `vue` | `eslint-plugin-vue` (templates) |
   | `astro.config.*` | — | `eslint-plugin-astro` |
   | `tailwindcss` ^4 | — | `eslint-plugin-better-tailwindcss` |
   | `@playwright/test` | — | `eslint-plugin-playwright` |
   | browserslist config | — | `eslint-plugin-compat` |
   | `hardhat.config.*` / `foundry.toml` | — | Solidity section below |

2. **Install:** `pnpm add -D oxlint @biomejs/biome`. Only if a residual plugin applies: `pnpm add -D eslint eslint-plugin-oxlint typescript-eslint` plus the gap plugins.
3. **Copy configs:** `templates/.oxlintrc.json` (set `plugins`), `templates/biome.json`, and `templates/eslint.config.mjs` only for residual ESLint (keep the needed sections). tsconfig comes from `/typescript` (`references/coding-standards/tooling.md`).
4. **Scripts:**

   ```json
   {
     "lint": "oxlint --max-warnings=0",
     "lint:fix": "oxlint --fix --max-warnings=0",
     "format": "biome check --write .",
     "format:check": "biome check .",
     "typecheck": "tsc --noEmit",
     "check": "pnpm lint && pnpm format:check && pnpm typecheck"
   }
   ```

   Residual ESLint appends `&& eslint . --max-warnings=0` to `lint` (and `--fix` to `lint:fix`).
5. **Hooks:** Husky + lint-staged + gitleaks + commitlint (`references/git-hooks.md`).
6. **Verify:** `pnpm check` passes, with a file staged, `pnpm exec lint-staged --verbose` runs the expected commands (lint-staged has no dry-run mode), and `oxlint` reports the rule count of your config (not the defaults).

Rules to keep in mind:
- Oxlint auto-discovers only `.oxlintrc.json` / `.oxlintrc.jsonc` / `oxlint.config.ts`. A repo with `oxlint.json` must pass `-c oxlint.json` everywhere, or its config is silently ignored.
- `plugins` replaces Oxlint's defaults: list `typescript`, `unicorn` and `oxc` explicitly.
- Oxlint's type-aware rules (`no-floating-promises`, `no-unsafe-*`) are opt-in: they need `oxlint-tsgolint` and a TS 7-ready tsconfig (no `baseUrl`). Upstream documents TS 7; they were observed working on TS 6.0.3 (2026-09-28). `tsc --noEmit` stays the type gate.
- New repos use Biome's default JS style (double quotes, `arrowParentheses: "always"`); existing repos keep their configured style.
- Run `biome migrate --write` after every Biome upgrade so `$schema` matches the installed version.
- Biome formats JS/TS, JSON, CSS and GraphQL. Markdown, YAML and HTML stay out of Biome globs.

Details: `references/typescript-oxlint-biome.md` (Oxlint, Biome, scripts, editor), `references/typescript-residual-eslint.md` (gap plugins), `references/migration-eslint-prettier-to-oxlint-biome.md` (migrating an existing repo).

## Python

Recommended standard for new Python work. `uv add --dev ruff mypy`, merge `templates/pyproject.toml`, then run `ruff check .`, `ruff format --check .` and `mypy src/`. Details: `references/python-ruff-mypy.md`.

## Go

**Recommended Stack:** golangci-lint v2 (pinned version). It runs the linters and the formatters (gofmt/goimports, or gofumpt in the strict profile); no standalone formatter install is needed.

### Quick Setup
```bash
# Binary (upstream-recommended), pinned
curl -sSfL https://golangci-lint.run/install.sh | sh -s -- -b $(go env GOPATH)/bin v2.14.0
# or on macOS
brew install golangci-lint
```

Source installs must use the v2 module path (`go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.14.0`); upstream does not guarantee `go install` or `go get -tool` / `go tool` installs and recommends the binary.

### Configuration (.golangci.yml): Baseline or Strict

| Profile | Template | What it runs | When |
|---------|----------|--------------|------|
| **Baseline** (default) | `templates/.golangci.yml` | v2 `standard` linters (errcheck, govet, ineffassign, staticcheck, unused) + gofmt/goimports | Every Go repo; the low-friction default most codebases pass with few changes |
| **Strict** (opt-in) | `templates/.golangci.strict.yml` | `default: all` minus a documented disable list, gofumpt | New or clean codebases, adopted deliberately |

Copy one to the module root as `.golangci.yml`, then check it:

```bash
golangci-lint config verify    # must pass before committing the config
```

Repos still pinning golangci-lint v1 (for example as a Go `tool` dependency) cannot read these files: run `golangci-lint migrate`, then `config verify`, and switch to a pinned v2 binary.

### Run Commands
```bash
golangci-lint run ./...             # Lint + formatter checks
golangci-lint run --fix ./...       # Lint + auto-fix + format
golangci-lint fmt ./...             # Format only
golangci-lint run --fast-only ./... # Fast linters only (v2; replaces --fast)
```

In CI, use `golangci/golangci-lint-action@v9` with a pinned `version: v2.x` and `go-version-file: go.mod`.

**Reference:** `references/go-golangci-lint.md` for both configs, the v1→v2 layout table, CI, pre-commit and troubleshooting.

## .NET / C#

Roslyn analyzers run in every build; `dotnet format` formats. Set `AnalysisLevel` `latest-recommended` (the opt-in strict profile is `latest-all`), `EnforceCodeStyleInBuild` and `TreatWarningsAsErrors` in `Directory.Build.props`, and declare StyleCop, Roslynator and Sonar analyzers as `GlobalPackageReference` under Central Package Management. Copy `templates/.editorconfig` to the solution root.

```bash
dotnet format --verify-no-changes   # CI format gate
dotnet build -warnaserror           # analyzers run as part of the build
```

Details: `references/dotnet-roslyn.md`; where a `/dotnet` skill is installed, its `references/coding-standards/tooling.md` holds the full .NET conventions.

## Solidity

Hardhat projects format with Prettier + `prettier-plugin-solidity`; Foundry projects use `forge fmt`. Solhint lints both (`templates/.solhint.json`).

```bash
pnpm exec solhint "contracts/**/*.sol"
pnpm exec prettier --check "contracts/**/*.sol"   # or: forge fmt --check
```

Details: `references/solidity-solhint-prettier.md`. Contract standards: a `/solidity` skill where installed.

## CI

Run the same checks as the hooks, as their own pipeline step, after dependency install:

```bash
pnpm lint && pnpm format:check && pnpm typecheck    # TS/JS
golangci-lint run ./...                              # Go
uv run ruff check . && uv run ruff format --check . && uv run mypy src/   # Python
dotnet format --verify-no-changes && dotnet build -warnaserror            # .NET
```

Also run gitleaks in CI with the same `.gitleaks.toml`, so skipped local hooks cannot merge a secret. GitHub Actions example:

```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
      with: { fetch-depth: 0 }
    - uses: gitleaks/gitleaks-action@v3   # organisation repos also need a GITLEAKS_LICENSE secret
      env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
    - uses: pnpm/action-setup@v6      # reads the pnpm version from package.json packageManager
    - uses: actions/setup-node@v7
      with: { node-version-file: .nvmrc, cache: pnpm }
    - run: pnpm install --frozen-lockfile
    - run: pnpm lint && pnpm format:check && pnpm typecheck
```

## References

| File | Content |
|------|---------|
| `references/typescript-oxlint-biome.md` | Oxlint config and plugins, type-aware rules, Biome config and language support, scripts, editor, monorepos |
| `references/typescript-residual-eslint.md` | Gap plugins: Vue, Astro, Tailwind v4, Playwright, browser compat |
| `references/migration-eslint-prettier-to-oxlint-biome.md` | Step-by-step migration of an ESLint + Prettier repo |
| `references/git-hooks.md` | Husky, lint-staged, gitleaks, commitlint |
| `references/python-ruff-mypy.md` | Ruff + mypy config, rule sets, adoption |
| `references/go-golangci-lint.md` | golangci-lint v2: baseline vs strict, install, v1 migration, CI, hooks |
| `references/dotnet-roslyn.md` | Roslyn analyzers, `.editorconfig`, strict profile |
| `references/solidity-solhint-prettier.md` | Solhint, Prettier-solidity, forge fmt |

## Templates

| File | Content |
|------|---------|
| `templates/.oxlintrc.json` | Oxlint config (auto-discovered) |
| `templates/biome.json` | Biome formatter + import sorting, linter off |
| `templates/eslint.config.mjs` | Residual ESLint, gap-plugin sections commented out |
| `templates/lint-staged.config.mjs` | Staged-file commands for every language |
| `templates/.husky/pre-commit` | gitleaks secret scan, then lint-staged |
| `templates/.husky/commit-msg` | commitlint |
| `templates/commitlint.config.mjs` | Ticket-first and Conventional Commits headers |
| `templates/.gitleaks.toml` | Canonical gitleaks config (blocks secrets and `.env` files) |
| `templates/.vscode/settings.json`, `templates/.vscode/extensions.json` | Biome format-on-save, Oxlint fix-on-save, recommended extensions |
| `templates/AGENTS.md.template` | Code-quality section for a project's AGENTS.md |
| `templates/pyproject.toml` | Ruff + mypy |
| `templates/.golangci.yml`, `templates/.golangci.strict.yml` | Go baseline and opt-in strict profile |
| `templates/.editorconfig` | .NET style and analyzer severities |
| `templates/.solhint.json` | Solhint rules |
| `templates/test/.solhint.json` | Solhint relaxations for test and harness contracts (copy to `test/.solhint.json`) |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Oxlint ignores the config (only default rules report) | Rename to `.oxlintrc.json`, or pass `-c <file>` |
| `Rule '…' not found in plugin '…'` | The rule was removed or renamed upstream; delete it from the config |
| A plugin's rules never fire | The plugin is missing from `plugins` (the list replaces the defaults) |
| Biome "No files were processed" in a hook | A glob passes a type Biome does not format (md, yaml, html); narrow it or add `--no-errors-on-unmatched` |
| Biome formats `node_modules` or build output in CI | Enable `vcs` integration; add `.pnpm-store/` to `.gitignore` |
| Biome `$schema` version warning | `pnpm exec biome migrate --write` |
| Biome fails on Tailwind CSS directives | `"css": { "parser": { "tailwindDirectives": true } }` |
| Residual ESLint "Unexpected token" on `.ts` | Add the `typescript-eslint` parser block |
| Residual ESLint duplicates Oxlint findings | `...oxlint.buildFromOxlintConfigFile("./.oxlintrc.json")` must be the last entry |
| `configs['flat/recommended']` undefined for better-tailwindcss | Spread `configs.recommended` into one block (see residual reference) |
| golangci-lint config errors | v1 layout: `golangci-lint migrate`, then `golangci-lint config verify` |
