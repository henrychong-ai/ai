# TypeScript/JavaScript Linting with Oxlint + Biome

Primary linting via Oxlint (668 built-in rules, native plugins). Formatting via Biome (Prettier-compatible, linter disabled). Type checking via tsc.

## Architecture

```
┌─────────────────────────────────┐
│ Oxlint (primary linter)         │  No npm deps for linting
│  └─ 668 built-in rules          │
│  └─ Native plugins (below)      │
├─────────────────────────────────┤
│ Biome (formatter only)          │  1 npm dep: @biomejs/biome
│  └─ Prettier-compatible         │
│  └─ Import sorting              │
│  └─ Linter DISABLED             │
├─────────────────────────────────┤
│ Residual ESLint (gap only)      │  Only when gap plugins needed
│  └─ eslint-plugin-oxlint        │
│  └─ Vue/Astro/Tailwind/etc.     │
├─────────────────────────────────┤
│ tsc (type checker)              │  Unchanged
└─────────────────────────────────┘
```

## Package Overview

### Core Packages (Always Required)

| Package | Purpose | Install |
|---------|---------|---------|
| `oxlint` | Primary linter (668 rules, native plugins) | `pnpm add -D oxlint` |
| `@biomejs/biome` | Formatter + import sorting (linter disabled) | `pnpm add -D @biomejs/biome` |
| `typescript` | Type checker | `pnpm add -D typescript` |

### Residual ESLint Packages (Only When Gap Plugins Needed)

| Package | When | Purpose |
|---------|------|---------|
| `eslint` | Gap plugins detected | ESLint engine |
| `eslint-plugin-oxlint` | Always with residual ESLint | Disables rules oxlint covers |
| `eslint-plugin-vue` | Vue projects | Template linting |
| `eslint-plugin-astro` | Astro projects | .astro file support |
| `eslint-plugin-better-tailwindcss` | Tailwind v4 | Class validation + sorting |
| `eslint-plugin-playwright` | Playwright E2E | Test rules |
| `eslint-plugin-obsidianmd` | Obsidian plugins | Plugin-specific rules |
| `eslint-plugin-compat` | Frontend + browserslist | Browser compat checking |

## Installation

### Bare Minimum (All TypeScript Projects) — 3 packages
```bash
pnpm add -D oxlint @biomejs/biome typescript
```

### React / Next.js — 3 packages (no extra deps!)
```bash
pnpm add -D oxlint @biomejs/biome typescript
# React, Next.js, jsx-a11y plugins are built into oxlint
# Just add "react", "jsx-a11y", "nextjs" to oxlint.json plugins
```

### Vue — 5 packages (residual ESLint for templates)
```bash
pnpm add -D oxlint @biomejs/biome typescript
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-vue
```

### With Tailwind — 5 packages (residual ESLint for class rules)
```bash
pnpm add -D oxlint @biomejs/biome typescript
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-better-tailwindcss
```

## Oxlint Configuration

