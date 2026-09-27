# The Ironclad Stack: Universal TypeScript for Claude Code

A single, production-ready TypeScript stack optimized for AI-assisted development. Designed for end-to-end type safety, maximum Claude Code proficiency, and universal compatibility across all project types.

**Core Principle:** *One source of truth, one type chain, one set of tools.*

---

## Design Principles

### 1. Claude Code Optimization
Every technology choice prioritizes Claude's training data coverage. We use tools with the most documentation, examples, and community adoption to minimize hallucinations and maximize accurate code generation.

### 2. End-to-End Strict Type Safety
Types flow from database to browser without gaps. TypeScript strict mode + Zod runtime validation + drizzle-zod schema generation create unbroken type chains that catch errors at compile time, not runtime.

### 3. Universal Compatibility
The same core stack works for all project types: web apps, APIs, CLI tools, Obsidian plugins, MCP servers, and npm packages. Framework choices vary; everything else stays consistent.

### 4. Multi-Developer + Multi-CC Stability
Pre-commit hooks enforce standards automatically. Strict TypeScript catches errors before code review. Consistent tooling means any developer or CC instance can work on any project.

---

## The Universal Core Stack

| Layer                | Technology               | Why                                        |
| -------------------- | ------------------------ | ------------------------------------------ |
| **Language**         | TypeScript (Strict)      | Type safety + maximum CC training data     |
| **Runtime**          | Node.js LTS              | Universal compatibility, battle-tested     |
| **Package Manager**  | pnpm                     | Fastest, strictest, best monorepo support  |
| **Path Aliases**     | @/* → src/*              | Clean imports, refactor-safe               |
| **Environment**      | Zod + dotenv             | Type-safe config, fail-fast validation     |
| **Validation**       | Zod                      | Runtime validation + type inference        |
| **ORM**              | Drizzle + drizzle-zod    | TypeScript-native, no DSL translation      |
| **API (internal)**   | tRPC                     | Zero boundary, types flow end-to-end       |
| **API (external)**   | Hono + @hono/zod-openapi | When external consumers needed             |
| **Build (backend)**  | tsup                     | Fast, DTS generation, sensible defaults    |
| **Build (frontend)** | Vite                     | HMR, ESM-native, fast                      |
| **Testing**          | Vitest + Playwright      | Jest-compatible, fast, full ecosystem      |
| **Linting**          | Oxlint (primary) + residual ESLint (gap plugins) | 50-100x faster, 668 built-in rules, zero npm deps for most projects |
| **Formatting**       | Biome (linter disabled)  | 25x faster than Prettier, handles JS/TS/CSS/JSON/MD |
| **Pre-commit**       | Husky + lint-staged      | Enforce standards automatically            |
| **Styling**          | Tailwind CSS + shadcn/ui | Utility-first, copy-paste components       |

> **Back-end / back-to-front default:** for a Worker/API that owns the contract with a dashboard and/or MCP consuming its types, use the **Option-B single-source pattern** (`@hono/zod-openapi`: ONE `createRoute()` → request+response validation + generated OpenAPI doc + dashboard client types + MCP tool schemas). Canonical definition: "The Option-B Back-to-Front Pattern (Recommended Default)" below.

---

## Node.js Version Policy

### Version Requirements

**Always use the latest patch release within the target major version.** Minimum floors below are CVE-driven.

| Context | Target Major | CVE Minimum Floor | Rationale |
|---------|-------------|-------------------|-----------|
| **New projects** | Node 24 | 24.13.0+ | Latest Active LTS; floor due to CVE-2025-59466 |
| **Minimum supported** | Node 22 | 22.22.0+ | Security baseline; floor due to CVE-2025-59466 |

### Current LTS Schedule

| Version | Status | CVE Minimum Floor | End of Life |
|---------|--------|------------------------|-------------|
| 24.x | Active LTS | **24.13.0** | April 2028 |
| 22.x | Active LTS | **22.22.0** | April 2027 |
| 20.x | Maintenance LTS | 20.20.0 | April 2026 |
| 18.x | End of Life | — | Expired |

### Security Baseline: January 2026 Patches

**Critical:** Versions below 24.13.0 / 22.22.0 are vulnerable to CVE-2025-59466 (async_hooks DoS).

When `async_hooks` is enabled (by Next.js, React Server Components, or APM tools), stack overflow causes immediate process crash that cannot be caught by try/catch. Attackers can trigger this with deeply nested JSON payloads.

- **CVE-2025-59466**: async_hooks stack overflow DoS (Medium)
- **Patched**: January 13, 2026
- **Reference**: [Node.js Security Release](https://nodejs.org/en/blog/vulnerability/december-2025-security-releases)

See `references/patterns/security-patterns.md` for defensive coding patterns.

### Why Node 22.22.0 Minimum (Not Node 20)

1. **Security baseline**: January 2026 security patches are mandatory. Node 22.22.0+ includes all critical fixes.

2. **Support window**: Node 20 enters EOL in ~3 months (April 2026). Node 22 has 15+ months remaining.

3. **Future-proofing**: New code should not target soon-to-expire runtimes. Projects started today will likely run for years.

4. **Feature parity**: Both 22 and 24 have all required features (native fetch, stable ESM, modern V8). No reason to support 20.

5. **Enterprise standard**: Enterprise projects need predictable support windows. Node 22.22.0+ provides this.

### Version Pinning

**`.nvmrc` (recommended):** Use major version only — nvm resolves to latest available patch:
```
24
```

**`.node-version` (alternative):**
```
24
```

**`package.json` engines (enforcement):** Use the CVE minimum floor, not a specific patch:
```json
{
  "engines": {
    "node": ">=22.22.0"
  }
}
```

### TypeScript Type Definitions

**`@types/node` must match the Node.js major version:**

| Node.js Version | @types/node | Rationale |
|-----------------|-------------|-----------|
| Node 24.x | `^24` | ES2023+ features, latest APIs |
| Node 22.x | `^22` | ES2022+ features |
| Node 20.x | `^20` | Legacy (not recommended) |

**Why this matters:**
- `@types/node` versions are aligned with Node.js major releases
- Using mismatched versions causes TypeScript errors (e.g., `Array.at()` requires ES2022+)
- When upgrading Node.js, always update `@types/node` to match

**`package.json` devDependencies:**
```json
{
  "devDependencies": {
    "@types/node": "^24"
  }
}
```

**tsconfig.json lib alignment:**
- Node 24 + @types/node@24 → `"lib": ["ES2023"]` minimum
- Node 22 + @types/node@22 → `"lib": ["ES2022"]` minimum

---

## Framework Version Policy

### Version Requirements

**Always use the latest minor/patch within the target major version.**

| Framework | New Projects (Target Major) | Minimum Supported | Rationale |
|-----------|---------------------------|-------------------|-----------|
| **Next.js** | 16 | 15 | Active LTS / Maintenance LTS |
| **React** | 19 | 18 | Current / Security-supported |
| **Vue** | 3 | 3 | Current major |

### Current LTS Schedule

#### Next.js

| Version | Status | Support Until |
|---------|--------|---------------|
| **16.x** | **Active LTS** | ~Oct 2027 |
| **15.x** | Maintenance LTS | ~Oct 2026 |
| 14.x | EOL | Oct 26, 2025 |

**Policy:** Active LTS receives features + bug fixes. Maintenance LTS receives critical security fixes only for 2 years from initial release.

#### React

| Version | Released | Active Support | Security Support |
|---------|----------|----------------|------------------|
| **19** | Dec 5, 2024 | ✅ Yes | ✅ Yes |
| **18** | Mar 29, 2022 | ❌ Ended Dec 2024 | ✅ Yes |
| 17 | Oct 20, 2020 | ❌ Ended | ✅ Yes |

**Policy:** React has no formal LTS. All major versions receive security fixes indefinitely. Active feature development only on latest major.

#### Vue

| Version | Status |
|---------|--------|
| **3.x** | **Current (Active)** — always use latest minor/patch |
| 2.x | **EOL Dec 31, 2023** |

**Policy:** Only the latest minor version receives updates. Always use the latest 3.x release.

### Framework Version Pinning

**`package.json` (recommended):**
```json
{
  "dependencies": {
    "next": "^16",
    "react": "^19",
    "react-dom": "^19"
  }
}
```

**For Vue projects:**
```json
{
  "dependencies": {
    "vue": "^3"
  }
}
```

### Framework + Node.js Compatibility

| Framework | Minimum Node.js | Recommended Node.js |
|-----------|-----------------|---------------------|
| Next.js 16 | 18.18.0 | Node 24 (latest patch) |
| Next.js 15 | 18.18.0 | Node 22 (latest patch) |
| React 19 | 18.0.0 | Node 24 (latest patch) |
| Vue 3 | 18.0.0 | Node 24 (latest patch) |

**Note:** Always use Node 22.22.0+ or Node 24.13.0+ regardless of framework minimum to ensure security patches (CVE-2025-59466).

---

## Tool Version Policy

**Always use the latest minor/patch version within the target major version.** The tables below specify target major versions only. When installing or upgrading, use the latest available release within that major (e.g., `^5` means latest 5.x, not a specific 5.y.z). The only exception is CVE-driven minimum floors, which are called out explicitly.

### Testing Tools

| Tool | Target Major | Notes |
|------|-------------|-------|
| **Vitest** | `^4` | Current stable, Browser Mode stable |
| **@vitest/coverage-v8** | `^4` | Must match Vitest major version |
| **Playwright** | `^1` | E2E testing, auto-waiting |

**Vitest 4.x Key Changes:**
- Browser Mode now stable (was experimental in 3.x)
- Visual regression testing support
- Playwright Trace integration
- Performance improvements

**Migration from Vitest 3.x:** Generally straightforward for basic usage. Review [Vitest 4 migration guide](https://vitest.dev/blog/vitest-4) for Browser Mode users.

**⚠️ Cloudflare Workers Compatibility:**
`@cloudflare/vitest-pool-workers` only supports **Vitest 2.0.x - 3.2.x**. Vitest 4.x is NOT compatible. For Workers projects:
```json
{
  "devDependencies": {
    "vitest": "~3.2.0",
    "@cloudflare/vitest-pool-workers": "latest"
  }
}
```

**package.json (non-Workers projects):**
```json
{
  "devDependencies": {
    "vitest": "^4",
    "@vitest/coverage-v8": "^4",
    "@playwright/test": "^1"
  }
}
```

### Build Tools

| Tool | Target Major | Notes |
|------|-------------|-------|
| **TypeScript** | `^5` | Strict mode required |
| **tsup** | `^8` | Backend/CLI builds |

**package.json:**
```json
{
  "devDependencies": {
    "typescript": "^5",
    "tsup": "^8"
  }
}
```

**Note:** `typescript-eslint` (`^8`) is only needed when using residual ESLint gap plugins that lint `.ts`/`.tsx` files. See Code Quality Tools section.

### Database Tools (Drizzle Ecosystem)

| Tool | Target Version | Notes |
|------|---------------|-------|
| **drizzle-orm** | `latest` | TypeScript-native ORM (pre-1.0) |
| **drizzle-kit** | `latest` | Migrations CLI (pre-1.0) |
| **drizzle-zod** | `latest` | Schema-to-Zod bridge (pre-1.0) |

**Note:** Drizzle is still in 0.x (pre-1.0) — there is no stable major to pin. Always use the latest available version. Check release notes when upgrading.

**package.json:**
```json
{
  "dependencies": {
    "drizzle-orm": "latest"
  },
  "devDependencies": {
    "drizzle-kit": "latest",
    "drizzle-zod": "latest"
  }
}
```

### Validation & API Tools

| Tool | Target Major | Notes |
|------|-------------|-------|
| **Zod** | `^4` | Runtime validation (new projects) |
| **Zod** | `^3` | Runtime validation (existing projects, until ready to migrate) |
| **tRPC** | `^11` | Type-safe internal APIs |
| **Hono** | `^4` | HTTP framework, edge-compatible |
| **@hono/zod-openapi** | `latest` | OpenAPI generation (pre-1.0); the **Option-B back-to-front default** for APIs/services/internal tools — see canonical section below |

**Zod Version Policy:**

| Context | Version | Rationale |
|---------|---------|-----------|
| **New projects** | `^4` | 14x faster string parsing, 57% smaller bundle |
| **Existing projects** | `^3` | Stay on 3.x until ready to migrate |

**Note:** Zod has **NO LTS policy** — both 3.x and 4.x are actively maintained.

**Zod 4 Benefits:**
- 14x faster string parsing
- 57% smaller bundle size
- Improved error messages
- Better TypeScript inference

**Zod 4 Breaking Changes:**
- Error customization APIs unified under single `error` param
- String validators moved to top-level: `z.email()` instead of `z.string().email()`
- `.merge()` and `.superRefine()` deprecated

See [Zod 4 migration guide](https://zod.dev/v4/changelog) for full details.

**Zod 4 Import (incremental migration for existing projects):**
```typescript
import { z } from 'zod/v4';  // Use v4 alongside v3 during migration
```

**package.json (new projects):**
```json
{
  "dependencies": {
    "zod": "^4",
    "@trpc/server": "^11",
    "@trpc/client": "^11",
    "hono": "^4"
  }
}
```

**package.json (existing projects staying on Zod 3.x):**
```json
{
  "dependencies": {
    "zod": "^3",
    "@trpc/server": "^11",
    "@trpc/client": "^11",
    "hono": "^4"
  }
}
```

### Code Quality Tools

| Tool | Target Major | Notes |
|------|-------------|-------|
| **Oxlint** | `latest` | Primary linter, 668 built-in rules, zero npm deps |
| **Biome** | `latest` | Formatter only (linter disabled), replaces Prettier |
| **ESLint** | `^10` (new projects), `^9` minimum | Residual only — gap plugins (Vue, Astro, Tailwind, Playwright) |
| **eslint-plugin-oxlint** | `latest` | Disables ESLint rules already covered by Oxlint |
| **Husky** | `^9` | Git hooks |
| **lint-staged** | `^16` | Pre-commit staging |

**Oxlint + Biome replaces ESLint + Prettier** as the default. ESLint is only needed for gap plugins that Oxlint doesn't cover yet (Vue templates, Astro, Tailwind class sorting, Playwright, Obsidian). See `/lint` skill for full framework detection matrix.

**Core install (all projects) — 3 packages:**
```bash
pnpm add -D oxlint @biomejs/biome typescript
```

**Add residual ESLint only when gap plugins needed:**
```bash
pnpm add -D eslint eslint-plugin-oxlint  # + specific gap plugin
```

**package.json:**
```json
{
  "devDependencies": {
    "oxlint": "latest",
    "@biomejs/biome": "latest",
    "husky": "^9",
    "lint-staged": "^16"
  }
}
```

### Package Management

| Tool | Target Major | Notes |
|------|-------------|-------|
| **pnpm** | `10` | Security-first defaults, always use latest 10.x |

**Version Policy:** pnpm does NOT have an LTS policy. Always use the latest stable 10.x release.

**pnpm 10 Breaking Changes:**
- Lifecycle scripts blocked by default (security improvement)
- Nothing hoisted by default
- `pnpm link` adds to workspace root
- Requires explicit `pnpm.onlyBuiltDependencies` for native modules

**packageManager field:** Set to the latest 10.x available at time of project creation:
```bash
npm pkg set packageManager=pnpm@$(pnpm --version)
```

**For existing projects staying on pnpm 9:** Use latest 9.x:
```bash
npm pkg set packageManager=pnpm@$(pnpm --version)
```

### Styling Tools

| Tool | Target Major | Notes |
|------|-------------|-------|
| **Tailwind CSS** | `^4` | CSS-first config, 5x faster |
| **shadcn/ui** | `latest` | Copy-paste components |

**Tailwind CSS 4.x Key Changes:**
- CSS-first configuration (no `tailwind.config.js`)
- 5x faster full builds, 100x faster incremental
- Built on cascade layers, `@property`, `color-mix()`
- Requires modern browsers (Safari 16.4+, Chrome 111+, Firefox 128+)

**Migration from Tailwind 3.x:**
- Run `npx @tailwindcss/upgrade` for automated migration
- Move config from `tailwind.config.js` to CSS `@theme` directive
- Update utilities: `border` now uses `currentColor`, `ring` defaults to 1px

**package.json:**
```json
{
  "dependencies": {
    "tailwindcss": "^4"
  }
}
```

**For legacy browser support (stay on 3.x):**
```json
{
  "dependencies": {
    "tailwindcss": "^3"
  }
}
```

### Complete Version Summary

**New Project Dependencies:**

```json
{
  "dependencies": {
    "zod": "^4",
    "drizzle-orm": "latest",
    "hono": "^4",
    "@trpc/server": "^11",
    "@trpc/client": "^11",
    "tailwindcss": "^4"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^24",
    "tsup": "^8",
    "vitest": "^4",
    "@vitest/coverage-v8": "^4",
    "@playwright/test": "^1",
    "oxlint": "latest",
    "@biomejs/biome": "latest",
    "husky": "^9",
    "lint-staged": "^16",
    "drizzle-kit": "latest",
    "drizzle-zod": "latest"
  },
  "engines": {
    "node": ">=22.22.0"
  }
}
```

**With residual ESLint (gap plugins needed):** Add to devDependencies:
```json
{
  "devDependencies": {
    "eslint": "^10",
    "eslint-plugin-oxlint": "latest"
  }
}
```

**Cloudflare Workers Projects:** Replace Vitest with pinned version:
```json
{
  "devDependencies": {
    "vitest": "~3.2.0",
    "@cloudflare/vitest-pool-workers": "latest"
  }
}
```

---

## Component Breakdown

### TypeScript (Strict Mode)

**Role:** Foundation language

**Why:** Transforms runtime errors into compile-time errors. Claude sees type mismatches immediately and self-corrects. Strict mode enables the full suite of type checking that catches entire categories of bugs before execution.

**Standard tsconfig.json:**
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

**Critical strictness options:**
- `noUncheckedIndexedAccess` - Array access returns `T | undefined`
- `useUnknownInCatchVariables` - `catch(e)` is `unknown`, not `any`
- `noImplicitOverride` - Requires `override` keyword in subclasses

---

### Node.js LTS

**Role:** Server runtime

**Why:** Maximum compatibility and Claude training data. Every npm package works. Battle-tested in production. Enterprise infrastructure standardized on Node.

**Version policy:** Node 24 (latest patch) for new projects, minimum Node 22.22.0+ for all projects (CVE security baseline).

---

### pnpm

**Role:** Package manager

**Why:**
- **Fastest:** 2-3x faster than npm
- **Strictest:** Won't let you import phantom dependencies (packages not in your package.json)
- **Disk efficient:** Uses hard links - same package version stored once globally
- **Monorepo native:** Built-in workspace support

**Installation:**
```bash
# Install globally
npm install -g pnpm

# Or via corepack (Node 16.13+)
corepack enable
corepack prepare pnpm@latest --activate
```

**Commands (same as npm):**
```bash
pnpm install              # Install all dependencies
pnpm add zod              # Add dependency
pnpm add -D vitest        # Add dev dependency
pnpm remove zod           # Remove dependency
pnpm run build            # Run script (or just: pnpm build)
pnpm test                 # Run test script
pnpm dlx create-next-app  # Execute package (like npx)
```

**Standard .npmrc:**
```ini
# Require Node version match from package.json "engines"
engine-strict=true

# Save exact versions (1.2.3 not ^1.2.3)
save-exact=true

# Hoist packages for compatibility (enable only if needed)
# shamefully-hoist=true
```

**package.json enforcement:**
```json
{
  "engines": {
    "node": ">=22.22.0"
  }
}
```

**Lockfile:** `pnpm-lock.yaml` (commit this to git)

**Strictness note:** pnpm's strict mode prevents importing packages not in your package.json. If a package breaks:
1. **Preferred:** Add the missing dependency explicitly
2. **Fallback:** Enable `shamefully-hoist=true` in .npmrc (makes pnpm behave like npm)

**Why not npm?** Slower, looser dependency resolution, larger disk usage.
**Why not yarn?** yarn v1 is comparable to npm; yarn v2+ (Berry) has compatibility issues.

---

### Path Aliases

**Role:** Clean imports, refactor-safe paths

**Why:** Deep relative imports are fragile and ugly. Path aliases provide stable, readable imports.

```typescript
// BAD - fragile, breaks on refactor
import { db } from '../../../lib/db';
import { UserSchema } from '../../../../schemas/user';

// GOOD - clean, refactor-safe
import { db } from '@/lib/db';
import { UserSchema } from '@/schemas/user';
```

**Standard tsconfig.json paths:**
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

**Build tool configuration:**

| Tool | Config Required |
|------|-----------------|
| tsup | Automatic (reads tsconfig) |
| esbuild | Automatic (reads tsconfig) |
| Next.js | Automatic (reads tsconfig) |
| Vite | Requires vite.config.ts |

**Vite config (if needed):**
```typescript
// vite.config.ts
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

---

### Environment Variables (Type-Safe Config)

**Role:** Runtime configuration with compile-time safety

**Why:** Environment variables are strings. Without validation, you get runtime errors when config is missing or malformed. Zod parsing catches these at startup.

**Standard pattern (all projects):**

```typescript
// src/env.ts
import { z } from 'zod';
import 'dotenv/config';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
});

export const env = envSchema.parse(process.env);
```

```typescript
// Usage - fully typed, guaranteed to exist
import { env } from '@/env';

env.PORT         // number (not string)
env.DATABASE_URL // string (validated URL)
env.API_KEY      // string (guaranteed non-empty)
```

**App crashes immediately on startup if config is invalid** - not at 3am when that code path runs.

**For Next.js (with client/server separation):**

```bash
pnpm add @t3-oss/env-nextjs
```

```typescript
// src/env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    API_KEY: z.string().min(1),
  },
  client: {
    NEXT_PUBLIC_API_URL: z.string().url(),
  },
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    API_KEY: process.env.API_KEY,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
});
```

**Benefits of @t3-oss/env-nextjs:**
- Separates server/client variables (prevents leaking secrets)
- Build-time validation
- TypeScript inference

**Dependencies:**
```bash
# All projects
pnpm add dotenv zod

# Next.js projects
pnpm add @t3-oss/env-nextjs
```

---

### tsup (Backend Builds)

**Role:** TypeScript bundler for Node.js backends

**Why:**
- Built on esbuild (very fast)
- Zero-config for common cases
- Built-in `.d.ts` generation
- Sensible Node.js defaults
- Handles externals intelligently

**Standard tsup.config.ts:**
```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node24',
  dts: true,
  clean: true,
  sourcemap: true,
  shims: true,
});
```

**For CLI tools / MCP servers (executable):**
```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node24',
  dts: true,
  clean: true,
  sourcemap: true,
  banner: {
    js: '#!/usr/bin/env node'
  }
});
```

**package.json scripts:**
```json
{
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "typecheck": "tsc --noEmit"
  }
}
```

**Pattern:** Use `tsc --noEmit` for type checking, `tsup` for building. Best of both worlds.

**Why not plain tsc?**
| Aspect | tsc | tsup |
|--------|-----|------|
| Speed | Slow | 10-100x faster |
| Bundling | No | Single file output |
| DTS | Yes | Yes (built-in) |
| Tree-shaking | No | Yes |

---

### Drizzle + PostgreSQL

**Role:** Database ORM

**Why:**
- Schemas are pure TypeScript (not a DSL like Prisma)
- SQL-like query builder (no abstraction overhead)
- Lightweight (~35KB vs Prisma's ~2MB)
- Edge-compatible (no binary engine required)
- Claude reads your DB schema as TypeScript code

```typescript
import { pgTable, text, integer, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  age: integer('age'),
  createdAt: timestamp('created_at').defaultNow()
});

// Queries are SQL-like
const result = await db
  .select()
  .from(users)
  .where(eq(users.email, 'test@example.com'));
```

**Why not Prisma?** Prisma uses a `.prisma` DSL file, introducing a translation layer. Drizzle's TypeScript-native approach means Claude doesn't need to learn a separate language, and types flow without code generation.

**SQLite variant (for local/embedded databases):**

```bash
pnpm add drizzle-orm better-sqlite3
pnpm add -D drizzle-kit @types/better-sqlite3
```

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';

export const users = sqliteTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  age: integer('age'),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date())
});

const sqlite = new Database('local.db');
export const db = drizzle(sqlite);
```

| Use Case | Database | Drizzle Package |
|----------|----------|-----------------|
| Production APIs | PostgreSQL | `drizzle-orm/pg-core` + `postgres` |
| Local/CLI/Embedded | SQLite | `drizzle-orm/sqlite-core` + `better-sqlite3` |
| Edge/Serverless | Turso (libSQL) | `drizzle-orm/libsql` + `@libsql/client` |

---

### drizzle-kit (Database Migrations)

**Role:** Schema migrations and database management

**Why:** Completes the Drizzle workflow - push schemas, generate migrations, apply to production.

**Setup:**

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',  // or 'sqlite'
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

**package.json scripts:**
```json
{
  "scripts": {
    "db:push": "drizzle-kit push",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:studio": "drizzle-kit studio"
  }
}
```

**Workflow:**

| Command | Use | Environment |
|---------|-----|-------------|
| `pnpm db:push` | Push schema directly (fast iteration) | Development |
| `pnpm db:generate` | Generate SQL migration files | Before deployment |
| `pnpm db:migrate` | Apply migrations | Production |
| `pnpm db:studio` | Visual database browser | Development |

**Migration files** (generated in `./drizzle/`):
```sql
-- 0001_add_users_table.sql
CREATE TABLE "users" (
  "id" text PRIMARY KEY,
  "email" text NOT NULL UNIQUE,
  "name" text NOT NULL
);
```

---

### drizzle-zod

**Role:** Schema bridge

**Why:** Automatically generates Zod validation schemas from Drizzle tables. Define once, validate everywhere.

```typescript
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { z } from 'zod';

// Define table once
export const users = pgTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text('email').notNull(),
  name: text('name').notNull(),
  age: integer('age'),
  createdAt: timestamp('created_at').defaultNow()
});

// Schemas derived automatically with refinements
export const insertUserSchema = createInsertSchema(users, {
  email: z.string().email().min(5).max(255),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150).optional()
}).omit({ id: true, createdAt: true });

export type InsertUser = z.infer<typeof insertUserSchema>;
```

| Function | Purpose | Use For |
|----------|---------|---------|
| `createInsertSchema` | Data going INTO database | Forms, API inputs, tRPC mutations |
| `createSelectSchema` | Data coming FROM database | API responses, type inference |

---

### Zod

**Role:** Runtime validation + type inference

**Why:** Single source of truth for validation. Define once, use everywhere:
- tRPC input validation
- Form validation (React Hook Form)
- API response validation
- Environment variable parsing

```typescript
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100)
});

type CreateUserInput = z.infer<typeof CreateUserSchema>;
// Types and validation are always in sync
```

---

### tRPC

**Role:** Type-safe API layer (internal APIs)

**Why:** Eliminates the API boundary. Backend functions become directly callable from frontend with full type inference. No OpenAPI specs, no code generation, no drift.

```typescript
// Server
export const appRouter = router({
  user: router({
    create: procedure
      .input(insertUserSchema)
      .mutation(async ({ input }) => {
        const [user] = await db.insert(users).values(input).returning();
        return user;
      }),
    byId: procedure
      .input(z.object({ id: z.string() }))
      .query(({ input }) => db.query.users.findFirst({
        where: eq(users.id, input.id)
      }))
  })
});

// Client - types flow automatically
const createUser = trpc.user.create.useMutation();
createUser.mutate({ email: 'test@example.com', name: 'Test' });
// ^^ Fully typed from Drizzle → drizzle-zod → tRPC → React
```

---

### Hono + OpenAPI (External APIs)

**Role:** HTTP framework for public/external APIs

**Why:** When external developers (non-TypeScript, different codebases) consume your API, use OpenAPI for language-agnostic clients.

```typescript
import { OpenAPIHono, createRoute, z } from '@hono/zod-openapi';

const getUserRoute = createRoute({
  method: 'get',
  path: '/users/{id}',
  request: {
    params: z.object({ id: z.string() })
  },
  responses: {
    200: {
      content: { 'application/json': { schema: selectUserSchema } },
      description: 'User found'
    }
  }
});

app.doc('/openapi.json', { openapi: '3.0.0', info: { title: 'API', version: '1.0.0' } });
```

**Decision guide:**
- Pure internal API, both ends in one TS monorepo, no external/MCP consumer → tRPC
- Anything with an external consumer, a separate SPA dashboard, **or an MCP server** → `@hono/zod-openapi` **single-source (Option-B back-to-front)** — the recommended default. One `createRoute()` single-sources request+response validation, the generated OpenAPI doc, dashboard client types, and MCP tool schemas. See "The Option-B Back-to-Front Pattern (Recommended Default)" below for the canonical definition and `patterns/api-patterns.md` for the implementation gotchas.

---

### Oxlint + Biome (Linting + Formatting)

**Role:** Linting (Oxlint) + formatting (Biome)

**Why Oxlint + Biome (replacing ESLint + Prettier):**
- **50-100x faster** than ESLint, 25x faster than Prettier
- **3 packages** for most projects vs 13+ with ESLint + Prettier
- **668 built-in rules** across 14 native plugins (React, Next.js, TypeScript, Vitest, Node.js, jsx-a11y, import, promise, unicorn — all zero npm deps)
- **Residual ESLint** only needed for gap plugins (Vue templates, Astro, Tailwind class sorting, Playwright, Obsidian)

**Core install (all projects):**
```bash
pnpm add -D oxlint @biomejs/biome typescript
```

**Standard oxlint.json:**
```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["import", "promise"],
  "rules": {},
  "ignorePatterns": ["dist", "node_modules", "coverage", ".next"]
}
```

Enable framework plugins as needed by adding to `plugins` array:
- React: `"react", "jsx-a11y"`
- Next.js: `"react", "jsx-a11y", "nextjs"`
- Node.js: `"node"`
- Vitest: `"vitest"`

**Standard biome.json:**
```json
{
  "$schema": "https://biomejs.dev/schemas/2.0.0/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "linter": { "enabled": false },
  "javascript": {
    "formatter": { "quoteStyle": "single", "trailingCommas": "es5", "semicolons": "always" }
  },
  "assist": {
    "actions": { "source": { "organizeImports": "on" } }
  },
  "files": {
    "includes": ["**/*.{ts,tsx,js,jsx,json,jsonc,css,md}"]
  }
}
```

**Residual ESLint (only for gap plugins):**
```bash
# Only install when a gap plugin is needed
pnpm add -D eslint eslint-plugin-oxlint

