# TypeScript/JavaScript Linting with ESLint + Plugins

Full manual ESLint configuration with strictTypeChecked and recommended plugins.

## Package Overview

### Core Packages (Always Required)

| Package | Version | Purpose |
|---------|---------|---------|
| `eslint` | ^9.x | Linter engine (flat config) |
| `prettier` | ^3.x | Code formatter |
| `typescript` | ^5.x | TypeScript compiler |
| `@typescript-eslint/eslint-plugin` | ^8.x | TypeScript lint rules |
| `@typescript-eslint/parser` | ^8.x | TypeScript parser |
| `eslint-config-prettier` | ^9.x | Disables conflicting rules |

### Recommended Plugins

| Package | Purpose | Rule Count |
|---------|---------|------------|
| `@stylistic/eslint-plugin` | Code style (spacing, braces) | ~100 |
| `eslint-plugin-import` | Import/export validation | ~40 |
| `eslint-plugin-unicorn` | Modern JS best practices | ~100 |
| `eslint-plugin-sonarjs` | Bug detection patterns | ~30 |
| `eslint-plugin-promise` | Async/Promise patterns | ~15 |
| `eslint-plugin-compat` | Browser compatibility checking | ~1 |
| `eslint-plugin-html` | Lint scripts in HTML files | ~0 (processor) |

### Framework-Specific Plugins

| Package | When to Use |
|---------|-------------|
| `eslint-plugin-react` | React projects |
| `eslint-plugin-react-hooks` | React projects |
| `eslint-plugin-jsx-a11y` | React/JSX accessibility |
| `@next/eslint-plugin-next` | Next.js projects (in addition to React plugins) |
| `eslint-plugin-vue` | Vue projects |
| `eslint-plugin-n` | Node.js backends |
| `eslint-plugin-vitest` | Vitest unit/integration testing |
| `eslint-plugin-playwright` | Playwright E2E testing |

## Installation

### Base Install (All TypeScript Projects)
```bash
pnpm add -D \
  eslint \
  prettier \
  typescript \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser \
  @stylistic/eslint-plugin \
  eslint-plugin-import \
  eslint-plugin-unicorn \
  eslint-plugin-sonarjs \
  eslint-plugin-promise \
  eslint-plugin-compat \
  eslint-plugin-html \
  eslint-config-prettier
```

### Add for React
```bash
pnpm add -D \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y
```

### Add for Next.js
```bash
pnpm add -D \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y \
  @next/eslint-plugin-next
```

### Add for Vue
```bash
pnpm add -D eslint-plugin-vue
```

### Add for Node.js
```bash
pnpm add -D eslint-plugin-n
```

### Add for Vitest Testing
```bash
pnpm add -D eslint-plugin-vitest
```

### Add for Playwright E2E Testing
```bash
pnpm add -D eslint-plugin-playwright
```

## ESLint Configuration (Flat Config)

### Base Config (eslint.config.mjs)

```javascript
// eslint.config.mjs
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import stylistic from '@stylistic/eslint-plugin';
import importPlugin from 'eslint-plugin-import';
import unicorn from 'eslint-plugin-unicorn';
import sonarjs from 'eslint-plugin-sonarjs';
import promise from 'eslint-plugin-promise';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // Ignores
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
      'import/no-unresolved': 'off', // TypeScript handles this
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

  // Custom rule overrides
  {
    rules: {
      // TypeScript overrides
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      }],
      '@typescript-eslint/consistent-type-imports': ['error', {
        prefer: 'type-imports',
        fixStyle: 'separate-type-imports',
      }],
      '@typescript-eslint/consistent-type-exports': 'error',

      // Stylistic overrides
      '@stylistic/semi': ['error', 'always'],
      '@stylistic/quotes': ['error', 'single', { avoidEscape: true }],
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
      '@stylistic/max-len': ['error', { code: 100, ignoreUrls: true, ignoreStrings: true }],
    },
  },

  // Prettier must be last
  prettier,
);
```

### With React/Next.js

```javascript
// eslint.config.mjs (React/Next.js)
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import stylistic from '@stylistic/eslint-plugin';
import importPlugin from 'eslint-plugin-import';
import unicorn from 'eslint-plugin-unicorn';
import sonarjs from 'eslint-plugin-sonarjs';
import promise from 'eslint-plugin-promise';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // ... (same ignores and base config as above)

  // React
  {
    plugins: {
      react,
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      'react/prop-types': 'off', // TypeScript handles this
    },
  },

  // ... (rest of config)
  prettier,
);
```

### With Next.js

