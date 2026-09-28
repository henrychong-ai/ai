# Git Hooks: Husky, lint-staged, gitleaks, commitlint

Two hooks run on every commit:

| Hook | Runs | Template |
|------|------|----------|
| `pre-commit` | gitleaks secret scan on staged changes, then lint-staged | `templates/.husky/pre-commit`, `templates/.gitleaks.toml`, `templates/lint-staged.config.mjs` |
| `commit-msg` | commitlint on the commit message | `templates/.husky/commit-msg`, `templates/commitlint.config.mjs` |

CI runs the same secret scan and lint checks, so skipping hooks locally (`--no-verify`) does not get a change merged. Reserve `--no-verify` for emergencies.

## Setup

```bash
pnpm add -D husky lint-staged @commitlint/cli @commitlint/config-conventional
pnpm exec husky init            # creates .husky/ and the "prepare": "husky" script

# from this skill's templates/ directory
cp templates/.husky/pre-commit   <repo>/.husky/pre-commit
cp templates/.husky/commit-msg   <repo>/.husky/commit-msg
cp templates/.gitleaks.toml      <repo>/.gitleaks.toml
cp templates/lint-staged.config.mjs <repo>/lint-staged.config.mjs
cp templates/commitlint.config.mjs  <repo>/commitlint.config.mjs

brew install gitleaks           # the pre-commit hook calls it; CI enforces it too
```

Verify:

```bash
git config core.hooksPath                   # .husky/_
test -x .husky/pre-commit && test -x .husky/commit-msg && echo "hooks executable"
pnpm exec lint-staged --verbose            # with a file staged; runs the tasks (there is no dry-run mode)
echo "[ABC-1] test commitlint" | pnpm exec commitlint
```

## gitleaks (pre-commit + CI)

`templates/.gitleaks.toml` is the canonical config: it extends gitleaks' built-in rules and adds a filename rule that blocks committing a real `.env` file (`.env.example`, `.env.sample`, `.env.template` and `.env.dist` are allowed). gitleaks finds `.gitleaks.toml` at the repo root, so the hook and the CI scan share it.

The hook runs `gitleaks git --staged --no-banner --redact`. When gitleaks is not installed it prints a warning and continues; CI still blocks the secret.

For a false positive, add a top-level `[[allowlists]]` block with at least one check (`paths`, `regexes`, `commits` or `stopwords`); an empty block fails to load. Keep each entry narrow: every entry is a hole in the scanner.

## lint-staged (pre-commit)

`templates/lint-staged.config.mjs` (`.mjs` so the ESM export loads whatever the package's `"type"` is). Patterns:

| Files | Commands |
|-------|----------|
| TS/JS | `oxlint --fix --max-warnings=0`, `biome check --write --no-errors-on-unmatched` |
| Vue | `oxlint --fix --max-warnings=0` |
| CSS, JSON | `biome check --write --no-errors-on-unmatched` |
| Python | `ruff check --fix`, `ruff format` |
| Go | `() => "golangci-lint run --fix ./..."` (whole module; golangci-lint lints packages, not file lists) |
| Solidity | `solhint --fix --noPrompt`, then `prettier --write` (Hardhat) or `forge fmt` (Foundry) |
| C# | `dotnet format --include` |

Keep Markdown, YAML and HTML out of Biome globs: Biome does not format them yet, and a staged file Biome skips fails the hook. Residual-ESLint projects add `eslint --fix --max-warnings=0` to the matching globs.

The package.json `"lint-staged"` field works for simple setups; JSON cannot hold the Go function form, so use `"*.go": "bash -c 'golangci-lint run --fix ./...'"` there.

## commitlint (commit-msg)

`templates/commitlint.config.mjs` extends `@commitlint/config-conventional` and teaches the parser two header shapes:

- ticket-first: `[ABC-123] add retry to the sync job`
- Conventional Commits: `feat(api): add retry`

The message format itself (ticket keys, when each shape applies, branch naming) is defined by your team's contribution guidelines; this config only enforces it. Change the ticket-key pattern in `HEADER_PATTERN` to match your tracker. Headers matching neither shape fail `subject-empty`. Merge and revert commits pass through commitlint's default ignores. The template is lenient so it does not block an existing history: `subject-case` is off (capitalised subjects pass) and `header-max-length` warns above 100 characters instead of failing; the shape, `subject-empty`, `subject-full-stop` and `body-max-line-length` still fail the commit. Tighten them in the config if your conventions require it.

`.husky/commit-msg`:

```sh
npx --no -- commitlint --edit "$1"
```

A CommonJS repo can keep `commitlint.config.cjs` with `module.exports = { … }`; the rules are the same.

## Other Ecosystems

- **Python only (no Node tooling):** the pre-commit framework, see `python-ruff-mypy.md` → Pre-commit.
- **Go only:** `.pre-commit-config.yaml` hooks from golangci-lint, see `go-golangci-lint.md` → Pre-commit Hook.
- **.NET only:** Husky.Net, see `dotnet-roslyn.md` → Pre-commit Integration.

Add gitleaks to those setups too (`https://github.com/gitleaks/gitleaks`, hook id `gitleaks`).
