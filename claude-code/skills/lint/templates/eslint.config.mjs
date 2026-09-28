// ESLint flat config: RESIDUAL ONLY
// Oxlint does the primary linting. Keep ESLint only for gap plugins Oxlint does
// not cover: Vue <template>, .astro files, Tailwind classes, Playwright, browser
// compatibility. Uncomment the sections the project needs and delete the rest.
//
// eslint-plugin-oxlint (last block) turns off every ESLint rule Oxlint already runs.

import oxlint from "eslint-plugin-oxlint";
import tseslint from "typescript-eslint";

// Vue (template linting; Oxlint handles <script>):
// import vue from "eslint-plugin-vue";

// Astro (.astro files):
// import astro from "eslint-plugin-astro";

// Tailwind CSS v4 (class order + validation; replaces prettier-plugin-tailwindcss):
// import betterTailwindcss from "eslint-plugin-better-tailwindcss";

// Playwright E2E tests:
// import playwright from "eslint-plugin-playwright";

// Browser compatibility (needs a browserslist config):
// import compat from "eslint-plugin-compat";

export default [
  {
    ignores: ["dist/", "build/", "coverage/", ".next/", ".astro/", ".wrangler/"],
  },

  // TypeScript parser so ESLint can read .ts/.tsx files
  {
    files: ["**/*.{ts,tsx,mts,cts}"],
    languageOptions: { parser: tseslint.parser },
  },

  // ---------------------------------------------------------------------------
  // Vue
  // ---------------------------------------------------------------------------
  // ...vue.configs["flat/recommended"],
  // {
  //   files: ["**/*.vue"],
  //   languageOptions: {
  //     parserOptions: { parser: tseslint.parser, extraFileExtensions: [".vue"] },
  //   },
  //   rules: { "vue/multi-word-component-names": "off" },
  // },

  // ---------------------------------------------------------------------------
  // Astro
  // ---------------------------------------------------------------------------
  // ...astro.configs["flat/recommended"],

  // ---------------------------------------------------------------------------
  // Tailwind CSS v4: point entryPoint at the CSS file that imports tailwindcss
  // ---------------------------------------------------------------------------
  // {
  //   files: ["src/**/*.{ts,tsx}"],
  //   ...betterTailwindcss.configs.recommended,
  //   settings: {
  //     "better-tailwindcss": { entryPoint: "src/styles/globals.css" },
  //   },
  //   rules: {
  //     ...betterTailwindcss.configs.recommended.rules,
  //     // Biome owns line layout; this rule would fight the formatter
  //     "better-tailwindcss/enforce-consistent-line-wrapping": "off",
  //   },
  // },

  // ---------------------------------------------------------------------------
  // Playwright
  // ---------------------------------------------------------------------------
  // {
  //   files: ["e2e/**/*.ts", "**/*.e2e.ts"],
  //   ...playwright.configs["flat/recommended"],
  // },

  // ---------------------------------------------------------------------------
  // Browser compatibility
  // ---------------------------------------------------------------------------
  // compat.configs["flat/recommended"],

  // Must stay last: disables ESLint rules that Oxlint covers
  ...oxlint.buildFromOxlintConfigFile("./.oxlintrc.json"),
];
