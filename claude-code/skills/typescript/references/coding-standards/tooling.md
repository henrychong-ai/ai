# TypeScript Development Tooling

TypeScript compiler configuration and editor integration.

**For linting setup:** Use the `/lint` skill which is the single source of truth for ESLint flat config with 7 core plugins + framework-specific plugins, Prettier, Husky/lint-staged, and CI/CD pipelines.

**Note:** The Ironclad Stack uses **ESLint + Prettier**, not Biome. See `typescript-ironclad-stack.md` for rationale.

---

## Tool Stack Overview

| Tool | Purpose | Managed By |
|------|---------|------------|
| **TypeScript** | Compiler & type checking | This skill |
| **ESLint 9** | Linting (find problems) | `/lint` skill |
| **Prettier** | Formatting (code style) | `/lint` skill |
| **Husky + lint-staged** | Pre-commit hooks | `/lint` skill |

---

## TypeScript Configuration

### Strict tsconfig.json (Ironclad Stack Standard)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",

    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "noUncheckedIndexedAccess": true,

    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,

    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    "esModuleInterop": true,
    "isolatedModules": true,
    "skipLibCheck": true
  }
}
```

### Critical Strictness Options

| Option | Effect |
|--------|--------|
| `noUncheckedIndexedAccess` | Array access returns `T \| undefined` |
| `useUnknownInCatchVariables` | `catch(e)` is `unknown`, not `any` |
| `noImplicitOverride` | Requires `override` keyword in subclasses |
| `strictNullChecks` | No implicit null/undefined |

### Path Aliases

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### Project-Specific Variations

| Project Type | Module | Target | Notes |
|--------------|--------|--------|-------|
| **Node.js backend** | NodeNext | ES2022 | Standard |
| **Vite frontend** | ESNext | ESNext | Vite handles bundling |
| **Next.js** | ESNext | ES2022 | Next.js manages config |
| **Cloudflare Workers** | ESNext | ESNext | Edge runtime |
| **Library (npm)** | NodeNext | ES2022 | For broad compatibility |

---

## Package Scripts

### Standard Script Set

```json
{
  "scripts": {
    "dev": "tsup --watch",
    "build": "tsup",
    "lint": "eslint . --max-warnings=0",
    "lint:fix": "eslint . --fix --max-warnings=0",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

### CI-Friendly Scripts

```json
{
  "scripts": {
    "ci:lint": "eslint . --max-warnings=0",
    "ci:format": "prettier --check .",
    "ci:typecheck": "tsc --noEmit",
    "ci:test": "vitest run --coverage",
    "ci": "pnpm ci:lint && pnpm ci:format && pnpm ci:typecheck && pnpm ci:test"
  }
}
```

---

## Editor Integration

### VS Code Settings (TypeScript)

```json
// .vscode/settings.json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "typescript.updateImportsOnFileMove.enabled": "always",

  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  }
}
```

### Recommended Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

---

## Cross-References

| Topic | Location |
|-------|----------|
| **ESLint flat config** | `/lint` skill → `references/typescript-eslint.md` |
| **Framework plugins** | `/lint` skill → React, Next.js, Vue, Vitest, Playwright |
| **Pre-commit hooks** | `/lint` skill → Husky + lint-staged section |
| **CI/CD pipelines** | `/lint` skill → `templates/` directory |
| **Ironclad Stack** | This skill → `tech-stack/typescript-ironclad-stack.md` |
| **Type patterns** | This skill → `type-patterns.md` |

---

*See also: type-patterns.md for advanced TypeScript patterns*
*For comprehensive linting setup: invoke `/lint` skill*
*Last updated: 2026-01-14*
