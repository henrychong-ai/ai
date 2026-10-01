# TypeScript Tooling — tsconfig Standard, Scripts, Editor

This file owns the **tsconfig standard**. Lint and format configuration (Oxlint + Biome, residual ESLint for gap plugins) and git hooks belong to `/lint`; versions to `../tech-stack/version-policy.md`.

## Tool stack

| Tool | Purpose | Owner |
|------|---------|-------|
| TypeScript (`typescript@~6.0`) | Type checking, declaration emit | This skill |
| Oxlint | Linting (primary) | `/lint` → `references/typescript-oxlint-biome.md` |
| Biome | Formatting (linter disabled), import sorting | `/lint` → `references/typescript-oxlint-biome.md` |
| Residual ESLint | Only for gap plugins (Vue templates, Astro, Tailwind class sorting, Playwright) | `/lint` → `references/typescript-residual-eslint.md` |
| husky + lint-staged + gitleaks | Pre-commit hooks | `/lint` → `references/git-hooks.md` |
| Migrating from ESLint + Prettier | — | `/lint` → `references/migration-eslint-prettier-to-oxlint-biome.md` |

## tsconfig standard

Every tsconfig is written to be **TypeScript 7-ready**: no `baseUrl`, no `moduleResolution: "node"`/`"node10"`/`"classic"`, `esModuleInterop` never `false`, no `downlevelIteration`, no ES5 target. TS 7 turns each of these into a hard error.

### Base (all projects)

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    // Strictness
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,
    "useUnknownInCatchVariables": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,

    // Modules
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,

    // Language level for Node 24 (TypeScript wiki Node target mapping; Node 22 → ES2023,
    // Node 26 → ES2025). Mapping and target changes: /typescript references/version-upgrade/ecmascript/es-upgrade-checklist.md
    "target": "ES2024",
    "lib": ["ES2024"],

    // Path alias: relative `paths`, no `baseUrl`
    "paths": { "@/*": ["./src/*"] }
  }
}
```

Then pick **one runtime block**:

| Runtime | `module` / `moduleResolution` | Add | Emits? |
|---------|-------------------------------|-----|--------|
| **Node service, CLI, library** (run with tsx, emit with `tsc`) | `"NodeNext"` / `"NodeNext"` | `"types": ["node"]`, `"rootDir": "src"`, `"outDir": "dist"`, `"declaration": true`, `"declarationMap": true`, `"sourceMap": true` | Yes |
| **Vite SPA / React** | `"ESNext"` / `"bundler"` | `"lib": ["ES2024", "DOM", "DOM.Iterable"]` (keep it at or below the browsers you support), `"jsx": "react-jsx"`, `"noEmit": true` | No (Vite builds) |
| **Cloudflare Workers** | `"ESNext"` / `"bundler"` | `"types": ["./worker-configuration.d.ts"]` (from `wrangler types`), `"noEmit": true` | No (Wrangler builds) |
| **Next.js** | `"ESNext"` / `"bundler"` | Keep the keys Next.js manages (`plugins`, `jsx`, `incremental`); add the strictness block | No |

Notes:

- **`verbatimModuleSyntax`** requires `import type` for type-only imports (see `style-guide.md`). Under `NodeNext`, relative imports carry the `.js` extension of the emitted file (`import { x } from './x.js'`).
- **`exactOptionalPropertyTypes`** and **`noPropertyAccessFromIndexSignature`** are the two flags most likely to need work in an existing codebase. Adopt them in new projects; in existing ones enable them when the error count is manageable.
- **`noUnusedLocals`/`noUnusedParameters`** stay off: Oxlint reports unused code without blocking the type check.
- **TypeScript 6 defaults**: `types` defaults to `[]`, so list every global types package the runtime needs (`node`, `vite/client`, `vitest/globals` when tests rely on `globals: true`); and an emitting build needs an explicit `rootDir` (`tsc` stops with TS5011 otherwise).
- **`process.env`** is an index signature, so `noPropertyAccessFromIndexSignature` rejects `process.env.FOO`. Parse the environment once with Zod (`../tech-stack/typescript-ironclad-stack.md` → "Environment and Configuration") and read the typed result; use `process.env['FOO']` only where that is impractical.
- Workspaces: put the base in `tsconfig.base.json` at the root and `extends` it from each package.

## Package scripts

```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc -p tsconfig.build.json",
    "typecheck": "tsc --noEmit",
    "lint": "oxlint --max-warnings=0",
    "lint:fix": "oxlint --fix --max-warnings=0",
    "format": "biome check --write .",
    "format:check": "biome check .",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck && pnpm test"
  }
}
```

Adjust `dev`/`build` to the runtime (Vite, Wrangler, Next). The exact Oxlint flags (for example `-c` when the config file is not auto-discovered) and the Biome setup come from `/lint`; `biome check` (linter off) formats and organises imports, where `biome format` only formats. `check` mirrors CI: green locally means green in CI.

Optional extra gate on large codebases (TS 7 native compiler, type-check only; see `version-policy.md`):

```bash
pnpm dlx --package=typescript@^7.0 tsc --noEmit -p tsconfig.json
```

## Editor integration (VS Code)

```jsonc
// .vscode/settings.json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.preferences.importModuleSpecifier": "non-relative",
  "typescript.updateImportsOnFileMove.enabled": "always",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "biomejs.biome",
  "editor.codeActionsOnSave": {
    "source.organizeImports.biome": "explicit",
    "source.fixAll.oxc": "explicit"
  }
}
```

```jsonc
// .vscode/extensions.json
{
  "recommendations": ["biomejs.biome", "oxc.oxc-vscode"]
}
```

`typescript.tsdk` makes the editor use the project's pinned TypeScript rather than the editor's bundled version.

## Cross-references

| Topic | Location |
|-------|----------|
| Oxlint + Biome configuration | `/lint` → `references/typescript-oxlint-biome.md` |
| Residual ESLint gap plugins | `/lint` → `references/typescript-residual-eslint.md` |
| Pre-commit hooks | `/lint` → `references/git-hooks.md` |
| Versions | `../tech-stack/version-policy.md` |
| Type patterns | `type-patterns.md` |
