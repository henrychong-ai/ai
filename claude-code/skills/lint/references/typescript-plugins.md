# TypeScript ESLint Plugins

Additional plugins for Astro, Obsidian, and Solidity projects.

## Astro

### Installation
```bash
pnpm add -D eslint-plugin-astro astro-eslint-parser @typescript-eslint/parser
```

### ESLint Config
```javascript
// eslint.config.mjs
import { defineConfig } from "eslint/config";
import core from "ultracite/eslint/core";
import astro from "eslint-plugin-astro";

export default defineConfig([
  { extends: [core] },
  ...astro.configs.recommended,
  {
    files: ["**/*.astro"],
    languageOptions: {
      parser: astro.parser,
      parserOptions: {
        parser: "@typescript-eslint/parser",
        extraFileExtensions: [".astro"],
      },
    },
  },
]);
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
import { defineConfig } from "eslint/config";
import core from "ultracite/eslint/core";
import obsidianmd from "eslint-plugin-obsidianmd";

export default defineConfig([
  { extends: [core] },
  ...obsidianmd.configs.recommended,
]);
```

### Key Rules

| Rule | Purpose |
|------|---------|
| `no-sample-code` | Disallow sample snippets from plugin template |
| `no-direct-dom-style` | Use CSS classes instead of inline styles |
| `no-type-cast-file-folder` | Use `instanceof` for TFile/TFolder checks |
| `no-view-reference` | Don't store view references (memory leaks) |
| `prefer-file-manager-trash` | Use FileManager.trashFile() over Vault.delete() |

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

When combining multiple plugins with Ultracite:

```javascript
// eslint.config.mjs - Multi-ecosystem project
import { defineConfig } from "eslint/config";
import core from "ultracite/eslint/core";
import react from "ultracite/eslint/react";
import astro from "eslint-plugin-astro";
import obsidianmd from "eslint-plugin-obsidianmd";

export default defineConfig([
  // Base Ultracite config
  { extends: [core, react] },

  // Astro files
  ...astro.configs.recommended,
  {
    files: ["**/*.astro"],
    languageOptions: {
      parser: astro.parser,
    },
  },

  // Obsidian plugin (if applicable)
  ...obsidianmd.configs.recommended,

  // Global ignores
  {
    ignores: [
      "dist/",
      "node_modules/",
      "artifacts/",
      "cache/",
    ],
  },
]);
```

**Note:** Solidity files are NOT linted by ESLint. Run Solhint as a separate command.
