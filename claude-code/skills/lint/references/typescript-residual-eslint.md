# Residual ESLint — Gap Plugins

Plugins that require ESLint because oxlint doesn't cover them yet. Use `eslint-plugin-oxlint` to disable all rules that oxlint already handles.

**When is residual ESLint needed?**

| Plugin | Trigger | Why Not Oxlint |
|--------|---------|----------------|
| `eslint-plugin-vue` | Vue detected | Oxlint: `<script>` only, no `<template>` linting |
| `eslint-plugin-astro` | Astro detected | Oxlint: no `.astro` file support |
| `eslint-plugin-better-tailwindcss` | Tailwind v4 detected | Oxlint: no Tailwind rules |
| `eslint-plugin-react-refresh` | Vite + React detected | Oxlint: no react-refresh/HMR rules |
| `eslint-plugin-playwright` | Playwright detected | Oxlint: not ported yet |
| `eslint-plugin-obsidianmd` | Obsidian detected | Oxlint: too niche |
| `eslint-plugin-compat` | Frontend + browserslist | Oxlint: no browser compat rules |

## Core Setup (Always Required with Residual ESLint)

```bash
pnpm add -D eslint eslint-plugin-oxlint
```

`eslint-plugin-oxlint` automatically disables all ESLint rules that oxlint already covers, preventing duplicate checking.

### TypeScript Parser Requirement

**CRITICAL:** ESLint cannot parse `.ts`/`.tsx` files natively. Any residual ESLint config that lints TypeScript files **must** include `typescript-eslint` for its parser:

```bash
pnpm add -D typescript-eslint
```

```javascript
import tseslint from 'typescript-eslint';

// In any config block with files: ['**/*.{ts,tsx}']
languageOptions: { parser: tseslint.parser },
```

Vue and Astro configs already include `typescript-eslint` for their own parser needs. For other gap plugins (react-refresh, playwright, tailwind, compat, obsidian), add it explicitly when the plugin lints `.ts`/`.tsx` files.

### Base eslint.config.mjs

```javascript
import tseslint from 'typescript-eslint';
import oxlint from 'eslint-plugin-oxlint';

export default [
  { ignores: ['dist/', 'build/', 'node_modules/', '.next/', 'coverage/'] },

  // TypeScript parser (required for .ts/.tsx files)
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { parser: tseslint.parser },
  },

  // ... gap plugin configs go here ...

  // MUST be last — disables rules oxlint covers
  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

---

## React Refresh (Vite + React)

Oxlint covers `react-hooks` natively, but `eslint-plugin-react-refresh` (Vite HMR support) is not in Oxlint. Only needed for Vite + React projects (not Next.js, which has its own HMR).

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-react-refresh typescript-eslint
```

### ESLint Config
```javascript
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import oxlint from 'eslint-plugin-oxlint';

export default [
  { ignores: ['dist'] },

  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { parser: tseslint.parser },
    plugins: { 'react-refresh': reactRefresh },
    rules: {
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },

  // Relax for generated component libraries (e.g., shadcn/ui)
  {
    files: ['src/components/ui/**/*.{ts,tsx}'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

### Detection
- `vite.config.*` present AND `react` in dependencies
- `@vitejs/plugin-react` in devDependencies
- NOT needed for Next.js (uses its own HMR)

---

## Vue

Oxlint handles `<script>` blocks in `.vue` files but cannot lint `<template>` directives and components. Use `eslint-plugin-vue` for template linting.

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-vue typescript-eslint
```

### ESLint Config
```javascript
import oxlint from 'eslint-plugin-oxlint';
import vue from 'eslint-plugin-vue';
import tseslint from 'typescript-eslint';

export default [
  { ignores: ['dist/', 'node_modules/'] },

  ...vue.configs['flat/recommended'],

  {
    files: ['*.vue', '**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
        extraFileExtensions: ['.vue'],
      },
    },
  },

  {
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'warn',
    },
  },

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

---

## Astro

Oxlint cannot parse `.astro` files. Use `eslint-plugin-astro` for full Astro support.

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-astro typescript-eslint
```

### ESLint Config
```javascript
import oxlint from 'eslint-plugin-oxlint';
import astro from 'eslint-plugin-astro';
import tseslint from 'typescript-eslint';

export default [
  { ignores: ['dist/', 'node_modules/', '.astro/', '.wrangler/'] },

  ...astro.configs.recommended,

  {
    files: ['**/*.astro'],
    languageOptions: {
      parser: astro.parser,
      parserOptions: {
        parser: tseslint.parser,
        extraFileExtensions: ['.astro'],
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

### Browserslist Config (package.json)
Required for `eslint-plugin-compat` if also used:
```json
{
  "browserslist": ["defaults", "not op_mini all"]
}
```

---

## Tailwind CSS v4

Since Prettier is removed, `prettier-plugin-tailwindcss` cannot be used for class sorting. Instead, use `eslint-plugin-better-tailwindcss` with the `sort-classes` rule enabled.

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-better-tailwindcss
```

