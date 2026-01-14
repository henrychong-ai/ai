# TypeScript ESLint Plugins

Additional plugins for Astro, Obsidian, and Solidity projects.

**Note:** All configs use manual ESLint flat config (no Ultracite or other bundled presets).

## Astro

### Installation
```bash
pnpm add -D eslint-plugin-astro astro-eslint-parser @typescript-eslint/parser
```

### ESLint Config
```javascript
// eslint.config.mjs
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import astro from 'eslint-plugin-astro';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // Ignores
  {
    ignores: ['dist/', 'node_modules/', '.astro/'],
  },

  // Base ESLint + TypeScript
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  // Parser options
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // Astro plugin
  ...astro.configs.recommended,
  {
    files: ['**/*.astro'],
    languageOptions: {
      parser: astro.parser,
      parserOptions: {
        parser: tseslint.parser,
        extraFileExtensions: ['.astro'],
      },
    },
  },

  // Prettier must be last
  prettier,
);
```

### VSCode Settings
```json
{
  "eslint.validate": [
    "javascript",
    "typescript",
    "astro"
  ]
}
```

### Linted Elements
- Frontmatter (script section)
- HTML templates
- JSX-like expressions
- Client-side scripts (`<script>` tags)
- Directives

---

## Obsidian Plugin Development

### Installation
```bash
pnpm add -D eslint-plugin-obsidianmd
```

### ESLint Config
```javascript
// eslint.config.mjs
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import obsidianmd from 'eslint-plugin-obsidianmd';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // Ignores
  {
    ignores: ['dist/', 'node_modules/', 'main.js'],
  },

  // Base ESLint + TypeScript
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  // Parser options
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // Obsidian plugin
  ...obsidianmd.configs.recommended,

  // Prettier must be last
  prettier,
);
```

### Key Rules

| Rule | Purpose |
|------|---------|
| `no-sample-code` | Disallow sample snippets from plugin template |
| `no-direct-dom-style` | Use CSS classes instead of inline styles |
| `no-type-cast-file-folder` | Use `instanceof` for TFile/TFolder checks |
| `no-view-reference` | Don't store view references (memory leaks) |
| `prefer-file-manager-trash` | Use FileManager.trashFile() over Vault.delete() |

### Detection
Obsidian plugins can be detected by:
- `manifest.json` with `id`, `name`, `version`, `minAppVersion` fields
- `obsidian` in dependencies or devDependencies

### Starting from Template
The [obsidian-sample-plugin](https://github.com/obsidianmd/obsidian-sample-plugin) template includes ESLint pre-configured:
```bash
# Already configured in template
npm run lint
```

---

## Solidity (Solhint)

**Note:** Solidity uses Solhint, a dedicated linter separate from ESLint.

### Installation
```bash
pnpm add -D solhint prettier prettier-plugin-solidity
```

### Solhint Config (.solhint.json)
```json
{
  "extends": "solhint:recommended",
  "plugins": [],
  "rules": {
    "compiler-version": ["error", "^0.8.0"],
    "func-visibility": ["warn", { "ignoreConstructors": true }],
    "no-empty-blocks": "warn",
    "reason-string": ["warn", { "maxLength": 64 }],
    "max-line-length": ["warn", 120],
    "no-unused-vars": "error",
    "no-console": "warn",
    "avoid-suicide": "error",
    "avoid-sha3": "warn"
  }
}
```

### Prettier Config for Solidity
```json
// .prettierrc
{
  "plugins": ["prettier-plugin-solidity"],
  "overrides": [
    {
      "files": "*.sol",
      "options": {
        "printWidth": 100,
        "tabWidth": 4,
        "useTabs": false,
        "singleQuote": false,
        "bracketSpacing": true
      }
    }
  ]
}
```

### Package.json Scripts
```json
{
  "scripts": {
    "lint:sol": "solhint 'contracts/**/*.sol'",
    "lint:sol:fix": "solhint 'contracts/**/*.sol' --fix",
    "format:sol": "prettier --write 'contracts/**/*.sol'",
    "lint": "eslint . && npm run lint:sol",
    "format": "prettier --write . && npm run format:sol"
  }
}
```

### Ignore File (.solhintignore)
```
node_modules/
artifacts/
cache/
coverage/
typechain-types/
```

### Combined Project Setup (Hardhat/Foundry)

For projects with both TypeScript and Solidity:

```json
// lint-staged in package.json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.sol": ["solhint --fix", "prettier --write"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

---

## Integration Pattern

When combining multiple framework plugins in a single project:

```javascript
// eslint.config.mjs - Multi-ecosystem project
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import stylistic from '@stylistic/eslint-plugin';
import importPlugin from 'eslint-plugin-import';
import unicorn from 'eslint-plugin-unicorn';
import sonarjs from 'eslint-plugin-sonarjs';
import promise from 'eslint-plugin-promise';
import astro from 'eslint-plugin-astro';
import obsidianmd from 'eslint-plugin-obsidianmd';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // Ignores
  {
    ignores: ['dist/', 'node_modules/', 'artifacts/', 'cache/'],
  },

  // Base ESLint + TypeScript strict
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  // Parser options
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // Core plugins
  stylistic.configs['recommended-flat'],
  {
    plugins: { import: importPlugin, unicorn, sonarjs, promise },
    rules: {
      ...unicorn.configs.recommended.rules,
      ...sonarjs.configs.recommended.rules,
      ...promise.configs.recommended.rules,
      'import/order': ['error', { 'newlines-between': 'always' }],
    },
  },

  // Astro files (if applicable)
  ...astro.configs.recommended,
  {
    files: ['**/*.astro'],
    languageOptions: {
      parser: astro.parser,
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },

  // Obsidian plugin (if applicable)
  ...obsidianmd.configs.recommended,

  // Prettier must be last
  prettier,
);
```

**Note:** Solidity files are NOT linted by ESLint. Run Solhint as a separate command.
