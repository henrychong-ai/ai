# ORM Standard — Drizzle and Prisma

This stack uses two ORMs, each in its own kind of project. Pick by project type, not preference.

| Project type | ORM | Databases |
|--------------|-----|-----------|
| Internal tools (Hono API + SPA dashboard), Cloudflare Workers services | **Drizzle** | D1 / SQLite on Workers; PostgreSQL on Node |
| Product apps: Next.js full-stack apps and Fastify services | **Prisma 7** | PostgreSQL and SQL Server |

A service that only reads another system's database (for example a read-only SQL Server source next to its own Drizzle database) may use the plain driver (`mssql`, `pg`) behind one isolated module instead of adding a second ORM.

Versions: `version-policy.md`.

## Why two

- **Drizzle** schemas are TypeScript, so types flow straight into Zod (`drizzle-zod`) and on into the `@hono/zod-openapi` contract (`typescript-ironclad-stack.md`). It runs on D1 with no build step.
- **Prisma** gives product apps a schema file, a mature migration workflow, SQL Server support and generated clients that many developers already know. Since **Prisma 7** the client is Rust-free (a TypeScript/WASM query compiler, about 1.6 MB instead of about 14 MB), so it also runs on edge runtimes through driver adapters. "Prisma cannot run on the edge" is no longer true.

| Aspect | Drizzle | Prisma 7 |
|--------|---------|----------|
| Schema | TypeScript (`pgTable`, `sqliteTable`) | `schema.prisma` |
| Types | Inferred from the schema (`$inferSelect`) | Generated (`prisma generate`) |
| Zod bridge | `drizzle-zod` | Write Zod schemas at the API boundary |
| Migrations | `drizzle-kit generate` → SQL files (apply with `wrangler d1 migrations apply` on D1) | `prisma migrate dev` / `prisma migrate deploy` |
| SQL Server | No first-class support | Supported |
| Workers / edge | Yes (D1, Hyperdrive) | Yes, with the `prisma-client` generator + a driver adapter |
| Version line | 0.x (1.0 in release candidate) | `^7` |

## Drizzle

```typescript
// src/db/schema.ts
import { integer, pgTable, text, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  age: integer('age'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
```

```typescript
// Zod schemas derived from the table, refined at the boundary (Zod 4)
import { createInsertSchema } from 'drizzle-zod';
import { z } from 'zod';
import { users } from './schema';

export const InsertUserSchema = createInsertSchema(users, {
  email: () => z.email().max(255),
  name: (schema) => schema.min(1).max(100),
}).omit({ id: true, createdAt: true });
```

| Runtime | Driver |
|---------|--------|
| Workers + D1 | `drizzle-orm/d1` with the `DB` binding |
| Node + PostgreSQL | `drizzle-orm/node-postgres` (`pg`) or `drizzle-orm/postgres-js` |
| Workers + external PostgreSQL | Hyperdrive binding + `postgres` / `pg` |

Migrations: `drizzle-kit generate` creates SQL files. Apply them with the database's migration runner (`wrangler d1 migrations apply <db> --local|--remote` on D1, `drizzle-kit migrate` or the app's migrator on PostgreSQL). Do not hand-apply the newest file with `wrangler d1 execute --file`: that skips the applied-migrations ledger.

## Prisma 7

**Pin the major.** npm's `latest` tag for `prisma` has pointed at an 8.0 release candidate, so an unpinned install takes a pre-release:

```bash
pnpm add @prisma/client@^7
pnpm add -D prisma@^7
```

Keep `prisma` and `@prisma/client` on the same version. Existing apps on Prisma 6 stay there until an upgrade is planned.

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client"          // the Rust-free generator (Prisma 7 default)
  output   = "../src/generated/prisma"
}

datasource db {
  provider = "postgresql"             // or "sqlserver"
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String
  createdAt DateTime @default(now())
}
```

Prisma 7 connects through a **driver adapter**; the connection URL moves from the schema into `prisma.config.ts` (CLI: `generate`, `migrate`) and into the adapter (runtime):

```typescript
// prisma.config.ts (project root)
import { defineConfig, env } from 'prisma/config';

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: { path: 'prisma/migrations' },
  datasource: { url: env('DATABASE_URL') },
});
```

```typescript
// src/db.ts — PostgreSQL
import { PrismaPg } from '@prisma/adapter-pg';
import { env } from './env.js'; // Zod-validated at boot (typescript-ironclad-stack.md)
import { PrismaClient } from './generated/prisma/client.js';

const adapter = new PrismaPg({ connectionString: env.DATABASE_URL });
export const prisma = new PrismaClient({ adapter });
```

The `.js` extensions are required under the `NodeNext` tsconfig and also resolve under `bundler`.

| Database | Adapter package |
|----------|-----------------|
| PostgreSQL | `@prisma/adapter-pg` |
| SQL Server | `@prisma/adapter-mssql` |
| D1 (Workers) | `@prisma/adapter-d1` |

Adapter and config details change between minors: follow Prisma's "Upgrade to Prisma ORM 7" guide when moving a 6.x project, and check the adapter docs for the installed version.

Rules for both ORMs:

- Validate external input with Zod before it reaches the ORM; ORM types are not runtime validation.
- Keep one client per process (Node) or per request (Workers); never construct a client inside a hot loop.
- Commit migrations; review generated SQL before applying it to shared environments.

---

*Facts checked 2026-09-28: npm dist-tags (`prisma` latest = 8.0.0-rc.17, prev = 7.10.0; `drizzle-orm` latest = 0.45.3), Prisma 7.0 changelog (Rust-free client default). The schema, `prisma.config.ts` and `src/db.ts` above were generated and type-checked with Prisma 7.10.0 and TypeScript 6.0.3 under the `tooling.md` Node tsconfig.*
