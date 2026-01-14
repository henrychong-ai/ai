// ESLint Flat Config - TypeScript Strict + Recommended Plugins
// Copy to project root and adjust as needed

import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import stylistic from '@stylistic/eslint-plugin';
import importPlugin from 'eslint-plugin-import';
import unicorn from 'eslint-plugin-unicorn';
import sonarjs from 'eslint-plugin-sonarjs';
import promise from 'eslint-plugin-promise';
import prettier from 'eslint-config-prettier';

// =============================================================================
// CONDITIONAL IMPORTS - Uncomment based on your project type
// =============================================================================

// Frontend projects (has browserslist or React/Vue/Next.js):
// import compat from 'eslint-plugin-compat';

// Projects with HTML files containing inline scripts:
// import html from 'eslint-plugin-html';

// React projects:
// import react from 'eslint-plugin-react';
// import reactHooks from 'eslint-plugin-react-hooks';
// import jsxA11y from 'eslint-plugin-jsx-a11y';

// Next.js projects (add to React imports above):
// import nextPlugin from '@next/eslint-plugin-next';

// Vue projects:
// import vue from 'eslint-plugin-vue';

// Node.js backend projects (Express, Fastify, Hono, Koa):
// import n from 'eslint-plugin-n';

// Vitest unit testing:
// import vitest from 'eslint-plugin-vitest';

// Playwright E2E testing:
// import playwright from 'eslint-plugin-playwright';

export default tseslint.config(
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
      '*.config.js',
      '*.config.mjs',
    ],
  },

  // =============================================================================
  // CORE PLUGINS (Always enabled)
  // =============================================================================

  // Base ESLint recommended
  eslint.configs.recommended,

  // TypeScript strict + stylistic
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  // Parser options for type-aware linting
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // Stylistic plugin
  stylistic.configs['recommended-flat'],

  // Import plugin
  {
    plugins: {
      import: importPlugin,
    },
    rules: {
      'import/order': ['error', {
        'groups': ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'always',
        'alphabetize': { order: 'asc', caseInsensitive: true },
      }],
      'import/no-duplicates': 'error',
      'import/no-cycle': 'error',
      'import/no-unresolved': 'off',
    },
  },

  // Unicorn plugin
  {
    plugins: {
      unicorn,
    },
    rules: {
      ...unicorn.configs.recommended.rules,
      'unicorn/filename-case': ['error', {
        cases: { kebabCase: true, pascalCase: true },
      }],
      'unicorn/prevent-abbreviations': 'off',
      'unicorn/no-null': 'off',
    },
  },

  // SonarJS plugin
  {
    plugins: {
      sonarjs,
    },
    rules: {
      ...sonarjs.configs.recommended.rules,
    },
  },

  // Promise plugin
  {
    plugins: {
      promise,
    },
    rules: {
      ...promise.configs.recommended.rules,
    },
  },

  // =============================================================================
  // CONDITIONAL PLUGINS - Uncomment based on your project type
  // =============================================================================

  // -----------------------------------------------------------------------------
  // Frontend: Browser Compatibility (if browserslist in package.json)
  // -----------------------------------------------------------------------------
  // {
  //   plugins: {
  //     compat,
  //   },
  //   rules: {
  //     'compat/compat': 'warn',
  //   },
  // },

  // -----------------------------------------------------------------------------
  // Frontend: HTML files with inline scripts
  // -----------------------------------------------------------------------------
  // {
  //   plugins: {
  //     html,
  //   },
  // },

  // -----------------------------------------------------------------------------
  // React
  // -----------------------------------------------------------------------------
  // {
  //   plugins: {
  //     react,
  //     'react-hooks': reactHooks,
  //     'jsx-a11y': jsxA11y,
  //   },
  //   settings: {
  //     react: { version: 'detect' },
  //   },
  //   rules: {
  //     ...react.configs.recommended.rules,
  //     ...react.configs['jsx-runtime'].rules,
  //     ...reactHooks.configs.recommended.rules,
  //     ...jsxA11y.configs.recommended.rules,
  //     'react/prop-types': 'off',
  //   },
  // },

  // -----------------------------------------------------------------------------
  // Next.js (add after React config)
  // -----------------------------------------------------------------------------
  // {
  //   plugins: {
  //     '@next/next': nextPlugin,
  //   },
  //   rules: {
  //     ...nextPlugin.configs.recommended.rules,
  //     ...nextPlugin.configs['core-web-vitals'].rules,
  //   },
  // },

  // -----------------------------------------------------------------------------
  // Vue
  // -----------------------------------------------------------------------------
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

  // -----------------------------------------------------------------------------
  // Node.js Backend (Express, Fastify, Hono, Koa)
  // -----------------------------------------------------------------------------
  // {
  //   plugins: { n },
  //   rules: {
  //     ...n.configs.recommended.rules,
  //     'n/no-missing-import': 'off',
  //     'n/no-unpublished-import': 'off',
  //   },
  // },

  // -----------------------------------------------------------------------------
  // Vitest (unit/integration testing)
  // -----------------------------------------------------------------------------
  // {
  //   files: ['**/*.test.ts', '**/*.spec.ts', '**/*.test.tsx', '**/*.spec.tsx'],
  //   plugins: {
  //     vitest,
  //   },
  //   rules: {
  //     ...vitest.configs.recommended.rules,
  //     'vitest/no-focused-tests': 'error',
  //     'vitest/no-disabled-tests': 'warn',
  //   },
  // },

  // -----------------------------------------------------------------------------
  // Playwright (E2E testing)
  // -----------------------------------------------------------------------------
  // {
  //   files: ['**/e2e/**/*.ts', '**/*.e2e.ts', '**/tests/**/*.spec.ts'],
  //   plugins: {
  //     playwright,
  //   },
  //   rules: {
  //     ...playwright.configs['flat/recommended'].rules,
  //     'playwright/no-focused-test': 'error',
  //     'playwright/no-skipped-test': 'warn',
  //   },
  // },

  // =============================================================================
  // CUSTOM RULE OVERRIDES
  // =============================================================================
  {
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
      '@typescript-eslint/consistent-type-imports': ['error', {
        prefer: 'type-imports',
        fixStyle: 'separate-type-imports',
      }],
      '@typescript-eslint/consistent-type-exports': 'error',
      '@stylistic/semi': ['error', 'always'],
      '@stylistic/quotes': ['error', 'single', { avoidEscape: true }],
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
      '@stylistic/max-len': ['error', { code: 100, ignoreUrls: true, ignoreStrings: true }],
    },
  },

  // =============================================================================
  // PRETTIER (must be last)
  // =============================================================================
  prettier,
);