# Example: Tailwind class sorting (replaces prettier-plugin-tailwindcss)
pnpm add -D eslint-plugin-better-tailwindcss

# Example: Vue templates
pnpm add -D eslint-plugin-vue typescript-eslint
```

See `/lint` skill for the full framework detection matrix and residual ESLint config templates.

---

### Husky + lint-staged (Mandatory)

**Role:** Pre-commit hooks

**Why:** Enforces standards automatically. Every commit is linted and formatted. No exceptions.

**Setup:**
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
echo "npx lint-staged" > .husky/pre-commit
```

**Standard lint-staged config (package.json):**
```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": [
      "oxlint --fix --max-warnings=0",
      "biome format --write"
    ],
    "*.css": [
      "biome format --write"
    ],
    "*.{json,md}": [
      "biome format --write"
    ]
  }
}
```

---

### Vitest + Playwright

**Role:** Testing

**Why Vitest:**
- Jest-compatible API (maximum Claude training data)
- Faster than Jest
- Works with Vite (frontend) and standalone (backend)
- Universal across all project types

**Standard vitest.config.ts:**
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
});
```

**Why Playwright (E2E):**
- Multi-browser testing
- Excellent TypeScript support
- Auto-waiting (no flaky tests)
- Works for web apps and API testing

---

### Tailwind CSS + shadcn/ui

**Role:** Styling

**Why Tailwind:** Utility-first CSS that Claude generates accurately. Styles colocated with components. No context-switching.

**Why shadcn/ui:** Not a component library - copy-paste components you own. Built on Radix UI (accessibility handled) + Tailwind. Claude reads the components in your codebase and generates consistent code.

```bash
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button card dialog form input
```

Components land in `components/ui/` - you own and modify them freely.

---

## Complete Type Flow

The Ironclad Stack's key advantage: single source of truth flowing through every layer.

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                               │
│  Drizzle Table Definition (TypeScript)                          │
│  export const users = pgTable('users', { ... })                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        drizzle-zod
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYER                              │
│  Zod Schemas (auto-generated)                                   │
│  export const insertUserSchema = createInsertSchema(users)      │
│  export type InsertUser = z.infer<typeof insertUserSchema>      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
┌───────────────────────────┐ ┌───────────────────────────────────┐
│       API LAYER           │ │        FRONTEND LAYER             │
│  tRPC Router              │ │  React Hook Form                  │
│  .input(insertUserSchema) │ │  zodResolver(insertUserSchema)    │
└───────────────────────────┘ └───────────────────────────────────┘
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TYPE INFERENCE                                │
│  InsertUser type available everywhere                           │
│  - Backend handlers: fully typed                                │
│  - Frontend forms: fully validated                              │
│  - API responses: fully typed                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Result:** Change the Drizzle table → Zod schema updates → tRPC input updates → Form validation updates → TypeScript errors show everywhere that needs fixing.

---

## The Option-B Back-to-Front Pattern (Recommended Default) — CANONICAL

> **This section is the canonical definition of the back-to-front ironclad pattern.** Other references point here; do not duplicate it. Keep project-specific adoption records (which tools use it, migration milestones) in your own project documentation.

For back-end and back-to-front projects (a Worker/API that owns the contract, with a dashboard and/or MCP server consuming its types), this is the **default architecture**. The boundary for when *not* to use it is in "Back-to-Front vs Front-to-Back" below.

### Core principle: one shared Zod route definition is the single source of truth

Using `@hono/zod-openapi`, ONE `createRoute()` + `.openapi()` definition single-sources **all four** of:

1. **Runtime validation** — both request and response are described by the same schema (requests are validated; responses are documented — see gotchas).
2. **The OpenAPI document** — *generated* from the route registry (never hand-written), with `info.version` self-healing from the build `VERSION`.
3. **The typed dashboard/client types** — the dashboard infers `z.input` (pre-default form shapes); Worker consumers infer `z.infer` / `z.output` (defaults applied).
4. **The MCP tool input schemas** — the MCP server's tools source the shared schema's `.shape`.

```
                 shared/  (single source of truth)
                 Zod route def: createRoute() + .openapi()
                              │
        ┌──────────┬──────────┴──────────┬──────────────┐
        ↓          ↓                      ↓              ↓
   request +    OpenAPI doc          dashboard       MCP tool
   response     (generated from      client types    input schemas
   validation   route registry)      (z.input /      (shared .shape)
   (runtime)    + API Shield         z.infer)
