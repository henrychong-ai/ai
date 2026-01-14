# Lint Skill

Code quality, linting, and formatting setup across all major ecosystems.

## Supported Ecosystems

| Ecosystem | Linter | Formatter | Type Checker |
|-----------|--------|-----------|--------------|
| TypeScript/JS | ESLint + Plugins | Prettier | TypeScript |
| Python | Ruff | Ruff | mypy |
| Go | golangci-lint v2 | gofmt | Built-in |
| .NET/C# | Roslyn Analyzers | dotnet format | Built-in |
| Solidity | Solhint | Prettier | N/A |

## ESLint Plugin Architecture

### Core Plugins (Always Enabled)
| Plugin | Purpose |
|--------|---------|
| @typescript-eslint | TypeScript type checking |
| @stylistic | Code style (spacing, braces) |
| eslint-plugin-import | Import validation |
| eslint-plugin-unicorn | Modern JS best practices |
| eslint-plugin-sonarjs | Bug detection patterns |
| eslint-plugin-promise | Async/Promise patterns |
| eslint-config-prettier | Disable conflicting rules |

### Conditional Plugins (Based on Project Type)
| Plugin | When to Enable |
|--------|----------------|
| eslint-plugin-compat | Frontend with `browserslist` |
| eslint-plugin-html | Projects with inline scripts in HTML |
| eslint-plugin-react | React projects |
| eslint-plugin-react-hooks | React projects |
| eslint-plugin-jsx-a11y | React/JSX accessibility |
| @next/eslint-plugin-next | Next.js projects |
| eslint-plugin-vue | Vue projects |
| eslint-plugin-n | Node.js backends (Express, Fastify, Hono, Koa) |
| eslint-plugin-vitest | Vitest unit/integration testing |
| eslint-plugin-playwright | Playwright E2E testing |

## Usage

**Invoke the skill:**
```
/lint
```

**Or ask Claude Code directly:**
- "Set up linting for this project"
- "Run lint and fix errors"
- "Configure ESLint for React"

## Directory Structure

```
lint/
├── SKILL.md              # Full skill instructions (for Claude Code)
├── README.md             # This file (for humans)
├── references/           # Detailed configuration guides
│   ├── typescript-eslint.md
│   ├── typescript-plugins.md
│   ├── python-ruff-mypy.md
│   ├── go-golangci-lint.md
│   └── dotnet-roslyn.md
└── templates/            # Ready-to-copy config files
    ├── README.md         # Template selection guide
    ├── CLAUDE.md.template
    ├── eslint.config.mjs
    ├── tsconfig.json
    └── ... (14 templates total)
```

## Quick Start

1. **Navigate to your project directory**
2. **Invoke the skill**: `/lint`
3. **Claude Code will**:
   - Detect your project type (framework, testing tools)
   - Install core + conditional dependencies
   - Copy and configure relevant templates
   - Set up package.json scripts

## Features

- **Automated Setup**: Detects framework and installs correct plugins
- **Smart Plugin Selection**: Core plugins always, conditional based on detection
- **Manual Config**: Full ESLint flat config (no black-box dependencies)
- **CI/CD Ready**: GitHub Actions and Bitbucket Pipelines templates
- **Pre-commit Hooks**: Husky + lint-staged configuration
- **IDE Integration**: VSCode settings for format-on-save

## References

| File | When to Read |
|------|--------------|
| `typescript-eslint.md` | Full ESLint + TypeScript setup details |
| `typescript-plugins.md` | Adding Astro, Vue, Obsidian, Solidity support |
| `python-ruff-mypy.md` | Python linting with Ruff + mypy |
| `go-golangci-lint.md` | Go linting with golangci-lint v2 |
| `dotnet-roslyn.md` | .NET/C# Roslyn analyzers setup |

## See Also

- **SKILL.md**: Complete skill instructions (Claude Code reads this)
- **templates/README.md**: Which templates to copy for your project