```javascript
// eslint.config.mjs (Next.js)
// Add to React config:
import nextPlugin from '@next/eslint-plugin-next';

// In the config array (after React plugins):
{
  plugins: {
    '@next/next': nextPlugin,
  },
  rules: {
    ...nextPlugin.configs.recommended.rules,
    ...nextPlugin.configs['core-web-vitals'].rules,
  },
},
```

### With Vue

```javascript
// eslint.config.mjs (Vue)
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import vue from 'eslint-plugin-vue';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // Ignores
  {
    ignores: ['dist/', 'node_modules/'],
  },

  // Base ESLint recommended
  eslint.configs.recommended,

  // TypeScript strict + stylistic
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  // Vue recommended (flat config)
  ...vue.configs['flat/recommended'],

  // Parser options
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
        extraFileExtensions: ['.vue'],
      },
    },
  },

  // Vue-specific settings
  {
    files: ['*.vue', '**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },

  // Custom Vue rules
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'warn',
    },
  },

  // Prettier must be last
  prettier,
);
```

### With Node.js

```javascript
// Add to config for Node.js projects
import n from 'eslint-plugin-n';

// In the config array:
{
  plugins: {
    n,
  },
  rules: {
    ...n.configs.recommended.rules,
    'n/no-missing-import': 'off', // TypeScript handles this
    'n/no-unpublished-import': 'off',
  },
},
```

### With Vitest

```javascript
// Add to config for Vitest projects
import vitest from 'eslint-plugin-vitest';

// In the config array (apply only to test files):
{
  files: ['**/*.test.ts', '**/*.spec.ts', '**/*.test.tsx', '**/*.spec.tsx'],
  plugins: {
    vitest,
  },
  rules: {
    ...vitest.configs.recommended.rules,
    'vitest/no-focused-tests': 'error',
    'vitest/no-disabled-tests': 'warn',
  },
},
```

### With Playwright (E2E Testing)

```javascript
// Add to config for Playwright E2E projects
import playwright from 'eslint-plugin-playwright';

// In the config array (apply only to E2E test files):
{
  files: ['**/e2e/**/*.ts', '**/*.e2e.ts', '**/tests/**/*.spec.ts'],
  plugins: {
    playwright,
  },
  rules: {
    ...playwright.configs['flat/recommended'].rules,
    'playwright/no-focused-test': 'error',
    'playwright/no-skipped-test': 'warn',
  },
},
```

## Prettier Configuration

### .prettierrc
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### .prettierignore
```
dist/
build/
node_modules/
.next/
coverage/
pnpm-lock.yaml
```

## TypeScript Configuration

### tsconfig.json (Strict)
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "alwaysStrict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*", "eslint.config.mjs"],
  "exclude": ["node_modules", "dist"]
}
```

## Package.json Scripts

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings=0",
    "lint:fix": "eslint . --fix --max-warnings=0",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

## Key Rules Explained

### TypeScript Rules (strictTypeChecked)

| Rule | Purpose |
|------|---------|
| `no-explicit-any` | Disallow `any` type |
| `no-unsafe-assignment` | Disallow assigning `any` |
| `no-unsafe-call` | Disallow calling `any` |
| `no-unsafe-member-access` | Disallow accessing `any` properties |
| `no-unsafe-return` | Disallow returning `any` |
| `strict-boolean-expressions` | Require explicit boolean comparisons |
| `no-floating-promises` | Require handling promises |
| `no-misused-promises` | Prevent promise misuse |

### Import Rules

| Rule | Purpose |
|------|---------|
| `import/order` | Enforce consistent import order |
| `import/no-duplicates` | Prevent duplicate imports |
| `import/no-cycle` | Detect circular dependencies |

### Unicorn Rules

| Rule | Purpose |
|------|---------|
| `prefer-modern-dom-apis` | Use modern DOM methods |
| `no-array-reduce` | Prefer explicit loops |
| `prefer-top-level-await` | Use top-level await |

### SonarJS Rules

| Rule | Purpose |
|------|---------|
| `no-duplicate-string` | Detect repeated strings |
| `cognitive-complexity` | Limit function complexity |
| `no-identical-functions` | Detect duplicate functions |

## VSCode Integration

### .vscode/settings.json
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

## Migration Notes

### From Ultracite
If migrating from Ultracite:
1. Remove `ultracite` package
2. Install individual plugins (see Installation section)
3. Replace `eslint.config.mjs` with manual config
4. Verify same rules are enabled

### From ESLint 8 (.eslintrc)
1. Rename `.eslintrc.json` to `eslint.config.mjs`
2. Convert to flat config format (see examples above)
3. Update `extends` to direct imports
4. Update `plugins` to object format
