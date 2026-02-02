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
| **Linting**          | ESLint 9 (flat config)   | Plugin ecosystem, maximum CC training data |
| **Formatting**       | Prettier                 | Consistent style                           |
| **Pre-commit**       | Husky + lint-staged      | Enforce standards automatically            |
| **Styling**          | Tailwind CSS + shadcn/ui | Utility-first, copy-paste components       |

---

## Node.js Version Policy

### Version Requirements

| Context | Version | Rationale |
|---------|---------|-----------|
| **New projects** | Node 24.13.0+ | Latest Active LTS with security patches |
| **Minimum supported** | Node 22.22.0+ | Security baseline (see below) |

### Current LTS Schedule (as of 2026-01-14)

| Version | Status | Minimum Secure Version | End of Life |
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

**`.nvmrc` (recommended):**
```
24.13.0
```

**`.node-version` (alternative):**
```
24.13.0
```

**`package.json` engines (enforcement):**
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

| Framework | New Projects | Minimum Supported | Rationale |
|-----------|--------------|-------------------|-----------|
| **Next.js** | 16.x | 15.x | Active LTS / Maintenance LTS |
| **React** | 19 | 18 | Current / Security-supported |
| **Vue** | 3.5 | 3.4 | Current active minor |

### Current LTS Schedule (as of 2026-01-14)

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

| Version | Released | Status |
|---------|----------|--------|
| **3.5** | Sep 3, 2024 | **Current (Active)** |
| 3.4 | Dec 29, 2023 | Unsupported |
| 2.7 | Jul 1, 2022 | **EOL Dec 31, 2023** |

**Policy:** Only the latest minor version receives updates. When new major releases, previous major's last minor gets 18 months bug fixes + 18 months security-only.

### Framework Version Pinning

**`package.json` (recommended):**
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}
```

**For Vue projects:**
```json
{
  "dependencies": {
    "vue": "^3.5.0"
  }
}
```

### Framework + Node.js Compatibility

| Framework | Minimum Node.js | Recommended Node.js |
|-----------|-----------------|---------------------|
| Next.js 16 | 18.18.0 | 24.13.0+ |
| Next.js 15 | 18.18.0 | 22.22.0+ |
| React 19 | 18.0.0 | 24.13.0+ |
| Vue 3.5 | 18.0.0 | 24.13.0+ |

**Note:** Always use Node.js 22.22.0+ or 24.13.0+ regardless of framework minimum to ensure security patches (CVE-2025-59466).

---

## Tool Version Policy

All tools in the Ironclad Stack have explicit version requirements. Use caret (`^`) for patch/minor updates while maintaining major version stability.

**Last updated:** 2026-01-14

### Testing Tools

| Tool | Minimum | Recommended | Notes |
|------|---------|-------------|-------|
| **Vitest** | 4.0.0 | `^4.0.0` | Current stable, Browser Mode stable |
| **@vitest/coverage-v8** | 4.0.0 | `^4.0.0` | Must match Vitest major version |
| **Playwright** | 1.50.0 | `^1.50.0` | E2E testing, auto-waiting |

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
    "@cloudflare/vitest-pool-workers": "^0.7.5"
  }
}
```

**package.json (non-Workers projects):**
```json
{
  "devDependencies": {
    "vitest": "^4.0.0",
    "@vitest/coverage-v8": "^4.0.0",
    "@playwright/test": "^1.50.0"
  }
}
```

### Build Tools

| Tool | Minimum | Recommended | Notes |
|------|---------|-------------|-------|
| **TypeScript** | 5.5.0 | `^5.7.0` | Strict mode required |
| **tsup** | 8.0.0 | `^8.0.0` | Backend/CLI builds |
| **typescript-eslint** | 8.0.0 | `^8.0.0` | ESLint TypeScript support |

**package.json:**
```json
{
  "devDependencies": {
    "typescript": "^5.7.0",
    "tsup": "^8.0.0",
    "typescript-eslint": "^8.0.0"
  }
}
```

### Database Tools (Drizzle Ecosystem)

| Tool | Minimum | Recommended | Notes |
|------|---------|-------------|-------|
| **drizzle-orm** | 0.40.0 | `^0.45.0` | TypeScript-native ORM |
| **drizzle-kit** | 0.30.0 | `^0.31.0` | Migrations CLI |
| **drizzle-zod** | 0.8.0 | `^0.8.0` | Schema-to-Zod bridge |