```

### Why `@hono/zod-openapi` (not a rewrite)

`OpenAPIHono` **extends `Hono`** — `.route()`, `.use()`, `.onError()`, and `.request()` all behave identically. Adoption is therefore an **incremental, strangler-safe, per-router conversion**: converted `.openapi()` routers mount alongside plain Hono routers on the same instance, so you migrate one router at a time without a big-bang rewrite. Convert routers in a deliberate sequence (typically lowest-risk, fewest-consumer routers first; auth-heavy and storage/opaque-content routers last), shipping each conversion independently behind the full test suite.

### Reference stack

The standard shape for this pattern — a pnpm workspace monorepo (workspace directory names are illustrative; a nested `packages/*` layout works well for new projects):

| Workspace | Role |
|-----------|------|
| **API / Worker** | Hono + `@hono/zod-openapi` + Zod 4 — owns routes, generates the OpenAPI doc |
| **`shared/`** | The single-source-of-truth package: Zod schemas, inferred types, error catalog, the shared success/error response envelope |
| **dashboard** | React 19 + Vite + Tailwind + shadcn dashboard — imports types from `shared/` |
| **MCP** *(optional)* | stdio MCP server — tool input schemas source `shared/` schema `.shape` |

Supporting (typical for a Workers deployment): Stytch B2B auth + RBAC (or your own auth setup); Cloudflare KV / D1 / R2 as the tool needs; Drizzle (+ drizzle-zod where DB types feed the chain); Biome (format) + Oxlint (lint, `--max-warnings=0`) + Vitest (Cloudflare Workers pool); CI (`lint → format:check → typecheck-all-workspaces → test-all-workspaces`, then deploy: `develop`→dev, `main`→prod).

### API Shield integration (Cloudflare)

The *generated* OpenAPI doc feeds **Cloudflare API Shield** schema validation in **BLOCK mode** on the zone. Two consequences make the freshness machinery non-negotiable:

- **A path absent from the uploaded spec 403s ALL traffic to it.** Dropping a path from the generated doc is a production outage, not a docs nit.
- Gate the spec upload inside each environment's deploy step, uploading the schema for **that environment's host**, then sync the schema's operations into **Endpoint Management** — API Shield validates only managed operations, so a schema upload alone leaves unmanaged paths silently unvalidated.

Two guards protect this (both detailed in `patterns/api-patterns.md`):

1. **Parity test** — the generated doc must be a *superset* of a committed baseline of live operations (no path silently dropped).
2. **Freshness gate** — wired into `pnpm run check`: the committed spec must equal the generator output, so CI fails on drift.

### Back-to-Front vs Front-to-Back: which to choose

| | **Back-to-front (this pattern — DEFAULT)** | **Front-to-back** |
|---|---|---|
| Owns the contract | The API/Worker (`shared/` Zod) | The frontend framework |
| Types flow | OUT from the Worker → dashboard + MCP | Co-located in the framework (server actions / RSC / route handlers) |
| Shape | Worker + SPA dashboard + MCP, split workspaces | One Next.js full-stack app |
| Choose when | The project is fundamentally an **API + SPA (+ MCP)** split — a service, internal tool, or platform API | The project is fundamentally a **Next.js web app**, not an API+SPA split |
| Reference | This section + `patterns/api-patterns.md` | `Full-Stack Web App` config below |

**Default to back-to-front** for services, APIs, and internal tools. Use front-to-back (Next.js full-stack — server actions, RSC, route handlers, types co-located) only when the project genuinely *is* a Next.js web app. tRPC remains the right internal-API choice when there is no external/MCP consumer and both ends live in one TypeScript monorepo (see `tRPC` above).

> **Gotchas:** the hard-won `@hono/zod-openapi` gotchas (defaultHook error funnelling, validation-vs-middleware ordering, repeated query keys, MCP arg coercion, `.refine()` enum loss, opaque content types, request-only validation) are codified in `patterns/api-patterns.md` → "@hono/zod-openapi Single-Source Pattern".

---

## Project-Type Configurations

The core stack is universal. Framework and build tool choices vary by project type:

### Full-Stack Web App

| Layer | Technology |
|-------|------------|
| Framework | Next.js (App Router) |
| Build | Built-in |
| API | tRPC via API routes |
| Database | Drizzle + drizzle-zod + PostgreSQL |
| Frontend | React (Server Components) |

**Quick start:**
```bash
pnpm dlx create-next-app@latest my-app --typescript --tailwind --app
cd my-app
pnpm add @trpc/server @trpc/client @trpc/react-query @tanstack/react-query zod
pnpm add drizzle-orm drizzle-zod postgres
pnpm add -D drizzle-kit vitest @playwright/test oxlint @biomejs/biome husky lint-staged
pnpm dlx husky init && echo "npx lint-staged" > .husky/pre-commit
pnpm dlx shadcn@latest init
echo "24.13" > .nvmrc
echo 'engine-strict=true\nsave-exact=true' > .npmrc
```

---

### API / Microservice

| Layer | Technology |
|-------|------------|
| Framework | Hono |
| Build | tsup |
| API | tRPC or OpenAPI |
| Database | Drizzle + drizzle-zod + PostgreSQL |

**Quick start:**
```bash
mkdir my-api && cd my-api
pnpm init
pnpm add hono @trpc/server zod drizzle-orm drizzle-zod postgres
pnpm add -D typescript @types/node@^24 tsup drizzle-kit vitest husky lint-staged
pnpm dlx tsc --init
pnpm dlx husky init && echo "pnpm dlx lint-staged" > .husky/pre-commit
echo "24.13" > .nvmrc
echo 'engine-strict=true\nsave-exact=true' > .npmrc
```

---

### Cloudflare Workers API (Edge)

| Layer | Technology |
|-------|------------|
| Framework | Hono |
| Build | wrangler |
| API | tRPC or OpenAPI |
| Database | Drizzle + D1 (edge SQLite) |
| Environment | Workers bindings (not dotenv) |

**Quick start:**
```bash
mkdir my-api && cd my-api
pnpm init
pnpm add hono @trpc/server @hono/trpc-server zod drizzle-orm
pnpm add -D wrangler drizzle-kit typescript vitest husky lint-staged
wrangler d1 create my-db
echo "24.13" > .nvmrc
echo 'engine-strict=true\nsave-exact=true' > .npmrc
```

**Key differences from Node.js API:**
- Use `wrangler` instead of `tsup`
- Use D1 instead of PostgreSQL/better-sqlite3
- Use Workers bindings instead of `dotenv`
- No native bindings allowed

> **Full reference:** See `cloudflare.md` for complete setup, Wrangler CLI, Hono patterns, and D1 integration.

---

### SPA (Single Page App)

| Layer | Technology |
|-------|------------|
| Framework | React |
| Build | Vite |
| API | tRPC client to backend |
| State | TanStack Query |

**Quick start:**
```bash
pnpm create vite@latest my-spa -- --template react-ts
cd my-spa
pnpm add @trpc/client @trpc/react-query @tanstack/react-query zod
pnpm add -D vitest @playwright/test husky lint-staged
pnpm dlx husky init && echo "pnpm dlx lint-staged" > .husky/pre-commit
pnpm dlx shadcn@latest init
echo "24.13" > .nvmrc
echo 'engine-strict=true\nsave-exact=true' > .npmrc
```

---

### Obsidian Plugin

| Layer | Technology |
|-------|------------|
| Framework | Obsidian API |
| Build | esbuild (ecosystem standard) |
| Output | CommonJS (required) |
| Linting | Oxlint + residual ESLint (eslint-plugin-obsidianmd) |

**Special requirements:**
- Must output CommonJS (Obsidian requirement)
- Use `eslint-plugin-obsidianmd` via residual ESLint for Obsidian-specific rules
- Runtime is Electron renderer, not Node.js
- Keep esbuild (matches official template and ecosystem)

---

### MCP Server

| Layer | Technology |
|-------|------------|
| Framework | @modelcontextprotocol/sdk |
| Build | tsup |
| Transport | stdio |
| Runtime | **Node.js (REQUIRED)** |

**Quick start:**
```bash
mkdir my-mcp && cd my-mcp
pnpm init
pnpm add @modelcontextprotocol/sdk zod
pnpm add -D typescript @types/node@^24 tsup vitest husky lint-staged
pnpm dlx tsc --init
pnpm dlx husky init && echo "pnpm dlx lint-staged" > .husky/pre-commit
echo "24.13" > .nvmrc
echo 'engine-strict=true\nsave-exact=true' > .npmrc
```

**tsup.config.ts for MCP:**
```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node24',
  dts: true,
  clean: true,
  sourcemap: true,
  banner: { js: '#!/usr/bin/env node' }
});
```

**Critical:** Bun runtime is NOT compatible with MCP SDK stdio transport or neo4j-driver. Always use Node.js.

---

### CLI Tool

| Layer | Technology |
|-------|------------|
| Framework | Commander or Yargs |
| Build | tsup |

**Quick start:**
```bash
mkdir my-cli && cd my-cli
pnpm init
pnpm add commander zod
pnpm add -D typescript @types/node@^24 tsup vitest husky lint-staged
pnpm dlx tsc --init
pnpm dlx husky init && echo "pnpm dlx lint-staged" > .husky/pre-commit
echo "24.13" > .nvmrc
echo 'engine-strict=true\nsave-exact=true' > .npmrc
```

---

### npm Library/Package

| Layer | Technology |
|-------|------------|
| Build | tsup |
| Output | ESM + CJS + .d.ts |
| Testing | Vitest |

**tsup.config.ts for library:**
```typescript
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  target: 'node22',  // Minimum supported
  dts: true,
  clean: true,
  sourcemap: true,
});
```

---

### Content Site (Marketing/Docs)

| Layer | Technology |
|-------|------------|
| Framework | Astro |
| Interactivity | React islands (when needed) |

**When to use Astro:**
- Content-driven sites with selective interactivity
- SEO-critical websites
- Marketing pages, documentation, blogs

---

## Decision Tree

```
What are you building?
│
├─► API/Microservice (incl. API + SPA dashboard + MCP)?
│   ├─► Owns the contract for a dashboard and/or MCP consumer?  ◄── recommended DEFAULT
│   │   └─► Option-B back-to-front: @hono/zod-openapi single-source
│   ├─► Public/Edge-deployed?
│   │   └─► Cloudflare Workers + Hono + D1 (see cloudflare.md)
│   └─► Private/Self-hosted, no external/MCP consumer?
│       └─► Hono + tsup + PostgreSQL/SQLite (tRPC if both ends in one monorepo)
│
├─► Full-stack web app with SSR/SEO?
│   ├─► Edge-deployed?
│   │   └─► Next.js + @cloudflare/next-on-pages
│   └─► Traditional?
│       └─► Next.js (App Router) + tRPC + Drizzle
│
├─► SPA (client-side only)?
│   └─► React + Vite + tRPC client
│       Deploy: Cloudflare Pages or self-hosted
│
├─► Obsidian plugin?
│   └─► Obsidian API + esbuild + Oxlint + residual ESLint (eslint-plugin-obsidianmd)
│
├─► MCP server?
│   └─► MCP SDK + tsup + Node.js (mandatory, not edge-compatible)
│
├─► CLI tool?
│   └─► Commander/Yargs + tsup (local execution)
│
├─► npm package?
│   └─► tsup (ESM + CJS + types)
│
└─► Content/marketing site?
    └─► Astro + Cloudflare Pages (or React islands)
```

> **Deployment details:** See `typescript-ironclad-infra.md` for full deployment decision framework.

---

## Appendix: Bun Considerations

Bun is **NOT** part of the universal stack as a runtime due to compatibility issues:

**Known incompatibilities:**
- neo4j-driver: TCP/Bolt protocol issues ([oven-sh/bun#9914](https://github.com/oven-sh/bun/issues/9914))
- MCP SDK: stdio transport concerns
- Various npm packages with native bindings

**Safe uses of Bun (optional optimization):**

| Use | Safe? | Notes |
|-----|-------|-------|
| `bun install` | ✅ Yes | 3-10x faster than npm |
| `bun run <script>` | ✅ Usually | Works for most dev scripts |
| `bun <file.ts>` runtime | ❌ No | Use Node.js |
| `bun test` | ❌ No | Use Vitest |

**Recommendation:** Use `bun install` for speed if desired. Always use Node.js for runtime.

---

## Appendix: Prisma Alternative

Prisma remains a valid choice for teams that prefer its abstraction. Trade-offs:

| Aspect | Drizzle | Prisma |
|--------|---------|--------|
| Schema language | TypeScript | .prisma DSL |
| Claude training data | Good | Excellent |
| Type flow | Native TS | Generated types |
| Bundle size | ~35KB | ~2MB |
| Edge compatibility | Yes | No (binary engine) |
| drizzle-zod integration | Native | Manual Zod schemas |

For the Ironclad Stack, Drizzle is preferred because TypeScript-native schemas mean Claude works in one language with no DSL translation.

---

## Appendix: Private npm Registry (Verdaccio)

For private packages within your organization, use Verdaccio with Tailscale for secure internal hosting.

### Why Verdaccio

- **Free and self-hosted** - No per-user costs
- **Lightweight** - Single Node.js process or Docker container
- **npm proxy** - Caches public packages, serves private packages
- **Simple auth** - htpasswd or integrate with existing auth

### Docker Setup

**docker-compose.yml:**
```yaml
services:
  verdaccio:
    image: verdaccio/verdaccio
    container_name: verdaccio
    restart: unless-stopped
    ports:
      - "4873:4873"
    volumes:
      - verdaccio-storage:/verdaccio/storage
      - verdaccio-conf:/verdaccio/conf
    environment:
      - VERDACCIO_PORT=4873

volumes:
  verdaccio-storage:
  verdaccio-conf:
```

```bash
docker compose up -d
```

### Tailscale Serve (Internal Access)

Expose Verdaccio securely within Tailscale network:

```bash
# Serve on tailnet only (no public internet)
tailscale serve --bg 4873

# Access at https://npm.<tailnet>.ts.net/
```

**For persistent HTTPS serve:**
```bash
tailscale serve status  # Check current config
tailscale serve reset   # Clear config
tailscale serve --bg --https=443 http://localhost:4873
```

Access at: `https://npm.<tailnet>.ts.net/`

### Client Configuration

**.npmrc (project or user level):**
```ini
# Use Verdaccio for @myorg scoped packages
@myorg:registry=https://npm.<tailnet>.ts.net/

# Auth token (generate via: pnpm login --registry=https://npm.<tailnet>.ts.net/)
//npm.<tailnet>.ts.net/:_authToken=${VERDACCIO_TOKEN}

# Public packages still come from npm
registry=https://registry.npmjs.org/
```

### Publishing Private Packages

```bash
# Login once
pnpm login --registry=https://npm.<tailnet>.ts.net/

# Publish (package.json must have @myorg scope)
pnpm publish --registry=https://npm.<tailnet>.ts.net/
```

**package.json for private package:**
```json
{
  "name": "@myorg/shared-utils",
  "version": "1.0.0",
  "private": false,
  "publishConfig": {
    "registry": "https://npm.<tailnet>.ts.net/"
  }
}
```

### Why Tailscale Serve (Not Public)

- **Zero config HTTPS** - Tailscale handles certs automatically
- **No port forwarding** - Works behind NAT/firewalls
- **Auth built-in** - Only tailnet members can access
- **No public exposure** - Registry never touches public internet

---

## Appendix: .gitignore Template

Standard .gitignore for Ironclad Stack projects:

```gitignore
# Dependencies
node_modules/
.pnpm-store/

# Build outputs
dist/
build/
.next/
out/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
coverage/

# Logs
*.log
npm-debug.log*
pnpm-debug.log*

# Database
*.db
*.sqlite
drizzle/meta/

# Misc
.turbo/
.cache/
```

---

## Summary

### The Ironclad Stack

```
Language:           TypeScript (Strict)
Runtime:            Node.js 24 LTS (minimum 22)
Package Manager:    pnpm
Path Aliases:       @/* → src/*
Environment:        Zod + dotenv (type-safe config)
Validation:         Zod
ORM:                Drizzle + drizzle-kit (PostgreSQL or SQLite)
API (internal):     tRPC (both ends in one TS monorepo, no external/MCP consumer)
API (back-to-front): @hono/zod-openapi single-source — recommended DEFAULT for API + dashboard/MCP
Build (backend):    tsup
Build (frontend):   Vite
Testing:            Vitest + Playwright
Linting:            Oxlint (primary) + residual ESLint (gap plugins)
Formatting:         Biome (linter disabled)
Pre-commit:         Husky + lint-staged (mandatory)
Styling:            Tailwind CSS + shadcn/ui
Framework:          Varies by project type
```

### Key Properties

- **Claude Code optimized:** Maximum training data coverage
- **End-to-end type safe:** Drizzle → drizzle-zod → Zod → tRPC → React
- **Universal:** Works for all project types
- **Edge-compatible:** Core stack works on Cloudflare Workers
- **Enforced:** Pre-commit hooks prevent violations
- **Single source of truth:** Change the Drizzle table, everything updates

### Companion Documents

| Document | Purpose |
|----------|---------|
| `cloudflare.md` | Complete Cloudflare Workers/D1/Wrangler reference |
| `typescript-ironclad-infra.md` | Deployment and infrastructure guide |
| `patterns/api-patterns.md` | `@hono/zod-openapi` single-source implementation + API Shield guards + hard-won gotchas |

---

*Last updated: 2026-06-05 (Option-B back-to-front single-source pattern added as recommended default — `@hono/zod-openapi`; Zod 4 default for new projects; pnpm 10.28.2 latest stable; de-repo pass 2026-09-28)*
