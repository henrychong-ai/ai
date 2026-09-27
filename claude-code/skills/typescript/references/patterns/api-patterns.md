# API Development Patterns

Patterns for building type-safe APIs with Hono, tRPC, and REST/GraphQL.

> **Full Hono/Workers setup:** See `tech-stack/cloudflare.md` for complete Cloudflare Workers configuration.

> **Recommended default for back-end / back-to-front projects:** the **`@hono/zod-openapi` single-source pattern** (one `createRoute()` drives request+response validation, the generated OpenAPI doc, dashboard client types, and MCP tool schemas). Hono, tRPC, REST, and GraphQL all remain documented below, but for a Worker/API that owns the contract with a dashboard and/or MCP consuming its types, default to the single-source pattern — see "@hono/zod-openapi Single-Source Pattern (Recommended Default)". The architectural rationale and the back-to-front vs front-to-back boundary live in `tech-stack/typescript-ironclad-stack.md` → "The Option-B Back-to-Front Pattern (Recommended Default)".

---

## Hono Patterns

### Project Structure

```
src/
├── index.ts          # App entry, route mounting
├── routes/
│   ├── users.ts      # User routes
│   ├── orders.ts     # Order routes
│   └── index.ts      # Route aggregation
├── middleware/
│   ├── auth.ts       # Authentication
│   ├── validation.ts # Request validation
│   └── error.ts      # Error handling
├── services/
│   └── user-service.ts
├── db/
│   ├── schema.ts     # Drizzle schema
│   └── index.ts      # DB client
└── types.ts          # Shared types
```

### Type-Safe Routes

```typescript
// src/routes/users.ts
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import type { Bindings } from '../types';

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

const users = new Hono<{ Bindings: Bindings }>()
  .get('/', async (c) => {
    const users = await c.env.DB.prepare('SELECT * FROM users').all();
    return c.json(users.results);
  })
  .get('/:id', async (c) => {
    const id = c.req.param('id');
    const user = await getUserById(c.env.DB, id);

    if (!user) {
      return c.json({ error: 'User not found' }, 404);
    }

    return c.json(user);
  })
  .post('/', zValidator('json', CreateUserSchema), async (c) => {
    const input = c.req.valid('json');
    const user = await createUser(c.env.DB, input);
    return c.json(user, 201);
  });

export { users };
```

### Route Aggregation

```typescript
// src/routes/index.ts
import { Hono } from 'hono';
import { users } from './users';
import { orders } from './orders';
import type { Bindings } from '../types';

const api = new Hono<{ Bindings: Bindings }>()
  .route('/users', users)
  .route('/orders', orders);

export { api };

// src/index.ts
import { Hono } from 'hono';
import { api } from './routes';

const app = new Hono()
  .route('/api', api)
  .get('/health', (c) => c.json({ status: 'ok' }));

export default app;
```

### Middleware Patterns

```typescript
// Authentication middleware
import { createMiddleware } from 'hono/factory';
import { HTTPException } from 'hono/http-exception';

type AuthVariables = {
  userId: string;
  role: 'user' | 'admin';
};

export const auth = createMiddleware<{
  Bindings: Bindings;
  Variables: AuthVariables;
}>(async (c, next) => {
  const token = c.req.header('Authorization')?.replace('Bearer ', '');

  if (!token) {
    throw new HTTPException(401, { message: 'Missing token' });
  }

  try {
    const payload = await verifyToken(token, c.env.JWT_SECRET);
    c.set('userId', payload.sub);
    c.set('role', payload.role);
    await next();
  } catch {
    throw new HTTPException(401, { message: 'Invalid token' });
  }
});

// Usage
app.use('/api/*', auth);
app.get('/api/me', (c) => {
  const userId = c.get('userId'); // Type-safe!
  return c.json({ userId });
});
```

### Response Immutability with Workers Static Assets

**CRITICAL:** When using Cloudflare Workers Static Assets (`ASSETS.fetch()`), the returned Response object has **immutable headers**. Middleware that modifies response headers (e.g., `secureHeaders()`, CORS) will fail silently or throw errors.

**Symptoms:**
- Headers not being added to responses
- `TypeError: Cannot modify read-only property` errors
- Middleware appears to run but has no effect

