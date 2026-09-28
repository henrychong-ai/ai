# Residual ESLint: Gap Plugins Only

Add ESLint only for rules Oxlint does not have. `eslint-plugin-oxlint`, as the last config block, turns off every ESLint rule Oxlint already runs, so nothing is checked twice. Template: `templates/eslint.config.mjs` (every section below, commented out).

| Plugin | Add when | Why Oxlint is not enough |
|--------|----------|--------------------------|
| `eslint-plugin-vue` | Vue | Oxlint's `vue` plugin covers `<script>`; `<template>` needs ESLint |
| `eslint-plugin-astro` | Astro | Oxlint does not parse `.astro` files |
| `eslint-plugin-better-tailwindcss` | Tailwind CSS v4 | No Tailwind rules in Oxlint; also replaces `prettier-plugin-tailwindcss` class sorting |
| `eslint-plugin-playwright` | Playwright tests | Not ported to Oxlint |
| `eslint-plugin-compat` | Browser code with a browserslist config | No browser-compat rules in Oxlint |

Not gaps any more: React Refresh (`react/only-export-components` is built into Oxlint's `react` plugin), React hooks, Next.js, jsx-a11y, Vitest and Jest.

Oxlint also has alpha support for running ESLint JS plugins directly (`jsPlugins` in `.oxlintrc.json`). It may remove the need for residual ESLint later; keep using ESLint for the plugins above until it is stable.

## Core Setup

```bash
pnpm add -D eslint eslint-plugin-oxlint typescript-eslint
```

`typescript-eslint` supplies the parser ESLint needs for `.ts`/`.tsx` files (and Vue/Astro script blocks). It depends on the TypeScript compiler API, so pin TypeScript as the `/typescript` version policy says wherever it is installed.

```javascript
import oxlint from "eslint-plugin-oxlint";
import tseslint from "typescript-eslint";

export default [
  { ignores: ["dist/", "build/", "coverage/", ".next/"] },
  { files: ["**/*.{ts,tsx,mts,cts}"], languageOptions: { parser: tseslint.parser } },

  // ... gap-plugin blocks ...

  // Must stay last
  ...oxlint.buildFromOxlintConfigFile("./.oxlintrc.json"),
];
```

Point `buildFromOxlintConfigFile` at the real Oxlint config file name.

## Vue

```bash
pnpm add -D eslint-plugin-vue
```

```javascript
import vue from "eslint-plugin-vue";

// inside the config array:
...vue.configs["flat/recommended"],
{
  files: ["**/*.vue"],
  languageOptions: {
    parserOptions: { parser: tseslint.parser, extraFileExtensions: [".vue"] },
  },
  rules: { "vue/multi-word-component-names": "off" },
},
```

Add `"vue"` to Oxlint's `plugins` too for script-level rules.

## Astro

```bash
pnpm add -D eslint-plugin-astro
```

```javascript
import astro from "eslint-plugin-astro";

...astro.configs["flat/recommended"],
```

For type-aware parsing inside `.astro` files, set `languageOptions.parserOptions.project: true` on the `**/*.astro` block, and scope `projectService: true` to `**/*.{ts,tsx}` only.

## Tailwind CSS v4

```bash
pnpm add -D eslint-plugin-better-tailwindcss
```

```javascript
import betterTailwindcss from "eslint-plugin-better-tailwindcss";

{
  files: ["src/**/*.{ts,tsx}"],
  ...betterTailwindcss.configs.recommended,
  settings: {
    // the CSS file that contains @import "tailwindcss"
    "better-tailwindcss": { entryPoint: "src/styles/globals.css" },
  },
  rules: {
    ...betterTailwindcss.configs.recommended.rules,
    // Biome owns line layout; this rule would fight the formatter
    "better-tailwindcss/enforce-consistent-line-wrapping": "off",
  },
},
```

`configs.recommended` is a single config object (plugins + rules), so spread it into one block rather than into the array. Other configs: `stylistic`, `correctness`, each with `-error`/`-warn` variants.

| Rule | Purpose |
|------|---------|
| `enforce-consistent-class-order` | Sorts classes (replaces `prettier-plugin-tailwindcss`) |
| `no-duplicate-classes` | Duplicate classes |
| `no-conflicting-classes` | Classes that override each other |
| `no-unknown-classes` | Classes Tailwind does not generate |
| `no-deprecated-classes`, `enforce-canonical-classes` | v4 class names |

Use `eslint-plugin-better-tailwindcss`; the older `eslint-plugin-tailwindcss` needs Tailwind v3's JS config. Detect Tailwind v4 by `tailwindcss` ^4 in dependencies or `@import "tailwindcss"` in CSS. Also set Biome's `css.parser.tailwindDirectives: true`.

## Playwright

```bash
pnpm add -D eslint-plugin-playwright
```

```javascript
import playwright from "eslint-plugin-playwright";

{
  files: ["e2e/**/*.ts", "**/*.e2e.ts"],
  ...playwright.configs["flat/recommended"],
},
```

## Browser Compatibility

```bash
pnpm add -D eslint-plugin-compat
```

```javascript
import compat from "eslint-plugin-compat";

compat.configs["flat/recommended"],
```

Needs a browserslist config, for example in package.json: `"browserslist": ["defaults", "not op_mini all"]`.

## Scripts and Hooks

- `lint`: `oxlint --max-warnings=0 && eslint . --max-warnings=0`
- lint-staged: add `"eslint --fix --max-warnings=0"` after the Oxlint command for the globs the gap plugins cover.
- VS Code: `"eslint.validate": ["vue", "astro"]` for template languages.
