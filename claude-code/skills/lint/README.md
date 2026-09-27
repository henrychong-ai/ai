# Lint Skill

Code quality, linting, and formatting setup across all major ecosystems.

## Supported Ecosystems

| Ecosystem | Linter | Formatter | Type Checker |
|-----------|--------|-----------|--------------|
| TypeScript/JS | Oxlint (primary) + residual ESLint (gap plugins) | Biome | TypeScript |
| Python | Ruff | Ruff | mypy |
| Go | golangci-lint v2 | gofmt | Built-in |
| .NET/C# | Roslyn Analyzers | dotnet format | Built-in |
| Solidity | Solhint | forge fmt / Prettier | N/A |

## TypeScript/JS Architecture

### Oxlint (Primary Linter)
668 built-in rules across 14 native plugins — **zero npm dependencies** for linting. Replaces ESLint + 11 plugins.

### Biome (Formatter Only)
Prettier-compatible formatter with import sorting. Linter **disabled** (oxlint handles all linting).

### Residual ESLint (Gap Plugins Only)
Only needed for Vue templates, Astro, Tailwind CSS, Playwright, Obsidian, and browser compat. Uses `eslint-plugin-oxlint` to prevent duplicate rule checking.

## Usage

**Invoke the skill:**
```
/lint
```

**Or ask Claude Code directly:**
- "Set up linting for this project"
- "Run lint and fix errors"
- "Configure oxlint for React"

## Directory Structure

```
lint/
├── SKILL.md              # Full skill instructions (for Claude Code)
├── README.md             # This file (for humans)
├── references/           # Detailed configuration guides
│   ├── typescript-oxlint-biome.md
│   ├── typescript-residual-eslint.md
│   ├── migration-eslint-prettier-to-oxlint-biome.md
│   ├── python-ruff-mypy.md
│   ├── go-golangci-lint.md
│   └── dotnet-roslyn.md
└── templates/            # Ready-to-copy config files
    ├── README.md         # Template selection guide
    ├── AGENTS.md.template
    ├── oxlint.json
    ├── biome.json
    ├── eslint.config.mjs (residual only)
    ├── tsconfig.json
    └── ... (15 templates total)
```

## Quick Start

1. **Navigate to your project directory**
2. **Invoke the skill**: `/lint`
3. **Claude Code will**:
   - Detect your project type (framework, testing tools)
   - Install core deps (only 3 packages for most projects!)
   - Copy and configure relevant templates
   - Set up package.json scripts

## Features

- **Minimal Dependencies**: 3 packages for most projects (oxlint + biome + typescript)
- **Automated Setup**: Detects framework and enables correct oxlint plugins
- **Smart Plugin Selection**: Oxlint built-in plugins first, residual ESLint only for gaps
- **CI/CD Ready**: GitHub Actions and Bitbucket Pipelines templates
- **Pre-commit Hooks**: Husky + lint-staged configuration
- **IDE Integration**: VSCode settings for Biome format-on-save + Oxlint fix-on-save

## References

| File | When to Read |
|------|--------------|
| `typescript-oxlint-biome.md` | Full Oxlint + Biome setup, plugin coverage, migration guide |
| `typescript-residual-eslint.md` | Adding Vue, Astro, Tailwind, Playwright, Obsidian, Compat support |
| `migration-eslint-prettier-to-oxlint-biome.md` | Migrating an existing ESLint + Prettier repo to Oxlint + Biome |
| `python-ruff-mypy.md` | Python linting with Ruff + mypy |
| `go-golangci-lint.md` | Go linting with golangci-lint v2 |
| `dotnet-roslyn.md` | .NET/C# Roslyn analyzers setup |

## See Also

- **SKILL.md**: Complete skill instructions (Claude Code reads this)
- **templates/README.md**: Which templates to copy for your project