**Root Cause:** `ASSETS.fetch()` returns a Response from the static asset handler that cannot be modified. This applies even with `run_worker_first = true` in `wrangler.toml`.

**Fix Pattern:** Create a new Response with mutable headers by copying the original:

```typescript
// src/index.ts - Handling static assets with mutable headers
import { Hono } from 'hono';
import { secureHeaders } from 'hono/secure-headers';

type Bindings = {
  ASSETS: Fetcher;
  // ... other bindings
};

const app = new Hono<{ Bindings: Bindings }>();

// Apply security headers middleware
app.use('*', secureHeaders());

// Serve static assets with mutable headers
app.get('*', async (c) => {
  const assetResponse = await c.env.ASSETS.fetch(c.req.raw);

  // CRITICAL: Create new Response with mutable headers
  // Original assetResponse has immutable headers
  return new Response(assetResponse.body, {
    status: assetResponse.status,
    statusText: assetResponse.statusText,
    headers: new Headers(assetResponse.headers), // Mutable copy
  });
});

export default app;
```

**Alternative Approaches:**

1. **Separate API and asset handling** - Apply header middleware only to API routes:
```typescript
// Only apply secureHeaders to API routes
app.use('/api/*', secureHeaders());

// Assets served without modification
app.get('*', (c) => c.env.ASSETS.fetch(c.req.raw));
```

2. **Add headers manually** - For specific headers without middleware:
```typescript
app.get('*', async (c) => {
  const response = await c.env.ASSETS.fetch(c.req.raw);
  const mutableResponse = new Response(response.body, {
    status: response.status,
    headers: new Headers(response.headers),
  });
  mutableResponse.headers.set('X-Custom-Header', 'value');
  return mutableResponse;
});
```

**Rule:** treat every `ASSETS.fetch()` response as immutable. Any middleware that sets headers after `await next()` (e.g. `secureHeaders()`, CORS, custom headers) must receive a mutable copy (`new Response(body, { headers: new Headers(...) })`), or the header change fails silently or throws at runtime.

### Error Handling

```typescript
// src/middleware/error.ts
import { Hono } from 'hono';
import { HTTPException } from 'hono/http-exception';
import { ZodError } from 'zod';

export function setupErrorHandling(app: Hono) {
  app.onError((error, c) => {
    console.error(error);

    if (error instanceof HTTPException) {
      return c.json(
        { error: error.message },
        error.status
      );
    }

    if (error instanceof ZodError) {
      return c.json(
        { error: 'Validation failed', details: error.flatten() },
        400
      );
    }

    return c.json(
      { error: 'Internal server error' },
      500
    );
  });

  app.notFound((c) => {
    return c.json({ error: 'Not found' }, 404);
  });
}
```

---

## tRPC Patterns

### Router Setup

```typescript
// src/trpc/router.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { z } from 'zod';

type Context = {
  db: Database;
  userId?: string;
};

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;

// Authenticated procedure
export const protectedProcedure = t.procedure.use(async ({ ctx, next }) => {
  if (!ctx.userId) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({ ctx: { ...ctx, userId: ctx.userId } });
});
```

### Procedure Definitions

```typescript
// src/trpc/routers/users.ts
import { z } from 'zod';
import { router, publicProcedure, protectedProcedure } from '../router';

export const usersRouter = router({
  // Public: get user by ID
  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const user = await ctx.db.users.findById(input.id);
      if (!user) {
        throw new TRPCError({ code: 'NOT_FOUND' });
      }
      return user;
    }),

  // Protected: update own profile
  updateProfile: protectedProcedure
    .input(z.object({
      name: z.string().min(1).optional(),
      email: z.string().email().optional(),
    }))
    .mutation(async ({ ctx, input }) => {
      return ctx.db.users.update(ctx.userId, input);
    }),

  // Protected: list users (admin only)
  list: protectedProcedure
    .input(z.object({
      limit: z.number().min(1).max(100).default(20),
      cursor: z.string().optional(),
    }))
    .query(async ({ ctx, input }) => {
      const users = await ctx.db.users.list(input);
      return {
        items: users,
        nextCursor: users.length === input.limit
          ? users[users.length - 1].id
          : undefined,
      };
    }),
});
```