### ESLint Config
```javascript
import oxlint from 'eslint-plugin-oxlint';
import betterTailwindcss from 'eslint-plugin-better-tailwindcss';

export default [
  { ignores: ['dist/', 'node_modules/'] },

  // Tailwind CSS v4 — includes sort-classes (replaces prettier-plugin-tailwindcss)
  ...betterTailwindcss.configs['flat/recommended'],

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

### Available Configs

| Config | Includes | Use When |
|--------|----------|----------|
| `recommended` | Stylistic + correctness rules | Default (most projects) |
| `stylistic` | Class sorting, multiline only | Want sorting without validation |
| `correctness` | Invalid classes, duplicates only | Want validation without sorting |

### Key Rules

| Rule | Purpose |
|------|---------|
| `sort-classes` | Automatic class sorting (replaces Prettier plugin) |
| `no-duplicate-classes` | Detect duplicate classes |
| `no-conflicting-classes` | Detect contradicting classes |
| `no-custom-classname` | Warn on non-Tailwind classes |
| `multiline` | Multi-line class formatting |

### Detection
Tailwind v4 projects:
- `tailwindcss` ^4.x in dependencies
- CSS files with `@import "tailwindcss"` or `@theme` directives
- Absence of `tailwind.config.js` (v4 doesn't use it)

---

## Playwright E2E Testing

Oxlint hasn't ported Playwright rules yet. Use `eslint-plugin-playwright` for E2E test linting.

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-playwright
```

### ESLint Config
```javascript
import oxlint from 'eslint-plugin-oxlint';
import playwright from 'eslint-plugin-playwright';

export default [
  { ignores: ['dist/', 'node_modules/'] },

  {
    files: ['**/e2e/**/*.ts', '**/*.e2e.ts', '**/tests/**/*.spec.ts'],
    plugins: { playwright },
    rules: {
      ...playwright.configs['flat/recommended'].rules,
      'playwright/no-focused-test': 'error',
      'playwright/no-skipped-test': 'warn',
    },
  },

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

---

## Obsidian Plugin Development

Too niche for oxlint to include. Use `eslint-plugin-obsidianmd` for Obsidian-specific rules.

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-obsidianmd
```

### ESLint Config
```javascript
import oxlint from 'eslint-plugin-oxlint';
import obsidianmd from 'eslint-plugin-obsidianmd';

export default [
  { ignores: ['dist/', 'node_modules/', 'main.js'] },

  ...obsidianmd.configs.recommended,

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

### Key Rules

| Rule | Purpose |
|------|---------|
| `no-sample-code` | Disallow sample snippets from template |
| `no-direct-dom-style` | Use CSS classes instead of inline |
| `no-type-cast-file-folder` | Use `instanceof` for TFile/TFolder |
| `no-view-reference` | Don't store view references (memory leaks) |
| `prefer-file-manager-trash` | Use FileManager.trashFile() |

### Detection
- `manifest.json` with `id`, `name`, `version`, `minAppVersion` fields
- `obsidian` in dependencies or devDependencies

---

## Browser Compatibility

Oxlint doesn't have browser compatibility rules. Use `eslint-plugin-compat` for frontend projects with `browserslist`.

### Installation
```bash
pnpm add -D eslint eslint-plugin-oxlint eslint-plugin-compat
```

### ESLint Config
```javascript
import oxlint from 'eslint-plugin-oxlint';
import compat from 'eslint-plugin-compat';

export default [
  { ignores: ['dist/', 'node_modules/'] },

  {
    plugins: { compat },
    rules: { 'compat/compat': 'warn' },
  },

  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

### Browserslist (package.json)
```json
{
  "browserslist": ["defaults", "not op_mini all"]
}
```

---

## Combining Multiple Gap Plugins

When a project needs several gap plugins:

```javascript
import oxlint from 'eslint-plugin-oxlint';
import vue from 'eslint-plugin-vue';
import betterTailwindcss from 'eslint-plugin-better-tailwindcss';
import compat from 'eslint-plugin-compat';
import tseslint from 'typescript-eslint';

export default [
  { ignores: ['dist/', 'node_modules/'] },

  // Vue templates
  ...vue.configs['flat/recommended'],
  {
    files: ['*.vue', '**/*.vue'],
    languageOptions: {
      parserOptions: { parser: tseslint.parser, extraFileExtensions: ['.vue'] },
    },
  },

  // Tailwind class validation + sorting
  ...betterTailwindcss.configs['flat/recommended'],

  // Browser compatibility
  { plugins: { compat }, rules: { 'compat/compat': 'warn' } },

  // Oxlint compat (must be last)
  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
```

---

## Solidity Note

Solidity uses **Solhint** (dedicated linter) and **forge fmt** (Foundry formatter) — completely separate from ESLint and Biome. See SKILL.md Solidity section for details.

For Hardhat projects without Foundry, use `prettier` with `prettier-plugin-solidity` as formatter fallback.
