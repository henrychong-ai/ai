// ESLint Flat Config - RESIDUAL ONLY
// Only needed when gap plugins are required (Vue templates, Astro, Tailwind,
// Playwright, Obsidian, Compat). Oxlint handles all primary linting.
//
// IMPORTANT: eslint-plugin-oxlint disables all rules that oxlint already covers,
// preventing duplicate checking.

import oxlint from 'eslint-plugin-oxlint';

// =============================================================================
// CONDITIONAL IMPORTS - Uncomment based on your project type
// =============================================================================

// Vue projects (template linting - oxlint only handles <script>):
// import vue from 'eslint-plugin-vue';
// import tseslint from 'typescript-eslint';

// Astro projects (.astro file support - oxlint can't parse):
// import astro from 'eslint-plugin-astro';
// import tseslint from 'typescript-eslint';

// Tailwind CSS v4 (class validation + sorting):
// import betterTailwindcss from 'eslint-plugin-better-tailwindcss';

// Playwright E2E testing (not yet ported to oxlint):
// import playwright from 'eslint-plugin-playwright';

// Obsidian plugin development (too niche for oxlint):
// import obsidianmd from 'eslint-plugin-obsidianmd';

// Browser compatibility checking (oxlint doesn't have):
// import compat from 'eslint-plugin-compat';

export default [
  // =============================================================================
  // IGNORES
  // =============================================================================
  {
    ignores: [
      'dist/',
      'build/',
      'node_modules/',
      '.next/',
      'coverage/',
    ],
  },

  // =============================================================================
  // CONDITIONAL PLUGINS - Uncomment based on your project type
  // =============================================================================

  // ---------------------------------------------------------------------------
  // Vue (template linting)
  // ---------------------------------------------------------------------------
  // ...vue.configs['flat/recommended'],
  // {
  //   files: ['*.vue', '**/*.vue'],
  //   languageOptions: {
  //     parserOptions: {
  //       parser: tseslint.parser,
  //       extraFileExtensions: ['.vue'],
  //     },
  //   },
  // },
  // {
  //   rules: {
  //     'vue/multi-word-component-names': 'off',
  //     'vue/no-v-html': 'warn',
  //   },
  // },

  // ---------------------------------------------------------------------------
  // Astro
  // ---------------------------------------------------------------------------
  // ...astro.configs.recommended,
  // {
  //   files: ['**/*.astro'],
  //   languageOptions: {
  //     parser: astro.parser,
  //     parserOptions: {
  //       parser: tseslint.parser,
  //       extraFileExtensions: ['.astro'],
  //       project: true,
  //       tsconfigRootDir: import.meta.dirname,
  //     },
  //   },
  // },

  // ---------------------------------------------------------------------------
  // Tailwind CSS v4 (class validation + sorting)
  // NOTE: sort-classes replaces prettier-plugin-tailwindcss
  // ---------------------------------------------------------------------------
  // ...betterTailwindcss.configs['flat/recommended'],

  // ---------------------------------------------------------------------------
  // Playwright E2E testing
  // ---------------------------------------------------------------------------
  // {
  //   files: ['**/e2e/**/*.ts', '**/*.e2e.ts', '**/tests/**/*.spec.ts'],
  //   plugins: { playwright },
  //   rules: {
  //     ...playwright.configs['flat/recommended'].rules,
  //     'playwright/no-focused-test': 'error',
  //     'playwright/no-skipped-test': 'warn',
  //   },
  // },

  // ---------------------------------------------------------------------------
  // Obsidian Plugin Development
  // ---------------------------------------------------------------------------
  // ...obsidianmd.configs.recommended,

  // ---------------------------------------------------------------------------
  // Browser Compatibility
  // ---------------------------------------------------------------------------
  // {
  //   plugins: { compat },
  //   rules: { 'compat/compat': 'warn' },
  // },

  // =============================================================================
  // OXLINT COMPAT (must be last - disables rules oxlint already covers)
  // =============================================================================
  ...oxlint.buildFromOxlintConfigFile('./oxlint.json'),
];