### Root Router

```typescript
// src/trpc/index.ts
import { router } from './router';
import { usersRouter } from './routers/users';
import { ordersRouter } from './routers/orders';

export const appRouter = router({
  users: usersRouter,
  orders: ordersRouter,
});

export type AppRouter = typeof appRouter;
```

### Hono + tRPC Integration

```typescript
// src/index.ts
import { Hono } from 'hono';
import { trpcServer } from '@hono/trpc-server';
import { appRouter } from './trpc';

const app = new Hono();

app.use('/trpc/*', trpcServer({
  router: appRouter,
  createContext: (opts) => ({
    db: opts.env.DB,
    userId: opts.req.header('x-user-id'),
  }),
}));

export default app;
```

### Client Usage

```typescript
// client/src/lib/trpc.ts
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '../../../server/src/trpc';

export const trpc = createTRPCReact<AppRouter>();

// Usage in component
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading } = trpc.users.getById.useQuery({ id: userId });

  const updateMutation = trpc.users.updateProfile.useMutation({
    onSuccess: () => {
      // Invalidate and refetch
    },
  });

  if (isLoading) return <Loading />;
  if (!data) return <NotFound />;

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      updateMutation.mutate({ name: newName });
    }}>
      <input defaultValue={data.name} />
    </form>
  );
}
```

---

## REST API Patterns

### Response Envelope

```typescript
type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string; code: string; details?: unknown };

function success<T>(data: T): ApiResponse<T> {
  return { success: true, data };
}

function error(message: string, code: string, details?: unknown): ApiResponse<never> {
  return { success: false, error: message, code, details };
}

// Usage
app.get('/users/:id', async (c) => {
  const user = await getUser(c.req.param('id'));
  if (!user) {
    return c.json(error('User not found', 'NOT_FOUND'), 404);
  }
  return c.json(success(user));
});
```

### Pagination

```typescript
// Cursor-based (preferred for large datasets)
type CursorPaginationParams = {
  cursor?: string;
  limit?: number;
};

type CursorPaginatedResponse<T> = {
  items: Array<T>;
  nextCursor?: string;
  hasMore: boolean;
};

async function paginateWithCursor<T extends { id: string }>(
  query: () => Promise<Array<T>>,
  params: CursorPaginationParams
): Promise<CursorPaginatedResponse<T>> {
  const limit = Math.min(params.limit ?? 20, 100);
  const items = await query();

  return {
    items: items.slice(0, limit),
    nextCursor: items.length > limit ? items[limit - 1].id : undefined,
    hasMore: items.length > limit,
  };
}

// Offset-based (simpler, but slower for large offsets)
type OffsetPaginationParams = {
  page?: number;
  limit?: number;
};

type OffsetPaginatedResponse<T> = {
  items: Array<T>;
  total: number;
  page: number;
  totalPages: number;
};
```

### Versioning

```typescript
// URL versioning (recommended)
const v1 = new Hono().route('/users', usersV1);
const v2 = new Hono().route('/users', usersV2);

app.route('/api/v1', v1);
app.route('/api/v2', v2);

// Header versioning
app.use('/api/*', async (c, next) => {
  const version = c.req.header('API-Version') ?? '1';
  c.set('apiVersion', version);
  await next();
});
```

### HTTP Status Codes

| Status | Use Case |
|--------|----------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid auth) |
| 403 | Forbidden (no permission) |
| 404 | Not Found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Unprocessable Entity (business logic error) |
| 500 | Internal Server Error |

---

## @hono/zod-openapi Single-Source Pattern (Recommended Default)

The recommended API approach for back-end / back-to-front projects. **One** shared Zod route definition (`createRoute()` + `.openapi()`) is the single source of truth for **all four** of: request+response validation, the generated OpenAPI doc, the dashboard/client types, and the MCP tool input schemas. Architectural rationale + the back-to-front vs front-to-back boundary: `tech-stack/typescript-ironclad-stack.md`.

