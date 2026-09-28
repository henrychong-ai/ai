# Lint Skill

Linting, formatting and git-hook standards across TypeScript/JavaScript, Python, Go, .NET and Solidity.

## Supported Ecosystems

| Ecosystem | Linter | Formatter | Type checker |
|-----------|--------|-----------|--------------|
| TypeScript/JS | Oxlint (+ residual ESLint for gap plugins) | Biome | `tsc` |
| Python | Ruff | Ruff | mypy |
| Go | golangci-lint v2 | gofmt + goimports (baseline) / gofumpt (strict), via golangci-lint | compiler |
| .NET/C# | Roslyn analyzers | `dotnet format` | compiler |
| Solidity | Solhint | Prettier + `prettier-plugin-solidity`, or `forge fmt` | compiler |

Git hooks: Husky pre-commit (gitleaks secret scan, lint-staged) and commit-msg (commitlint).

## Usage

Ask the coding agent, for example:
- "Set up linting for this project"
- "Run lint and fix the errors"
- "Add the pre-commit and commit-msg hooks"
- "Migrate this repo from ESLint + Prettier to Oxlint + Biome"

The agent detects the stack, installs the tools, copies the templates, adds package scripts and hooks, and verifies them.

## Directory Structure

```
lint/
├── SKILL.md                  # Instructions for the coding agent
├── README.md                 # This file
├── TODO.md                   # Open items
├── references/
│   ├── typescript-oxlint-biome.md
│   ├── typescript-residual-eslint.md
│   ├── migration-eslint-prettier-to-oxlint-biome.md
│   ├── git-hooks.md
│   ├── python-ruff-mypy.md
│   ├── go-golangci-lint.md
│   ├── dotnet-roslyn.md
│   └── solidity-solhint-prettier.md
└── templates/                # Ready-to-copy configs (see templates/README.md)
```

## References

| File | When to read |
|------|--------------|
| `typescript-oxlint-biome.md` | Oxlint + Biome setup, plugins, scripts, editor |
| `typescript-residual-eslint.md` | Vue, Astro, Tailwind, Playwright, browser compat |
| `migration-eslint-prettier-to-oxlint-biome.md` | Migrating an existing ESLint + Prettier repo |
| `git-hooks.md` | Husky, lint-staged, gitleaks, commitlint |
| `python-ruff-mypy.md` | Python linting with Ruff + mypy |
| `go-golangci-lint.md` | Go linting with golangci-lint v2 (baseline and strict profiles) |
| `dotnet-roslyn.md` | .NET/C# Roslyn analyzers |
| `solidity-solhint-prettier.md` | Solidity lint and format |

tsconfig and tool version policy come from the `/typescript` skill; CI pipelines are project-specific (SKILL.md has the lint step to add).
