# TypeScript/JavaScript: Oxlint + Biome

Oxlint lints, Biome formats and sorts imports (its linter stays off), `tsc --noEmit` type-checks. Residual ESLint is added only for gap plugins (`typescript-residual-eslint.md`).

Tool versions and upgrade policy (Node, TypeScript, pnpm, lint tools) are owned by `/typescript` → `references/tech-stack/version-policy.md`. Check live versions before pinning: `npm view oxlint version`, `npm view @biomejs/biome version`.

## Packages

| Package | Purpose |
|---------|---------|
| `oxlint` | Linter (Rust, built-in plugins, no plugin packages to install) |
| `@biomejs/biome` | Formatter + import sorting |
| `typescript` | Type checker (pin per `/typescript` version policy) |

```bash
pnpm add -D oxlint @biomejs/biome
```

## Oxlint

### Config file: `.oxlintrc.json`

Oxlint auto-discovers only `.oxlintrc.json`, `.oxlintrc.jsonc`, `oxlint.config.ts` and `oxlint.config.mts`. Use `templates/.oxlintrc.json`. A repo that keeps a file named `oxlint.json` must pass `-c oxlint.json` in every script, lint-staged entry and CI step; without it Oxlint silently runs its defaults and ignores the file.

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["typescript", "unicorn", "oxc", "import", "promise"],
  "categories": {
    "correctness": "error",
    "suspicious": "warn",
    "pedantic": "off",
    "style": "off",
    "restriction": "off",
    "nursery": "off"
  },
  "rules": {
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_", "varsIgnorePattern": "^_" }],
    "import/no-duplicates": "error",
    "import/no-cycle": "warn",
    "import/no-self-import": "error",
    "import/no-unassigned-import": ["warn", { "allow": ["**/*.css"] }],
    "typescript/consistent-type-imports": "error",
    "typescript/no-explicit-any": "error",
    "unicorn/filename-case": ["error", { "cases": { "kebabCase": true, "pascalCase": true } }],
    "unicorn/no-null": "off"
  },
  "ignorePatterns": [
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    ".output",
    ".wrangler",
    "*.config.js",
    "*.config.mjs"
  ],
  "overrides": [
    {
      "files": ["**/tests/setup.*", "**/test/setup.*", "**/*.setup.*", "**/setupTests.*"],
      "rules": {
        "import/no-unassigned-import": "off"
      }
    }
  ]
}
```

Key points:
- **`plugins` replaces the default set.** List every plugin you want, including `typescript`, `unicorn` and `oxc`; any plugin left out is switched off and its rules are silently skipped.
- **`style` is off.** With `--max-warnings=0`, the style category flags most real code (identifier length, export grouping, function style). Enable individual style rules you want under `rules` instead.
- **Keep the file comment-free JSON** (or name it `.oxlintrc.jsonc`) so Biome can format it. The template is already in Biome's layout, so `biome check .` passes on a fresh copy; keep it that way after editing (`biome check --write .oxlintrc.json`).
- **Unknown rule names fail the whole config** ("Rule '…' not found"). After an Oxlint upgrade, run `oxlint` once and remove any rule it reports.
- **CSS side-effect imports are allowed** (`import "./index.css"` in a Vite entry) through the rule's `allow: ["**/*.css"]` option; other side-effect imports still warn.
- **Test-setup files are exempt from `import/no-unassigned-import`.** Setup files exist for side-effect imports (`import "@testing-library/jest-dom/vitest"`), which the rule warns on and `--max-warnings=0` turns into a failure. The override covers `tests/setup.*`, `test/setup.*`, `*.setup.*` (incl. `vitest.setup.ts`) and `setupTests.*`; add your setup path if it differs.
- `$schema` points at the schema shipped in the installed package, so it always matches the version in use.

### Plugins by project type

Oxlint 1.85 ships 870 rules across 15 plugin scopes; `oxlint --rules` lists what the installed version has.

| Project | Add to `plugins` |
|---------|------------------|
| Every TS/JS project | `typescript`, `unicorn`, `oxc`, `import`, `promise` |
| React | `react`, `jsx-a11y` (+ `react-perf` if wanted) |
| Next.js | `react`, `jsx-a11y`, `nextjs` |
| Vue | `vue` (script-level rules; templates still need residual ESLint) |
| Node.js backend | `node` |
| Vitest / Jest | `vitest` / `jest` |
| JSDoc-heavy code | `jsdoc` |

`react` includes the hooks rules and `react/only-export-components` (the React Refresh / Vite HMR rule), so Vite + React needs no ESLint.

Test-file overrides:

```json
{
  "overrides": [
    {
      "files": ["**/*.test.ts", "**/*.spec.ts", "**/*.test.tsx", "**/*.spec.tsx"],
      "rules": { "vitest/no-focused-tests": "error", "vitest/no-disabled-tests": "warn" }
    }
  ]
}
```

### Type-aware rules (opt-in; needs `oxlint-tsgolint` and a TS 7-ready tsconfig)

Rules that need type information (`typescript/no-floating-promises`, `no-misused-promises`, `no-unsafe-assignment`, `no-unsafe-call`, `no-unsafe-member-access`, `no-unsafe-return`, `unbound-method` and others; `oxlint --rules -f json` marks them `type_aware`) run only when all of these hold:

- `oxlint --type-aware` or `"options": { "typeAware": true }` in `.oxlintrc.json`
- the `oxlint-tsgolint` package installed
- a tsconfig that is TypeScript 7-ready: no `baseUrl` and none of the other options TS 7 removed; tsgolint rejects the file otherwise (`Option 'baseUrl' has been removed`)

Upstream documents TypeScript 7.0+ as required (tsgolint is built on the native compiler). On 2026-09-28 it also ran on a TypeScript 6 project (`typescript@6.0.3`, oxlint 1.86.0, `oxlint-tsgolint` 7.0.2003): with a `baseUrl`-free tsconfig it reported `no-floating-promises` correctly. Treat the rules as **opt-in**; `tsc --noEmit` remains the type-safety gate either way.

### Rules worth knowing

| Rule | Plugin | Purpose |
|------|--------|---------|
| `no-explicit-any` | typescript | Disallow `any` |
| `consistent-type-imports` | typescript | Enforce `import type` |
| `no-duplicates`, `no-cycle`, `no-self-import` | import | Import correctness (Biome handles order) |
| `filename-case` | unicorn | File naming |
| `rules-of-hooks`, `exhaustive-deps` | react | Hooks correctness |

## Biome

### `biome.json`

Use `templates/biome.json`. For new repos it keeps Biome's own JavaScript defaults: double quotes and `arrowParentheses: "always"`. Existing repos keep their configured style; changing it reformats every file.

```json
{
  "$schema": "https://biomejs.dev/schemas/2.5.14/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": {
    "includes": ["**", "!**/dist", "!**/build", "!**/coverage", "!**/.next", "!**/.pnpm-store"]
  },
  "formatter": { "enabled": true, "indentStyle": "space", "indentWidth": 2, "lineWidth": 100, "lineEnding": "lf" },
  "javascript": {
    "formatter": { "quoteStyle": "double", "trailingCommas": "all", "semicolons": "always", "arrowParentheses": "always" }
  },
  "linter": { "enabled": false },
  "assist": { "actions": { "source": { "organizeImports": "on" } } }
}
```

- **`$schema` must match the installed Biome version.** After every Biome upgrade run `pnpm exec biome migrate --write`; it updates `$schema` and any renamed options.
- **Turn on VCS integration.** It is off by default; without it Biome ignores `.gitignore` and, in CI containers, formats build output and dependency folders.
- **Exclusions** are `!` negations inside `files.includes` (Biome 2 has no `files.ignore`/`excludes`). Also add `.pnpm-store/` to `.gitignore`: a cold pnpm cache can create it in the build root.
- **Tailwind v4 CSS** (`@theme`, `@apply`, `@custom-variant`): add `"css": { "parser": { "tailwindDirectives": true } }`.
- **`biome check` vs `biome format`:** `biome format` only formats. `biome check` (with the linter off) formats and applies the organise-imports assist, so scripts and hooks use `check`.

### Language support (Biome 2.5)

| Language | Format | Notes |
|----------|--------|-------|
| JS / TS / JSX / TSX | Yes | |
| JSON / JSONC | Yes | `.vscode/*.json` and `tsconfig*.json` are read as JSONC |
| CSS | Yes | SCSS/Less not supported |
| GraphQL, GritQL | Yes | |
| HTML | Experimental, opt-in | Leave out of hooks and format-on-save |
| Vue / Svelte / Astro | Experimental | Leave out of hooks |
| Markdown, YAML | Not yet (in progress) | Leave out of hooks |

Source: <https://biomejs.dev/internals/language-support/>. A file type Biome does not handle, passed explicitly, fails with "No files were processed"; keep lint-staged globs to supported types, or add `--no-errors-on-unmatched`.

### Prettier → Biome option names

| Prettier | Biome |
|----------|-------|
| `printWidth` | `formatter.lineWidth` |
| `tabWidth` / `useTabs` | `formatter.indentWidth` / `formatter.indentStyle` |
| `semi` | `javascript.formatter.semicolons` (`always` / `asNeeded`) |
| `singleQuote` | `javascript.formatter.quoteStyle` |
| `trailingComma` | `javascript.formatter.trailingCommas` (`all` / `es5` / `none`) |
| `arrowParens` (`always` / `avoid`) | `javascript.formatter.arrowParentheses` (`always` / `asNeeded`) |
| `endOfLine` | `formatter.lineEnding` |

## package.json scripts

```json
{
  "scripts": {
    "lint": "oxlint --max-warnings=0",
    "lint:fix": "oxlint --fix --max-warnings=0",
    "format": "biome check --write .",
    "format:check": "biome check .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

With residual ESLint, append `&& eslint . --max-warnings=0` to `lint` and `&& eslint . --fix --max-warnings=0` to `lint:fix`.

## Editor (VS Code)

`templates/.vscode/settings.json` (Biome format-on-save, Oxlint fix-on-save) and `templates/.vscode/extensions.json`: `biomejs.biome` and `oxc.oxc-vscode`.

## Monorepos

- One `.oxlintrc.json` and one `biome.json` at the workspace root. Oxlint also picks up nested `.oxlintrc.json` files for per-package rules; Biome supports nested `biome.json` with `"root": false`.
- Root scripts run once over the tree (`oxlint`, `biome check .`); `tsc` runs per package (`pnpm -r typecheck`).

## CSS without Tailwind (optional)

Biome formats CSS but does not lint it with this setup. Where a project needs CSS/SCSS linting, add Stylelint (`stylelint`, `stylelint-config-standard`, `stylelint-config-standard-scss`) with a `.stylelintrc.json`. It is not part of the default stack. Tailwind projects use the better-tailwindcss ESLint plugin instead.