`OpenAPIHono` **extends `Hono`** — adoption is an incremental, strangler-safe per-router conversion. Converted `.openapi()` routers mount alongside plain Hono routers on the same instance; `.route()` / `.use()` / `.onError()` / `.request()` all behave identically.

### Hono + Zod OpenAPI

```typescript
import { OpenAPIHono, createRoute, z } from '@hono/zod-openapi';

const app = new OpenAPIHono();

const getUserRoute = createRoute({
  method: 'get',
  path: '/users/{id}',
  request: {
    params: z.object({
      id: z.string().uuid().openapi({ example: '123e4567-e89b-12d3-a456-426614174000' }),
    }),
  },
  responses: {
    200: {
      content: {
        'application/json': {
          schema: UserSchema.openapi('User'),
        },
      },
      description: 'User found',
    },
    404: {
      content: {
        'application/json': {
          schema: ErrorSchema,
        },
      },
      description: 'User not found',
    },
  },
});

app.openapi(getUserRoute, async (c) => {
  const { id } = c.req.valid('param');
  const user = await getUser(id);
  if (!user) {
    return c.json({ error: 'Not found' }, 404);
  }
  return c.json(user, 200);
});

// Generate OpenAPI spec — the doc is GENERATED from the route registry, never hand-written.
// Self-heal info.version from the build VERSION so the doc never drifts behind the deploy.
app.doc('/openapi.json', {
  openapi: '3.0.0',
  info: { title: 'My API', version: VERSION },
});
```

The dashboard infers `z.input<typeof UserSchema>` (pre-default form shapes); Worker/MCP consumers infer `z.infer` / `z.output<typeof UserSchema>` (defaults applied). The MCP server's tool input schemas source the shared schema's `.shape`.

### Hard-Won Gotchas (codify — these bite without warning)

These surface during real per-router migrations to `@hono/zod-openapi`. Preserve each deliberately.

- **Funnel validation failures with `defaultHook`.** Request-validation failures otherwise return the library's raw 400 shape, not your error envelope. Set a `defaultHook` on the `OpenAPIHono` instance to convert them into your standard envelope. For a router with a bespoke legacy error body, the `defaultHook` can **return that exact `c.json(...)` body** to preserve it.

  ```typescript
  const app = new OpenAPIHono({
    defaultHook: (result, c) => {
      if (!result.success) {
        return c.json(apiError('VALIDATION_FAILED', result.error.issues), 400);
      }
    },
  });
  ```

- **Preserve auth-before-validation ordering.** Route-def request validation runs AFTER instance/mounted middleware but BEFORE the handler. If a handler relied on doing an auth/RBAC check before body validation, move that check into `createRoute({ middleware: [...] })` so it still runs first.

- **Repeated query keys become `string[]`.** The query validator surfaces `?x=a&x=b` as an array, which scalar schemas reject with a 400 — unlike `c.req.query()` first-value semantics. Wrap query objects in a `repeatTolerantQuery` preprocess (array → first element) to preserve the old behaviour.

  ```typescript
  const repeatTolerantQuery = <T extends z.ZodTypeAny>(schema: T) =>
    z.preprocess((v) => {
      if (v && typeof v === 'object') {
        const out: Record<string, unknown> = {};
        for (const [k, val] of Object.entries(v)) out[k] = Array.isArray(val) ? val[0] : val;
        return out;
      }
      return v;
    }, schema);
  ```

- **Keep `z.coerce` on MCP tool schemas.** MCP tool args may arrive as strings, so keep `z.coerce.number()` / `z.coerce.boolean()` on the shared tool schemas. Footgun to preserve deliberately: `z.coerce.boolean("false") === true` — coercion is truthiness-based, not string-value-based.

- **`.refine()` does NOT serialise to an OpenAPI `enum`.** An allow-list built with `.refine()` (e.g. a domain allow-list) loses its enum in the generated doc — and the doc feeds API Shield. Use `z.enum([...])`, or inject the enum onto the generated doc post-hoc.

- **Opaque content types can't be Zod-bound.** multipart/form-data uploads, binary / octet-stream, text/markdown, `204 No Content`, and slash-bearing path params (`:key{.+}` — an OpenAPI `{key}` param is single-segment and drops the `.+` match) cannot be route-def-validated. Keep these as plain-Hono methods on the same `OpenAPIHono` instance, and document them via `app.openAPIRegistry.registerPath()` so they still appear in the spec (required for API Shield parity).