**Note:** Drizzle is still in 0.x (pre-1.0). API is stable but check release notes when upgrading.

**package.json:**
```json
{
  "dependencies": {
    "drizzle-orm": "^0.45.0"
  },
  "devDependencies": {
    "drizzle-kit": "^0.31.0",
    "drizzle-zod": "^0.8.0"
  }
}
```

### Validation & API Tools

| Tool | Recommended | Minimum | Notes |
|------|-------------|---------|-------|
| **Zod** | `^4.0.0` | 3.24.0 (existing projects only) | Runtime validation |
| **tRPC** | `^11.0.0` | 11.0.0 | Type-safe internal APIs |
| **Hono** | `^4.11.0` | 4.0.0 | HTTP framework, edge-compatible |
| **@hono/zod-openapi** | `^0.18.0` | 0.18.0 | OpenAPI generation |

**Zod Version Policy:**

| Context | Version | Rationale |
|---------|---------|-----------|
| **New projects** | `^4.0.0` | 14x faster string parsing, 57% smaller bundle |
| **Existing projects** | `^3.24.0` | Stay on 3.x until ready to migrate |

**Note:** Zod has **NO LTS policy** - both 3.x and 4.x are actively maintained. Current stable versions: Zod 4.3.6 (`npm latest`), Zod 3.25.76 (latest 3.x).

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
    "zod": "^4.0.0",
    "@trpc/server": "^11.0.0",
    "@trpc/client": "^11.0.0",
    "hono": "^4.11.0"
  }
}
```

**package.json (existing projects staying on 3.x):**
```json
{
  "dependencies": {
    "zod": "^3.24.0",
    "@trpc/server": "^11.0.0",
    "@trpc/client": "^11.0.0",
    "hono": "^4.11.0"
  }
}
```

### Code Quality Tools

| Tool | Minimum | Recommended | Notes |
|------|---------|-------------|-------|
| **ESLint** | 9.0.0 | `^9.0.0` | Flat config required |
| **Prettier** | 3.0.0 | `^3.0.0` | Code formatting |
| **Husky** | 9.0.0 | `^9.0.0` | Git hooks |
| **lint-staged** | 16.0.0 | `^16.0.0` | Pre-commit staging |

**ESLint 9 Flat Config:** Legacy `.eslintrc.*` configs are deprecated. Use `eslint.config.js` or `eslint.config.mjs`.

**package.json:**
```json
{
  "devDependencies": {
    "eslint": "^9.0.0",
    "prettier": "^3.0.0",
    "husky": "^9.0.0",
    "lint-staged": "^16.0.0"
  }
}
```

### Package Management

| Tool | Minimum | Recommended | Notes |
|------|---------|-------------|-------|
| **pnpm** | 10.0.0 | `^10.28.2` | Security-first defaults, latest stable |

**Version Policy:** pnpm does NOT have an LTS policy. Use the latest stable 10.x for new projects. Current stable: **10.28.2** (as of 2026-02-02).

**pnpm 10 Breaking Changes:**
- Lifecycle scripts blocked by default (security improvement)
- Nothing hoisted by default
- `pnpm link` adds to workspace root
- Requires explicit `pnpm.onlyBuiltDependencies` for native modules

**packageManager field (new projects):**
```json
{
  "packageManager": "pnpm@10.28.2"
}
```

**Update command:**
```bash
npm pkg set packageManager=pnpm@10.28.2
```

**For existing projects staying on pnpm 9:**
```json
{
  "packageManager": "pnpm@9.15.9"
}
```

### Styling Tools

| Tool | Minimum | Recommended | Notes |
|------|---------|-------------|-------|
| **Tailwind CSS** | 4.0.0 | `^4.0.0` | CSS-first config, 5x faster |
| **shadcn/ui** | N/A | Latest CLI | Copy-paste components |

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
    "tailwindcss": "^4.0.0"
  }
}
```

**For legacy browser support (stay on 3.x):**
```json
{
  "dependencies": {
    "tailwindcss": "^3.4.0"
  }
}
```

### Complete Version Summary

**New Project Dependencies (2026-02-02):**

