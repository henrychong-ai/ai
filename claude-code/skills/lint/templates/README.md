# Lint Skill Templates

Ready-to-copy configuration files. Paths are relative to this `templates/` directory.

## TypeScript/JavaScript

```bash
cp .oxlintrc.json biome.json <project>/
cp eslint.config.mjs <project>/        # only for residual ESLint gap plugins
```

Set Oxlint `plugins` for the project type, and keep only the needed sections of `eslint.config.mjs`:

| Project type | Residual ESLint? | Section |
|--------------|------------------|---------|
| React, Vite + React, Next.js, Node.js, Vitest/Jest | No (Oxlint built in) | - |
| Vue | Yes | vue |
| Astro | Yes | astro |
| Tailwind CSS v4 | Yes | better-tailwindcss |
| Playwright | Yes | playwright |
| Browser compat | Yes | compat |

tsconfig comes from the `/typescript` skill.

## Git Hooks (every repo)

```bash
mkdir -p <project>/.husky
cp .husky/pre-commit .husky/commit-msg <project>/.husky/
cp .gitleaks.toml lint-staged.config.mjs commitlint.config.mjs <project>/
```

Then in the project:

```bash
pnpm add -D husky lint-staged @commitlint/cli @commitlint/config-conventional
pnpm exec husky init
brew install gitleaks
```

The pre-commit hook runs gitleaks (blocks secrets and `.env` files) and then lint-staged; the commit-msg hook runs commitlint. The CI secret-scan step reads the same `.gitleaks.toml`.

## Other Languages

```bash
cp pyproject.toml <project>/                                   # Python: merge the tables
cp .golangci.yml <project>/                                    # Go baseline
cp .golangci.strict.yml <project>/.golangci.yml                # Go strict profile (opt-in)
cp .editorconfig <solution-root>/                              # .NET
cp .solhint.json <project>/                                    # Solidity
cp test/.solhint.json <project>/test/                          # Solidity test-directory overrides
```

Run `golangci-lint config verify` after copying a Go config.

## Editor and Project Instructions

```bash
mkdir -p <project>/.vscode && cp .vscode/settings.json .vscode/extensions.json <project>/.vscode/
```

Merge `AGENTS.md.template` into the project's `AGENTS.md` (with a one-line `@AGENTS.md` `CLAUDE.md` shim) and delete the parts that do not apply.

## Template List

| File | Ecosystem | Purpose |
|------|-----------|---------|
| `.oxlintrc.json` | TS/JS | Oxlint config (auto-discovered) |
| `biome.json` | TS/JS | Biome formatter + import sorting, linter off |
| `eslint.config.mjs` | TS/JS | Residual ESLint (gap plugins only) |
| `lint-staged.config.mjs` | All | Staged-file commands |
| `.husky/pre-commit` | All | gitleaks secret scan, then lint-staged |
| `.husky/commit-msg` | All | commitlint |
| `commitlint.config.mjs` | All | Commit header rules |
| `.gitleaks.toml` | All | Canonical gitleaks config |
| `.vscode/settings.json` | TS/JS | Biome format-on-save, Oxlint fix-on-save |
| `.vscode/extensions.json` | TS/JS | Recommended extensions |
| `AGENTS.md.template` | All | Code-quality section for AGENTS.md |
| `pyproject.toml` | Python | Ruff + mypy |
| `.golangci.yml` | Go | golangci-lint v2 baseline |
| `.golangci.strict.yml` | Go | golangci-lint v2 opt-in strict profile |
| `.editorconfig` | .NET | Style and analyzer severities |
| `.solhint.json` | Solidity | Solhint rules |
| `test/.solhint.json` | Solidity | Test and harness relaxations (nested config) |