- **Only requests are runtime-validated.** `@hono/zod-openapi` validates requests but only *documents* response schemas. Binding a response schema is therefore **zero-runtime-risk** — it drives the doc and the client types without adding a runtime failure mode.

### API Shield Integration (Cloudflare)

The *generated* OpenAPI doc feeds **Cloudflare API Shield** schema validation in **BLOCK mode** on the zone. This makes spec freshness a production concern, not a docs nicety:

- **A path absent from the uploaded spec 403s ALL traffic to it.** Dropping a path from the generated doc is an outage. (This is why opaque-content-type routes must still be `registerPath()`-documented.)
- Gate the spec upload inside each environment's deploy step, uploading the schema for **that environment's host**, then sync the schema's operations into **Endpoint Management** — API Shield validates only managed operations, so a schema upload alone leaves unmanaged paths silently unvalidated.

Two guards protect this:

1. **Parity test** — the generated doc must be a *superset* of a committed baseline of live operations, so no path is silently dropped.
2. **Freshness gate** — wired into `pnpm run check`: the committed spec must equal the generator output. CI fails on drift, forcing the spec to be regenerated and committed alongside any route change.

```jsonc
// package.json (excerpt) — freshness wired into the standard check gate
{
  "scripts": {
    "openapi:gen": "tsx scripts/generate-openapi.ts > openapi.json",
    "openapi:check": "tsx scripts/generate-openapi.ts | diff -q - openapi.json",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck && pnpm openapi:check && pnpm test"
  }
}
```

---

## Type-Safe Fetch Client

```typescript
type RequestConfig = {
  baseUrl: string;
  headers?: Record<string, string>;
};

type FetchOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
};

function createApiClient(config: RequestConfig) {
  async function request<T>(
    path: string,
    options: FetchOptions = {}
  ): Promise<T> {
    const response = await fetch(`${config.baseUrl}${path}`, {
      method: options.method ?? 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
        ...options.headers,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }

    return response.json();
  }

  return {
    get: <T>(path: string) => request<T>(path),
    post: <T>(path: string, body: unknown) =>
      request<T>(path, { method: 'POST', body }),
    put: <T>(path: string, body: unknown) =>
      request<T>(path, { method: 'PUT', body }),
    patch: <T>(path: string, body: unknown) =>
      request<T>(path, { method: 'PATCH', body }),
    delete: <T>(path: string) =>
      request<T>(path, { method: 'DELETE' }),
  };
}

// Usage
const api = createApiClient({ baseUrl: 'https://api.example.com' });

const user = await api.get<User>('/users/123');
const created = await api.post<User>('/users', { name: 'John' });
```

---

## Validation at Boundaries

### Request Validation

```typescript
import { zValidator } from '@hono/zod-validator';

// Validate body
app.post('/users', zValidator('json', CreateUserSchema), async (c) => {
  const input = c.req.valid('json'); // Typed!
  return c.json(await createUser(input));
});

// Validate query params
app.get('/users', zValidator('query', ListUsersSchema), async (c) => {
  const { page, limit } = c.req.valid('query');
  return c.json(await listUsers({ page, limit }));
});

// Validate path params
app.get('/users/:id', zValidator('param', z.object({ id: z.string().uuid() })), async (c) => {
  const { id } = c.req.valid('param');
  return c.json(await getUser(id));
});
```

### Response Validation (Optional)

```typescript
// Validate responses in development/testing
async function validateResponse<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): Promise<T> {
  if (process.env.NODE_ENV === 'development') {
    return schema.parse(data);
  }
  return data as T;
}
```

---

*Companion to: error-handling.md, async-patterns.md*
*See also: tech-stack/cloudflare.md for Hono/Workers setup; tech-stack/typescript-ironclad-stack.md for the Option-B back-to-front canonical definition*
*Last updated: 2026-06-05 (@hono/zod-openapi single-source promoted to recommended default; API Shield guards + migration gotchas added; de-repo pass 2026-09-28)*