```json
{
  "dependencies": {
    "zod": "^4.0.0",
    "drizzle-orm": "^0.45.0",
    "hono": "^4.11.0",
    "@trpc/server": "^11.0.0",
    "@trpc/client": "^11.0.0",
    "tailwindcss": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "@types/node": "^24",
    "tsup": "^8.0.0",
    "vitest": "^4.0.0",
    "@vitest/coverage-v8": "^4.0.0",
    "@playwright/test": "^1.50.0",
    "eslint": "^9.0.0",
    "typescript-eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "husky": "^9.0.0",
    "lint-staged": "^16.0.0",
    "drizzle-kit": "^0.31.0",
    "drizzle-zod": "^0.8.0"
  },
  "packageManager": "pnpm@10.28.2",
  "engines": {
    "node": ">=22.22.0"
  }
}
```

**Cloudflare Workers Projects:** Replace Vitest with pinned version:
```json
{
  "devDependencies": {
    "vitest": "~3.2.0",
    "@cloudflare/vitest-pool-workers": "^0.7.5"
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

**Version policy:** Node 24.13.0+ for new projects, minimum Node 22.22.0+ for all projects (security baseline).

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
  "packageManager": "pnpm@9.15.9",
  "engines": {
    "node": ">=22.0.0"
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
- Internal APIs (monorepo, same team) → tRPC
- External APIs (public, third-party) → OpenAPI via Hono

---

### ESLint 9 + Prettier

**Role:** Linting + formatting

**Why ESLint (not Biome):**
- Maximum Claude training data
- Plugin ecosystem (eslint-plugin-obsidianmd, jsx-a11y, etc.)
- Works for ALL project types without exceptions
- ESLint 9 flat config is simpler than legacy

**Standard eslint.config.js:**
```javascript
import tseslint from 'typescript-eslint';
import prettier from 'eslint-plugin-prettier';
import eslintConfigPrettier from 'eslint-config-prettier';

export default [
  { ignores: ['node_modules/**', 'dist/**', 'coverage/**'] },
  ...tseslint.configs.recommended,
  {
    plugins: { prettier },
    rules: {
      'prettier/prettier': 'error',
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }],
      '@typescript-eslint/explicit-function-return-type': ['warn', {
        allowExpressions: true,
        allowTypedFunctionExpressions: true,
      }],
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  },
  eslintConfigPrettier,
];
```

**Standard .prettierrc:**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

---

### Husky + lint-staged (Mandatory)

**Role:** Pre-commit hooks

**Why:** Enforces standards automatically. Every commit is linted and formatted. No exceptions.

**Setup:**
```bash
npm install --save-dev husky lint-staged
npx husky init
echo "npx lint-staged" > .husky/pre-commit
```

**Standard lint-staged config (package.json):**
```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": [
      "eslint --fix --cache",
      "prettier --write"
    ],
    "*.{json,md,css,yml,yaml}": [
      "prettier --write"
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
pnpm dlx create-next-app@latest my-app --typescript --tailwind --eslint --app
cd my-app
pnpm add @trpc/server @trpc/client @trpc/react-query @tanstack/react-query zod
pnpm add drizzle-orm drizzle-zod postgres
pnpm add -D drizzle-kit vitest @playwright/test husky lint-staged
pnpm dlx husky init && echo "pnpm dlx lint-staged" > .husky/pre-commit
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
| Linting | ESLint + eslint-plugin-obsidianmd |

**Special requirements:**
- Must output CommonJS (Obsidian requirement)
- Use `eslint-plugin-obsidianmd` for Obsidian-specific rules
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
├─► API/Microservice?
│   ├─► Public/Edge-deployed?
│   │   └─► Cloudflare Workers + Hono + D1 (see cloudflare.md)
│   └─► Private/Self-hosted?
│       └─► Hono + tsup + PostgreSQL/SQLite
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
│   └─► Obsidian API + esbuild + eslint-plugin-obsidianmd
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
API (internal):     tRPC
API (external):     Hono + OpenAPI (when needed)
Build (backend):    tsup
Build (frontend):   Vite
Testing:            Vitest + Playwright
Linting:            ESLint 9 (flat config)
Formatting:         Prettier
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

---

*Last updated: 2026-02-02 (Zod 4 default for new projects; pnpm 10.28.2 latest stable)*