### oxlint.json

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/nicolo-ribaudo/oxlint-config-schema/refs/heads/main/schema.json",
  "plugins": [
    "import",
    "promise"
    // Add based on project type:
    // React: "react", "jsx-a11y"
    // React + perf: "react", "jsx-a11y", "react-perf"
    // Next.js: "react", "jsx-a11y", "nextjs"
    // Node.js: "node"
    // Vitest: "vitest"
    // Jest: "jest"
    // JSDoc: "jsdoc"
  ],
  "categories": {
    "correctness": "error",
    "suspicious": "warn",
    "pedantic": "off",
    "style": "warn",
    "restriction": "off",
    "nursery": "off"
  },
  "rules": {
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_", "varsIgnorePattern": "^_" }],
    "import/no-duplicates": "error",
    "import/no-cycle": "warn",
    "import/no-self-import": "error",
    "unicorn/filename-case": ["error", { "cases": { "kebabCase": true, "pascalCase": true } }],
    "unicorn/prevent-abbreviations": "off",
    "unicorn/no-null": "off"
  },
  "ignorePatterns": [
    "dist", "build", "node_modules", ".next", ".nuxt", ".output", "coverage"
  ]
}
```

### Built-in Plugin Coverage

Oxlint includes these plugins with ZERO npm dependencies:

| Plugin | Rules | Replaces |
|--------|-------|----------|
| `eslint` (core) | ~200 | ESLint core rules |
| `typescript` | ~90 | @typescript-eslint |
| `unicorn` | ~100 | eslint-plugin-unicorn |
| `oxc` (deepscan) | ~30 | eslint-plugin-sonarjs (partial) |
| `import` | ~25 | eslint-plugin-import |
| `promise` | ~15 | eslint-plugin-promise |
| `react` | ~40 | eslint-plugin-react + react-hooks |
| `react-perf` | ~6 | (new — performance rules) |
| `nextjs` | ~15 | @next/eslint-plugin-next |
| `jsx-a11y` | ~30 | eslint-plugin-jsx-a11y |
| `node` | ~20 | eslint-plugin-n |
| `vitest` | ~15 | eslint-plugin-vitest |
| `jest` | ~25 | eslint-plugin-jest |
| `jsdoc` | ~20 | (optional — JSDoc validation) |

### Framework-Specific Plugin Configuration

#### React
```jsonc
{
  "plugins": ["import", "promise", "react", "jsx-a11y"]
}
```

#### React + Performance Monitoring
```jsonc
{
  "plugins": ["import", "promise", "react", "jsx-a11y", "react-perf"]
}
```

#### Next.js
```jsonc
{
  "plugins": ["import", "promise", "react", "jsx-a11y", "nextjs"]
}
```

#### Node.js Backend
```jsonc
{
  "plugins": ["import", "promise", "node"]
}
```

#### Vitest Testing
```jsonc
{
  "plugins": ["import", "promise", "vitest"],
  "overrides": [{
    "files": ["**/*.test.ts", "**/*.spec.ts", "**/*.test.tsx", "**/*.spec.tsx"],
    "rules": {
      "vitest/no-focused-tests": "error",
      "vitest/no-disabled-tests": "warn"
    }
  }]
}
```

#### Jest Testing
```jsonc
{
  "plugins": ["import", "promise", "jest"],
  "overrides": [{
    "files": ["**/*.test.ts", "**/*.spec.ts", "**/__tests__/**/*.ts"],
    "rules": {
      "jest/no-focused-tests": "error",
      "jest/no-disabled-tests": "warn"
    }
  }]
}
```

## Biome Configuration

### biome.json

```json
{
  "$schema": "https://biomejs.dev/schemas/2.3.15/schema.json",
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingCommas": "all",
      "semicolons": "always",
      "arrowParentheses": "asNeeded"
    }
  },
  "json": {
    "formatter": {
      "trailingCommas": "none"
    }
  },
  "linter": {
    "enabled": false
  },
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on"
      }
    }
  },
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "files": {
    "includes": [
      "**",
      "!**/dist/**", "!**/build/**", "!**/node_modules/**",
      "!**/.next/**", "!**/.nuxt/**", "!**/coverage/**",
      "!**/pnpm-lock.yaml", "!**/package-lock.json"
    ]
  }
}
```

### VCS Integration (Required for CI)

**CRITICAL:** Biome's VCS integration is **off by default**. Without the `vcs` block, Biome does NOT read `.gitignore`. This causes CI failures in Docker-based pipelines (Bitbucket Pipelines, GitHub Actions) where Biome scans `node_modules/` and build artifacts, producing hundreds of spurious formatting errors.

The `vcs` config must always be included:
```json
{
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  }
}
```

**Why it works locally but fails in CI:** Locally, Biome's built-in `node_modules` hardcoded ignore masks the issue. In CI Docker containers, file discovery context differs and the `files.includes` negation patterns become the sole defence. Negation patterns for directories are unreliable ([Biome bug #7279](https://github.com/biomejs/biome/issues/7279)), so the VCS config is essential as belt-and-suspenders.

**pnpm store caveat:** Even with VCS integration, `pnpm install` may create a `.pnpm-store/` directory in the build root when the global content-addressable store cache misses (common on first CI runs). This directory contains hundreds of JSON index files that Biome will try to format. Since `.pnpm-store/` is not in a typical `.gitignore`, add it to both `.gitignore` and `biome.json` negation patterns (`"!.pnpm-store/**"`).

### files.includes Negation Patterns

Biome v2.3.15 uses `files.includes` with `!` negation for exclusions. There is **no `files.excludes` field** (the valid keys are: `maxSize`, `ignoreUnknown`, `includes`, `experimentalScannerIgnores`).

**Rules for negation patterns:**
- Always use `/**` suffix for directories: `!**/dist/**` not `!**/dist`
- Always list `"**"` first, then negations
- Negation patterns for directories are buggy ([#7279](https://github.com/biomejs/biome/issues/7279)) — rely on VCS integration as primary defence, negation patterns as secondary

### Tailwind CSS Projects

If the project uses Tailwind CSS v4, Biome needs the CSS parser configured to handle Tailwind directives (`@theme`, `@apply`, `@custom-variant`):

```json
{
  "css": {
    "parser": {
      "cssModules": false,
      "tailwindDirectives": true
    }
  }
}
```

Without this, `biome format` will fail on CSS files containing Tailwind-specific syntax.

### Formatter Settings (Prettier Equivalents)

| Prettier | Biome | Value |
|----------|-------|-------|
| `semi: true` | `javascript.formatter.semicolons` | `"always"` |
| `singleQuote: true` | `javascript.formatter.quoteStyle` | `"single"` |
| `tabWidth: 2` | `formatter.indentWidth` | `2` |
| `trailingComma: "all"` | `javascript.formatter.trailingCommas` | `"all"` |
| `printWidth: 100` | `formatter.lineWidth` | `100` |
| `arrowParens: "avoid"` | `javascript.formatter.arrowParentheses` | `"asNeeded"` |
| `endOfLine: "lf"` | `formatter.lineEnding` | `"lf"` |

### Import Sorting

Biome handles import sorting via `assist.actions.source.organizeImports` (Biome 2.x). This replaces:
- `eslint-plugin-import` order rules
- `@trivago/prettier-plugin-sort-imports`
- `@ianvs/prettier-plugin-sort-imports`

Import correctness rules (no-duplicates, no-cycle, no-self-import) remain in oxlint.

## Package.json Scripts

### Standard (no residual ESLint needed)
```json
{
  "scripts": {
    "lint": "oxlint --max-warnings=0",
    "lint:fix": "oxlint --fix --max-warnings=0",
    "format": "biome format --write .",
    "format:check": "biome format .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

### With Residual ESLint
```json
{
  "scripts": {
    "lint": "oxlint --max-warnings=0 && eslint . --max-warnings=0",
    "lint:fix": "oxlint --fix --max-warnings=0 && eslint . --fix --max-warnings=0",
    "format": "biome format --write .",
    "format:check": "biome format .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

## VSCode Integration

### .vscode/settings.json
```jsonc
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "editor.codeActionsOnSave": {
    "source.fixAll.oxc": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Recommended Extensions
- **Biome**: `biomejs.biome` — Formatter + import sorting
- **Oxlint**: `nicolo-ribaudo.oxlint-vscode` — Linter integration

## Key Rules Reference

### Oxlint TypeScript Rules (via typescript plugin)

| Rule | Purpose |
|------|---------|
| `no-explicit-any` | Disallow `any` type |
| `no-unsafe-assignment` | Disallow assigning `any` |
| `no-unsafe-call` | Disallow calling `any` |
| `no-unsafe-member-access` | Disallow accessing `any` properties |
| `no-unsafe-return` | Disallow returning `any` |
| `no-floating-promises` | Require handling promises |
| `no-misused-promises` | Prevent promise misuse |
| `consistent-type-imports` | Enforce type-only imports |

### Oxlint Import Rules

| Rule | Purpose |
|------|---------|
| `import/no-duplicates` | Prevent duplicate imports |
| `import/no-cycle` | Detect circular dependencies |
| `import/no-self-import` | Prevent self-imports |

### Oxlint Unicorn Rules

| Rule | Purpose |
|------|---------|
| `prefer-modern-dom-apis` | Use modern DOM methods |
| `no-array-reduce` | Prefer explicit loops |
| `prefer-top-level-await` | Use top-level await |

## Migration from ESLint + Prettier

### Step 1: Install New Tools
```bash
pnpm add -D oxlint @biomejs/biome
```

### Step 2: Create Configs
Copy `oxlint.json` and `biome.json` templates to project root.

### Step 3: Update package.json Scripts
Replace ESLint/Prettier commands with oxlint/biome commands (see above).

### Step 4: Update lint-staged
```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["oxlint --fix --max-warnings=0", "biome format --write"],
    "*.{json,md}": ["biome format --write"]
  }
}
```

### Step 5: Remove Old Dependencies
```bash
pnpm remove eslint prettier \
  @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  @stylistic/eslint-plugin eslint-plugin-import eslint-plugin-unicorn \
  eslint-plugin-sonarjs eslint-plugin-promise eslint-config-prettier \
  eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y \
  @next/eslint-plugin-next eslint-plugin-n eslint-plugin-vitest \
  eslint-plugin-jest eslint-plugin-compat eslint-plugin-html
```

### Step 6: Delete Old Config Files
```bash
rm eslint.config.mjs .prettierrc .prettierignore
```

### Step 7: Update VSCode Settings
Replace Prettier formatter with Biome. Add oxlint extension.

### Step 8: Verify
```bash
pnpm lint      # Should use oxlint
pnpm format    # Should use biome
pnpm typecheck # Should use tsc
```
