# TypeScript on Cloudflare Workers

The TypeScript-specific parts of Workers development. Platform products (KV, R2, D1, Queues, Hyperdrive, Durable Objects), limits, pricing and the Wrangler CLI are covered by Cloudflare's Workers documentation.

## Types: generate `Env`, do not hand-write it

```bash
pnpm exec wrangler types          # writes worker-configuration.d.ts from the Wrangler config
```

Commit the generated file (or regenerate it in `check`), and use the global `Env` type it declares:

```typescript
// src/index.ts
import { Hono } from 'hono';

const app = new Hono<{ Bindings: Env }>();

app.get('/health', (c) => c.json({ status: 'ok', environment: c.env.ENVIRONMENT }));

export default app; // Workers require the default export (an exception to the named-exports rule)
```

Regenerate after every binding or `vars` change; a hand-written `Bindings` type silently drifts from `wrangler.jsonc`. Prefer `wrangler.jsonc` for new projects.

## Runtime facts that change code

- **`nodejs_compat`**: enable it with a current `compatibility_date`. From compatibility date 2025-04-01, `process.env` is populated with vars and secrets (`nodejs_compat_populate_process_env`), so shared config code can read `process.env` on Workers too. Prefer `env` bindings in Worker code.
- **No filesystem, no child processes, no native addons.** Pure JS/WASM dependencies only.
- **TCP** is available through `connect()` from `cloudflare:sockets`; PostgreSQL goes through Hyperdrive.
- **Limits**: no wall-clock limit on an HTTP request while the client stays connected; CPU time defaults to 30 s on paid plans and can be raised to 5 minutes; 128 MB memory per isolate. The old "Unbound" usage model is discontinued. Check Cloudflare's limits page for current numbers.
- **Crypto**: use Web Crypto (`crypto.subtle`, `crypto.randomUUID()`); use `jose` for JWTs.
- **Multiple environments**: bindings and `vars` are **not** inherited by `env.<name>` blocks in the Wrangler config; redeclare them per environment.
- **Static assets**: responses from `env.ASSETS.fetch()` have immutable headers; copy them into a new `Response` before middleware sets headers (`patterns/api-patterns.md` → "Response Immutability with Workers Static Assets").
- **Next.js on Workers**: `@opennextjs/cloudflare`. `@cloudflare/next-on-pages` is deprecated.

## D1 with Drizzle

```typescript
// src/db/client.ts
import { drizzle } from 'drizzle-orm/d1';
import * as schema from './schema';

export const createDb = (d1: D1Database) => drizzle(d1, { schema });
export type Db = ReturnType<typeof createDb>;
```

Generate migrations with `drizzle-kit generate` and apply them with `wrangler d1 migrations apply <db> --local` / `--remote`, which records applied migrations. After editing any migration file, re-apply it to a fresh local database and check that the expected statements actually ran. ORM standard: `orm.md`.

## Testing Workers with Vitest

Workers projects use **Vitest `^4.1`** with `@cloudflare/vitest-pool-workers` (0.22 peers `vitest ^4.1`; Vitest 5 is not supported by the pool yet). Since the Vitest 4 release of the pool, options live in the `cloudflareTest()` Vite plugin; `defineWorkersConfig` and `test.poolOptions.workers` are gone.

```typescript
// vitest.config.ts
import { cloudflareTest } from '@cloudflare/vitest-pool-workers';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [
    cloudflareTest({
      main: './src/index.ts',
      wrangler: { configPath: './wrangler.jsonc' },
      miniflare: {
        bindings: { ENVIRONMENT: 'test' },
      },
    }),
  ],
  test: {
    include: ['src/**/*.test.ts'],
  },
});
```

```typescript
// src/index.test.ts
import { env } from 'cloudflare:test';
import { describe, expect, it } from 'vitest';
import app from './index';

describe('GET /health', () => {
  it('returns ok with the configured environment', async () => {
    const res = await app.request('/health', {}, env);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ status: 'ok', environment: 'test' });
  });
});
```

Add `@cloudflare/vitest-pool-workers/types` to `compilerOptions.types` for the `cloudflare:test` module. The Wrangler config's `compatibility_date` must not be newer than the date the installed `workerd` supports, or the pool fails to start ("requires compatibility date … newest date supported"); upgrade the pool or use an earlier date. Each test file gets its own isolated Worker and storage. Coverage: the Workers runtime has no Node inspector, so use `@vitest/coverage-istanbul` there and verify the report lists every owned file (`testing/vitest-patterns.md`). Upgrading an older config: the package ships a `codemods/vitest-v3-to-v4` codemod.

In agent sessions that run several test processes in parallel, stale `workerd` processes can accumulate; see `testing/ai-testing-protocols.md`.
