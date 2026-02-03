# Cloudflare Developer Platform Reference

Complete reference for Cloudflare Workers and Developer Platform integration with the Ironclad Stack.

**Core Principle:** *Edge-first, JavaScript-native, globally distributed.*

---

## Platform Overview

| Service | Purpose | Ironclad Stack Integration |
|---------|---------|---------------------------|
| **Workers** | Serverless compute (V8 isolates) | Hono + tRPC |
| **Pages** | Static sites + edge functions | Astro, Next.js, SPAs |
| **D1** | SQLite at the edge | Drizzle (sqlite-core + d1 adapter) |
| **KV** | Key-value storage | Sessions, cache, feature flags |
| **R2** | Object storage (S3-compatible) | File uploads, assets |
| **Hyperdrive** | Connection pooler for external DBs | Neon PostgreSQL |
| **Queues** | Message queues | Background jobs |
| **Durable Objects** | Stateful edge compute | Real-time, coordination |
| **Workers AI** | ML inference at edge | AI features |

---

## Wrangler CLI Complete Reference

### Installation & Authentication

```bash
# Install globally
pnpm add -g wrangler

# Or per-project (recommended)
pnpm add -D wrangler

# Login (opens browser)
wrangler login

# Check authentication
wrangler whoami
```

### Authentication with Scoped API Tokens

When using scoped Cloudflare API tokens (recommended for security), wrangler may fail with:
```
A request to the Cloudflare API (/memberships) failed - Unable to authenticate request
```

**Cause:** Wrangler calls `/memberships` to auto-discover accounts, but narrowly-scoped tokens don't have this permission.

**Solution:** Provide `CLOUDFLARE_ACCOUNT_ID` explicitly to bypass the lookup:

```bash
# Required env vars for scoped tokens
export CLOUDFLARE_API_TOKEN="your-scoped-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"

# Now wrangler commands work
pnpm exec wrangler deploy
pnpm exec wrangler secret put SECRET_NAME
pnpm exec wrangler kv key put --namespace-id=xxx key value
```

**With 1Password:**
```bash
# Using 1Password CLI for secure token retrieval
CLOUDFLARE_API_TOKEN=$(op read "op://<vault>/<item>/API Token" --account <your-account>.1password.com) \
CLOUDFLARE_ACCOUNT_ID="<your-account-id>" \
pnpm exec wrangler deploy
```

**Token Permission Requirements:**
| Permission | Wrangler Commands |
|------------|-------------------|
| Workers Scripts: Edit | deploy, publish |
| Workers KV Storage: Edit | kv namespace/key operations |
| Workers R2 Storage: Edit | r2 bucket/object operations |
| D1: Edit | d1 database operations |
| User Memberships: Read | Auto-discover accounts (optional if ACCOUNT_ID set) |

**Best Practice:** Use narrowly-scoped tokens + explicit `CLOUDFLARE_ACCOUNT_ID` rather than broad permissions.

### Project Commands

```bash
# Initialize new project
wrangler init my-project
wrangler init my-project --type worker    # Worker only
wrangler init my-project --type pages     # Pages project

# Development (local with Miniflare)
wrangler dev                              # Start local dev server
wrangler dev --remote                     # Dev against production bindings
wrangler dev --local                      # Force local-only (default)
wrangler dev --port 8787                  # Custom port
wrangler dev --inspector-port 9229        # Debugger port

# Deploy (ALWAYS use --env flag when multiple environments defined)
wrangler deploy --env=""                  # Deploy to top-level (production)
wrangler deploy --env staging             # Deploy to staging environment
wrangler deploy --dry-run                 # Show what would deploy

# WARNING: If wrangler.toml has [env.xxx] sections, running `wrangler deploy`
# without --env will show a warning about unspecified environment.
# Best practice: Always use explicit --env flag to avoid accidental deploys.

# Logs
wrangler tail                             # Live logs (production)
wrangler tail --format pretty             # Formatted output
wrangler tail --status error              # Filter by status
wrangler tail --search "user"             # Filter by content

# Versions & Rollback
wrangler versions list                    # List deployed versions
wrangler versions upload                  # Upload without activating
wrangler rollback                         # Rollback to previous
```

### D1 Database Commands

```bash
# Create database
wrangler d1 create my-db                  # Create new D1 database
wrangler d1 list                          # List all databases
wrangler d1 info my-db                    # Database info

# Execute SQL
wrangler d1 execute my-db --local --command="SELECT * FROM users"
wrangler d1 execute my-db --remote --command="SELECT * FROM users"

# Run migration files
wrangler d1 execute my-db --local --file=./drizzle/0001_init.sql
wrangler d1 execute my-db --remote --file=./drizzle/0001_init.sql

# Migrations (Wrangler native - alternative to drizzle-kit)
wrangler d1 migrations list my-db
wrangler d1 migrations apply my-db --local
wrangler d1 migrations apply my-db --remote

# Backup & Export
wrangler d1 export my-db --output=backup.sql
wrangler d1 time-travel my-db --timestamp="2024-01-01T00:00:00Z"
```

### KV Commands

```bash
# Namespace management
wrangler kv namespace create MY_KV        # Create namespace
wrangler kv namespace list                # List namespaces
wrangler kv namespace delete --namespace-id=xxx

# Key operations
wrangler kv key put --binding=MY_KV "key" "value"
wrangler kv key put --binding=MY_KV "key" --path=./file.txt
wrangler kv key get --binding=MY_KV "key"
wrangler kv key delete --binding=MY_KV "key"
wrangler kv key list --binding=MY_KV
wrangler kv key list --binding=MY_KV --prefix="user:"

# Bulk operations
wrangler kv bulk put --binding=MY_KV ./data.json
wrangler kv bulk delete --binding=MY_KV ./keys.json
```

### R2 Commands

```bash
# Bucket management
wrangler r2 bucket create my-bucket
wrangler r2 bucket list
wrangler r2 bucket delete my-bucket

# Object operations
wrangler r2 object put my-bucket/path/file.txt --file=./local.txt
wrangler r2 object get my-bucket/path/file.txt
wrangler r2 object delete my-bucket/path/file.txt
wrangler r2 object list my-bucket --prefix="uploads/"
```

### Secrets Commands

```bash
# Set secrets (prompts for value - never in command history)
wrangler secret put API_KEY
wrangler secret put JWT_SECRET
wrangler secret put DATABASE_URL

# Bulk secrets from file
wrangler secret bulk < secrets.json

# List & delete
wrangler secret list
wrangler secret delete API_KEY
```

### Pages Commands

```bash
# Deploy static site
wrangler pages deploy dist                # Deploy dist folder
wrangler pages deploy dist --project-name=my-site

# Project management
wrangler pages project create my-site
wrangler pages project list
wrangler pages deployment list --project-name=my-site

# Functions (in pages/functions/)
# Automatically deployed with wrangler pages deploy
```

### Queues Commands

```bash
# Queue management
wrangler queues create my-queue
wrangler queues list
wrangler queues delete my-queue

# Consumer management
wrangler queues consumer add my-queue my-worker
wrangler queues consumer remove my-queue my-worker
```

### Hyperdrive Commands

```bash
# Create connection to external database
wrangler hyperdrive create my-hyperdrive \
  --connection-string="postgres://user:pass@host:5432/db"

# List & manage
wrangler hyperdrive list
wrangler hyperdrive get my-hyperdrive
wrangler hyperdrive update my-hyperdrive --connection-string="..."
wrangler hyperdrive delete my-hyperdrive
```

---

## Workers Runtime

### V8 Isolates vs Node.js

Workers run on V8 isolates, NOT Node.js. Critical differences:

| Capability | Node.js | Workers | Workaround |
|------------|---------|---------|------------|
| File system (`fs`) | ✅ | ❌ | Use R2 or KV |
| `child_process` | ✅ | ❌ | Use Queues or Service Bindings |
| Native bindings | ✅ | ❌ | Pure JS alternatives only |
| `process.env` | ✅ | ❌ | Use env bindings |
| TCP sockets | ✅ | ❌ | Use Hyperdrive, fetch |
| Execution time | Unlimited | 30s-60s | Durable Objects for long-running |
| Memory | GB+ | 128MB | Stream large data |
| `crypto` | Full Node | Web Crypto | Use Web Crypto API |
| `Buffer` | ✅ | ⚠️ | Use with nodejs_compat |

### nodejs_compat Flag

Enable partial Node.js compatibility:

```toml
# wrangler.toml
compatibility_flags = ["nodejs_compat"]
```

**What it enables:**
- `Buffer` global
- `process.env` (empty by default)
- `crypto` (mapped to Web Crypto)
- `util` (partial)
- `events` (EventEmitter)
- `stream` (partial)
- `assert`
- `path`
- `url`
- `string_decoder`
- `querystring`

**What it does NOT enable:**
- `fs` - Use R2/KV
- `child_process` - Use Queues
- `net` / `dgram` - Use fetch/Hyperdrive
- `cluster` - N/A (edge distribution)
- Native addons - Pure JS only

### Execution Limits

| Plan | CPU Time | Duration | Memory | Subrequests |
|------|----------|----------|--------|-------------|
| Free | 10ms | 30s | 128MB | 50/request |
| Paid | 30s CPU | 30s wall | 128MB | 1000/request |
| Unbound | 30s CPU | No limit | 128MB | 1000/request |

**Tips:**
- CPU time ≠ wall time (I/O doesn't count)
- Use streaming for large responses
- Durable Objects for long-running tasks

### Web Crypto API

Workers use the Web Crypto API, not Node's `crypto`:

```typescript
// Generate UUID
const id = crypto.randomUUID();

// Random bytes
const bytes = new Uint8Array(32);
crypto.getRandomValues(bytes);

// Hashing
const encoder = new TextEncoder();
const data = encoder.encode('hello world');
const hashBuffer = await crypto.subtle.digest('SHA-256', data);
const hashArray = Array.from(new Uint8Array(hashBuffer));
const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

// HMAC
const key = await crypto.subtle.importKey(
  'raw',
  encoder.encode(secret),
  { name: 'HMAC', hash: 'SHA-256' },
  false,
  ['sign', 'verify']
);
const signature = await crypto.subtle.sign('HMAC', key, data);

// JWT signing (use jose library for convenience)
import { SignJWT, jwtVerify } from 'jose';

const token = await new SignJWT({ sub: userId })
  .setProtectedHeader({ alg: 'HS256' })
  .setExpirationTime('2h')
  .sign(encoder.encode(secret));
```

**Recommended library:** `jose` for JWT (pure JS, Workers-compatible)

```bash
pnpm add jose
```

---

## Hono on Workers

### Project Structure

```
my-api/
├── src/
│   ├── index.ts          # Entry point (Hono app export)
│   ├── env.ts            # Type-safe bindings
│   ├── db/
│   │   ├── index.ts      # Drizzle D1 setup
│   │   └── schema.ts     # Table definitions
│   ├── routes/
│   │   ├── index.ts      # Route aggregation
│   │   ├── users.ts      # User routes
│   │   └── auth.ts       # Auth routes
│   ├── middleware/
│   │   ├── auth.ts       # Auth middleware
│   │   └── rateLimit.ts  # Rate limiting
│   └── lib/
│       └── utils.ts      # Shared utilities
├── drizzle/              # Migration files
├── wrangler.toml         # Cloudflare config
├── drizzle.config.ts     # Drizzle Kit config
├── tsconfig.json
└── package.json
```

### Entry Point Pattern

```typescript
// src/index.ts
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { secureHeaders } from 'hono/secure-headers';
import { prettyJSON } from 'hono/pretty-json';
import type { Bindings } from './env';
import { userRoutes } from './routes/users';
import { authRoutes } from './routes/auth';

// Create app with typed bindings
const app = new Hono<{ Bindings: Bindings }>();

// Global middleware
app.use('*', logger());
app.use('*', secureHeaders());
app.use('*', prettyJSON());
app.use('*', cors({
  origin: ['https://example.com', 'http://localhost:3000'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization'],
  exposeHeaders: ['X-Request-Id'],
  maxAge: 86400,
  credentials: true,
}));

// Health check
app.get('/health', (c) => c.json({ status: 'ok', timestamp: Date.now() }));

// Mount routes
app.route('/api/users', userRoutes);
app.route('/api/auth', authRoutes);

// 404 handler
app.notFound((c) => c.json({ error: 'Not found' }, 404));

// Error handler
app.onError((err, c) => {
  console.error('Unhandled error:', err);
  return c.json({
    error: 'Internal server error',
    message: c.env.ENVIRONMENT === 'development' ? err.message : undefined,
  }, 500);
});

// Export for Workers
export default app;
```

### Type-Safe Bindings

```typescript
// src/env.ts
export type Bindings = {
  // D1 Database
  DB: D1Database;

  // KV Namespace
  CACHE: KVNamespace;

  // R2 Bucket
  UPLOADS: R2Bucket;

  // Queues
  EMAIL_QUEUE: Queue<EmailMessage>;

  // Service Bindings
  AUTH_SERVICE: Fetcher;

  // Environment variables (from [vars] in wrangler.toml)
  ENVIRONMENT: 'development' | 'staging' | 'production';
  API_VERSION: string;

  // Secrets (from wrangler secret put)
  JWT_SECRET: string;
  API_KEY: string;
  STRIPE_SECRET_KEY: string;
};

// Type for queue messages
export interface EmailMessage {
  to: string;
  subject: string;
  body: string;
}
```

### Middleware Patterns

```typescript
// src/middleware/auth.ts
import { createMiddleware } from 'hono/factory';
import { HTTPException } from 'hono/http-exception';
import { jwtVerify } from 'jose';
import type { Bindings } from '../env';

// Context with user
export type AuthContext = {
  Bindings: Bindings;
  Variables: {
    userId: string;
    userEmail: string;
  };
};

export const authMiddleware = createMiddleware<AuthContext>(async (c, next) => {
  const authHeader = c.req.header('Authorization');

  if (!authHeader?.startsWith('Bearer ')) {
    throw new HTTPException(401, { message: 'Missing authorization header' });
  }

  const token = authHeader.slice(7);

  try {
    const secret = new TextEncoder().encode(c.env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);

    c.set('userId', payload.sub as string);
    c.set('userEmail', payload.email as string);

    await next();
  } catch {
    throw new HTTPException(401, { message: 'Invalid token' });
  }
});

// Usage in routes
import { authMiddleware } from '../middleware/auth';

const protectedRoutes = new Hono<AuthContext>();

protectedRoutes.use('*', authMiddleware);

protectedRoutes.get('/me', (c) => {
  return c.json({
    userId: c.get('userId'),
    email: c.get('userEmail'),
  });
});
```

### Rate Limiting (KV-based)

```typescript
// src/middleware/rateLimit.ts
import { createMiddleware } from 'hono/factory';
import { HTTPException } from 'hono/http-exception';
import type { Bindings } from '../env';

interface RateLimitOptions {
  windowMs: number;  // Time window in ms
  max: number;       // Max requests per window
}

export const rateLimit = (options: RateLimitOptions) => {
  return createMiddleware<{ Bindings: Bindings }>(async (c, next) => {
    const ip = c.req.header('CF-Connecting-IP') || 'unknown';
    const key = `ratelimit:${ip}`;

    const current = await c.env.CACHE.get(key);
    const count = current ? parseInt(current, 10) : 0;

    if (count >= options.max) {
      throw new HTTPException(429, { message: 'Too many requests' });
    }

    // Increment count
    await c.env.CACHE.put(key, String(count + 1), {
      expirationTtl: Math.ceil(options.windowMs / 1000),
    });

    c.header('X-RateLimit-Limit', String(options.max));
    c.header('X-RateLimit-Remaining', String(options.max - count - 1));

    await next();
  });
};

// Usage
app.use('/api/*', rateLimit({ windowMs: 60000, max: 100 }));
```

### Error Handling

```typescript
import { HTTPException } from 'hono/http-exception';

// Throw HTTP errors
app.get('/users/:id', async (c) => {
  const user = await getUser(c.req.param('id'));

  if (!user) {
    throw new HTTPException(404, { message: 'User not found' });
  }

  return c.json(user);
});

// Custom error with response
app.get('/protected', async (c) => {
  if (!authorized) {
    const errorResponse = new Response('Unauthorized', {
      status: 401,
      headers: { 'WWW-Authenticate': 'Bearer realm="api"' },
    });
    throw new HTTPException(401, { res: errorResponse });
  }
});

// Global error handler
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return err.getResponse();
  }

  // Log unexpected errors
  console.error('Unexpected error:', err);

  return c.json({
    error: 'Internal server error',
    requestId: c.req.header('CF-Ray'),
  }, 500);
});
```

### Response Helpers

```typescript
// JSON response
c.json({ data: users });
c.json({ data: user }, 201);

// Text response
c.text('Hello World');

// HTML response
c.html('<h1>Hello</h1>');

// Redirect
c.redirect('/new-location');
c.redirect('/new-location', 301);  // Permanent

// No content
c.body(null, 204);

// Stream response
c.stream(async (stream) => {
  for await (const chunk of asyncIterator) {
    await stream.write(chunk);
  }
});

// Custom response
return new Response(body, {
  status: 200,
  headers: { 'X-Custom': 'value' },
});
```

---

## D1 Database (SQLite at Edge)

### Setup with Drizzle

```bash
# Install dependencies
pnpm add drizzle-orm
pnpm add -D drizzle-kit
```

**wrangler.toml:**
```toml
name = "my-api"
main = "src/index.ts"
compatibility_date = "2024-12-01"
compatibility_flags = ["nodejs_compat"]

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**src/db/schema.ts:**
```typescript
import { sqliteTable, text, integer, real, blob } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

// Users table
export const users = sqliteTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  avatarUrl: text('avatar_url'),
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),
});

// Posts table with foreign key
export const posts = sqliteTable('posts', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  title: text('title').notNull(),
  content: text('content').notNull(),
  authorId: text('author_id').notNull().references(() => users.id),
  publishedAt: integer('published_at', { mode: 'timestamp' }),
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),
});

// Type exports
export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
export type Post = typeof posts.$inferSelect;
export type InsertPost = typeof posts.$inferInsert;
```

**src/db/index.ts:**
```typescript
import { drizzle } from 'drizzle-orm/d1';
import * as schema from './schema';

export const createDb = (d1: D1Database) => {
  return drizzle(d1, { schema });
};

export type Database = ReturnType<typeof createDb>;
export * from './schema';
```

**drizzle.config.ts:**
```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  driver: 'd1-http',
  dbCredentials: {
    accountId: process.env.CLOUDFLARE_ACCOUNT_ID!,
    databaseId: process.env.CLOUDFLARE_D1_ID!,
    token: process.env.CLOUDFLARE_API_TOKEN!,
  },
});
```

### Migration Workflow

```bash
# 1. Create database (once)
wrangler d1 create my-db
# Copy database_id to wrangler.toml

# 2. Generate migration from schema changes
pnpm drizzle-kit generate

# 3. Apply to local (Miniflare)
wrangler d1 execute my-db --local --file=./drizzle/0001_init.sql

# 4. Test locally
wrangler dev

# 5. Apply to production
wrangler d1 execute my-db --remote --file=./drizzle/0001_init.sql

# 6. Deploy
wrangler deploy
```

**package.json scripts:**
```json
{
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "db:generate": "drizzle-kit generate",
    "db:migrate:local": "wrangler d1 execute my-db --local --file=./drizzle/$(ls -t drizzle/*.sql | head -1)",
    "db:migrate:prod": "wrangler d1 execute my-db --remote --file=./drizzle/$(ls -t drizzle/*.sql | head -1)",
    "db:studio": "drizzle-kit studio"
  }
}
```

### Query Patterns

```typescript
import { eq, and, or, like, desc, asc, sql, count } from 'drizzle-orm';
import { createDb, users, posts } from './db';

// In route handler
app.get('/users', async (c) => {
  const db = createDb(c.env.DB);

  // Select all
  const allUsers = await db.select().from(users);

  // Select with filter
  const activeUsers = await db
    .select()
    .from(users)
    .where(eq(users.status, 'active'));

  // Select with multiple conditions
  const filtered = await db
    .select()
    .from(users)
    .where(and(
      eq(users.status, 'active'),
      like(users.email, '%@example.com')
    ));

  // Select with ordering and limit
  const recent = await db
    .select()
    .from(users)
    .orderBy(desc(users.createdAt))
    .limit(10);

  // Select specific columns
  const emails = await db
    .select({ email: users.email, name: users.name })
    .from(users);

  // Join
  const postsWithAuthors = await db
    .select({
      post: posts,
      author: users,
    })
    .from(posts)
    .leftJoin(users, eq(posts.authorId, users.id));

  // Count
  const [{ total }] = await db
    .select({ total: count() })
    .from(users);

  return c.json(allUsers);
});

// Insert
app.post('/users', async (c) => {
  const db = createDb(c.env.DB);
  const body = await c.req.json();

  const [user] = await db.insert(users).values({
    email: body.email,
    name: body.name,
  }).returning();

  return c.json(user, 201);
});

// Update
app.put('/users/:id', async (c) => {
  const db = createDb(c.env.DB);
  const id = c.req.param('id');
  const body = await c.req.json();

  const [user] = await db
    .update(users)
    .set({
      name: body.name,
      updatedAt: new Date(),
    })
    .where(eq(users.id, id))
    .returning();

  if (!user) {
    throw new HTTPException(404, { message: 'User not found' });
  }

  return c.json(user);
});

// Delete
app.delete('/users/:id', async (c) => {
  const db = createDb(c.env.DB);
  const id = c.req.param('id');

  await db.delete(users).where(eq(users.id, id));

  return c.body(null, 204);
});
```

### Batch Operations

```typescript
// Batch insert (more efficient)
await db.insert(users).values([
  { email: 'user1@example.com', name: 'User 1' },
  { email: 'user2@example.com', name: 'User 2' },
  { email: 'user3@example.com', name: 'User 3' },
]);

// D1 batch API (atomic)
const results = await c.env.DB.batch([
  c.env.DB.prepare('INSERT INTO users (id, email, name) VALUES (?, ?, ?)').bind(id1, email1, name1),
  c.env.DB.prepare('INSERT INTO users (id, email, name) VALUES (?, ?, ?)').bind(id2, email2, name2),
]);
```

### Local Development

```bash
wrangler dev
# Creates .wrangler/state/v3/d1/miniflare-D1DatabaseObject/
# SQLite files persist between restarts

# Query local database directly
wrangler d1 execute my-db --local --command="SELECT * FROM users"

# Reset local database
rm -rf .wrangler/state
```

---

## Storage Services

### KV (Key-Value)

**When to use:** Sessions, cache, feature flags, rate limiting, config.

**Characteristics:**
- Eventually consistent (may take 60s to propagate globally)
- Max key size: 512 bytes
- Max value size: 25MB
- Read-heavy workloads (cached at edge)

**wrangler.toml:**
```toml
[[kv_namespaces]]
binding = "CACHE"
id = "xxxxxxxx"
```

**Usage patterns:**
```typescript
// Simple get/put
const value = await c.env.CACHE.get('key');
await c.env.CACHE.put('key', 'value');

// With TTL (seconds)
await c.env.CACHE.put('session:123', JSON.stringify(session), {
  expirationTtl: 3600,  // 1 hour
});

// With absolute expiration
await c.env.CACHE.put('temp:123', 'data', {
  expiration: Math.floor(Date.now() / 1000) + 3600,
});

// JSON storage
await c.env.CACHE.put('user:123', JSON.stringify(user));
const user = await c.env.CACHE.get('user:123', 'json');

// With metadata
await c.env.CACHE.put('doc:123', content, {
  metadata: { contentType: 'text/html', author: 'john' },
});
const { value, metadata } = await c.env.CACHE.getWithMetadata('doc:123');

// Delete
await c.env.CACHE.delete('key');

// List keys
const keys = await c.env.CACHE.list({ prefix: 'user:', limit: 100 });
for (const key of keys.keys) {
  console.log(key.name, key.expiration, key.metadata);
}
```

### R2 (Object Storage)

**When to use:** File uploads, images, documents, large binary data.

**Characteristics:**
- S3-compatible API
- No egress fees
- Max object size: 5TB
- Strong consistency

**wrangler.toml:**
```toml
[[r2_buckets]]
binding = "UPLOADS"
bucket_name = "my-uploads"
```

**Usage patterns:**
```typescript
// Upload
app.post('/upload', async (c) => {
  const formData = await c.req.formData();
  const file = formData.get('file') as File;

  const key = `uploads/${crypto.randomUUID()}/${file.name}`;

  await c.env.UPLOADS.put(key, file.stream(), {
    httpMetadata: {
      contentType: file.type,
    },
    customMetadata: {
      originalName: file.name,
      uploadedBy: c.get('userId'),
    },
  });

  return c.json({ key });
});

// Download
app.get('/files/:key{.+}', async (c) => {
  const key = c.req.param('key');
  const object = await c.env.UPLOADS.get(key);

  if (!object) {
    throw new HTTPException(404, { message: 'File not found' });
  }

  return new Response(object.body, {
    headers: {
      'Content-Type': object.httpMetadata?.contentType || 'application/octet-stream',
      'Content-Length': String(object.size),
      'ETag': object.etag,
    },
  });
});

// List objects
const objects = await c.env.UPLOADS.list({
  prefix: 'uploads/',
  limit: 100,
  cursor: previousCursor,
});

// Delete
await c.env.UPLOADS.delete(key);

// Head (metadata only)
const head = await c.env.UPLOADS.head(key);
```

**Presigned URLs (for direct upload):**
```typescript
// Using aws4fetch for S3-compatible signing
import { AwsClient } from 'aws4fetch';

app.get('/presigned-url', async (c) => {
  const r2 = new AwsClient({
    accessKeyId: c.env.R2_ACCESS_KEY_ID,
    secretAccessKey: c.env.R2_SECRET_ACCESS_KEY,
  });

  const key = `uploads/${crypto.randomUUID()}`;
  const url = `https://${c.env.ACCOUNT_ID}.r2.cloudflarestorage.com/my-uploads/${key}`;

  const signedRequest = await r2.sign(new Request(url, { method: 'PUT' }), {
    aws: { signQuery: true },
  });

  return c.json({ uploadUrl: signedRequest.url, key });
});
```

### D1 vs KV vs R2 Decision Matrix

| Need | Use | Why |
|------|-----|-----|
| Relational queries | D1 | SQL, joins, indexes |
| Simple key lookup | KV | Fast, cached at edge |
| Session storage | KV | TTL support, fast reads |
| File storage | R2 | Large objects, streaming |
| Cache | KV | Automatic edge caching |
| User data | D1 | Structured, queryable |
| Feature flags | KV | Simple, fast |
| Audit logs | D1 | Queryable history |
| Media files | R2 | Large, streamable |

---

## Advanced Services

### Queues (Background Jobs)

**wrangler.toml:**
```toml
[[queues.producers]]
binding = "EMAIL_QUEUE"
queue = "email-queue"

[[queues.consumers]]
queue = "email-queue"
max_batch_size = 10
max_batch_timeout = 30
```

**Producer (send messages):**
```typescript
// src/index.ts
app.post('/send-email', async (c) => {
  const { to, subject, body } = await c.req.json();

  await c.env.EMAIL_QUEUE.send({
    to,
    subject,
    body,
    timestamp: Date.now(),
  });

  return c.json({ status: 'queued' });
});
```

**Consumer (process messages):**
```typescript
// src/index.ts
export default {
  // HTTP handler
  fetch: app.fetch,

  // Queue consumer
  async queue(batch: MessageBatch<EmailMessage>, env: Bindings): Promise<void> {
    for (const message of batch.messages) {
      try {
        await sendEmail(message.body);
        message.ack();
      } catch (error) {
        console.error('Failed to send email:', error);
        message.retry();
      }
    }
  },
};
```

### Scheduled Workers (Cron)

**wrangler.toml:**
```toml
[triggers]
crons = [
  "0 * * * *",      # Every hour
  "0 0 * * *",      # Daily at midnight
  "*/5 * * * *",    # Every 5 minutes
]
```

**Handler:**
```typescript
export default {
  fetch: app.fetch,

  async scheduled(event: ScheduledEvent, env: Bindings, ctx: ExecutionContext) {
    switch (event.cron) {
      case '0 * * * *':
        await hourlyCleanup(env);
        break;
      case '0 0 * * *':
        await dailyReport(env);
        break;
    }
  },
};
```

### Durable Objects (Stateful Edge)

**When to use:** Real-time collaboration, rate limiting, WebSocket coordination.

**wrangler.toml:**
```toml
[durable_objects]
bindings = [
  { name = "ROOMS", class_name = "ChatRoom" }
]

[[migrations]]
tag = "v1"
new_classes = ["ChatRoom"]
```

**Durable Object class:**
```typescript
// src/ChatRoom.ts
export class ChatRoom {
  private state: DurableObjectState;
  private connections: Set<WebSocket> = new Set();

  constructor(state: DurableObjectState) {
    this.state = state;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/websocket') {
      const pair = new WebSocketPair();
      await this.handleWebSocket(pair[1]);
      return new Response(null, { status: 101, webSocket: pair[0] });
    }

    return new Response('Not found', { status: 404 });
  }

  async handleWebSocket(ws: WebSocket) {
    ws.accept();
    this.connections.add(ws);

    ws.addEventListener('message', (event) => {
      // Broadcast to all connections
      for (const conn of this.connections) {
        if (conn !== ws) {
          conn.send(event.data);
        }
      }
    });

    ws.addEventListener('close', () => {
      this.connections.delete(ws);
    });
  }
}
```

**Usage in Worker:**
```typescript
app.get('/room/:id/websocket', async (c) => {
  const id = c.env.ROOMS.idFromName(c.req.param('id'));
  const room = c.env.ROOMS.get(id);
  return room.fetch(c.req.raw);
});
```

### Hyperdrive (External Database Pooling)

**When D1 isn't enough:** Complex queries, existing Postgres, large datasets.

**wrangler.toml:**
```toml
[[hyperdrive]]
binding = "HYPERDRIVE"
id = "xxxxxxxx"
```

**Usage with Drizzle:**
```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

app.get('/data', async (c) => {
  // Hyperdrive provides pooled connection string
  const sql = postgres(c.env.HYPERDRIVE.connectionString);
  const db = drizzle(sql);

  const result = await db.select().from(users);
  return c.json(result);
});
```

### Service Bindings (Worker-to-Worker)

**wrangler.toml:**
```toml
[[services]]
binding = "AUTH_SERVICE"
service = "auth-worker"
```

**Usage:**
```typescript
app.get('/protected', async (c) => {
  // Call another Worker directly (no network hop)
  const authResponse = await c.env.AUTH_SERVICE.fetch(
    new Request('https://auth/verify', {
      headers: { Authorization: c.req.header('Authorization')! },
    })
  );

  if (!authResponse.ok) {
    throw new HTTPException(401, { message: 'Unauthorized' });
  }

  const user = await authResponse.json();
  // Continue with user context
});
```

---

## Pages

### Static Sites

```bash
# Build your site (React, Vue, etc.)
pnpm build

# Deploy
wrangler pages deploy dist
```

### With Functions (API Routes)

```
my-site/
├── src/              # Frontend source
├── functions/        # Edge functions
│   ├── api/
│   │   ├── hello.ts  # GET /api/hello
│   │   └── users/
│   │       └── [id].ts  # GET /api/users/:id
│   └── _middleware.ts   # Runs on all routes
├── dist/             # Build output
└── wrangler.toml
```

**functions/api/hello.ts:**
```typescript
export const onRequest: PagesFunction = async (context) => {
  return Response.json({ message: 'Hello from the edge!' });
};
```

**functions/_middleware.ts:**
```typescript
export const onRequest: PagesFunction = async (context) => {
  // Add CORS headers
  const response = await context.next();
  response.headers.set('Access-Control-Allow-Origin', '*');
  return response;
};
```

### Framework Adapters

**Astro:**
```bash
pnpm add @astrojs/cloudflare
```

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  adapter: cloudflare(),
});
```

**Next.js:**
```bash
pnpm add @cloudflare/next-on-pages
```

```bash
# Build
npx @cloudflare/next-on-pages

# Deploy
wrangler pages deploy .vercel/output/static
```

---

## Debugging & Monitoring

### Local Development

```bash
# Start dev server
wrangler dev

# With inspector (Chrome DevTools)
wrangler dev --inspector-port 9229
# Open chrome://inspect in Chrome

# Force remote bindings
wrangler dev --remote
```

### Live Logs

```bash
# Stream production logs
wrangler tail

# Filter by status
wrangler tail --status error
wrangler tail --status ok

# Filter by content
wrangler tail --search "userId"

# Format options
wrangler tail --format pretty
wrangler tail --format json

# Sample rate (high-traffic workers)
wrangler tail --sampling-rate 0.1
```

### Logging Best Practices

```typescript
// Structured logging
console.log(JSON.stringify({
  level: 'info',
  message: 'User created',
  userId: user.id,
  timestamp: Date.now(),
  requestId: c.req.header('CF-Ray'),
}));

// Error logging
console.error(JSON.stringify({
  level: 'error',
  message: 'Database error',
  error: error.message,
  stack: error.stack,
  requestId: c.req.header('CF-Ray'),
}));
```

### Request Tracing

```typescript
// Add request ID to all responses
app.use('*', async (c, next) => {
  const requestId = c.req.header('CF-Ray') || crypto.randomUUID();
  c.header('X-Request-Id', requestId);

  const start = Date.now();
  await next();
  const duration = Date.now() - start;

  console.log(JSON.stringify({
    requestId,
    method: c.req.method,
    path: c.req.path,
    status: c.res.status,
    duration,
  }));
});
```

---

## Decision Matrices

### Workers vs Pages

| Requirement | Use |
|-------------|-----|
| Pure API (no frontend) | Workers |
| Static site + API | Pages (with Functions) |
| SPA with API | Pages (with Functions) |
| SSR framework (Astro, Next) | Pages |
| WebSocket server | Workers |
| Cron jobs | Workers |

### D1 vs Hyperdrive + Neon

| Requirement | Use |
|-------------|-----|
| Simple schemas | D1 |
| Edge latency critical | D1 |
| < 10GB data | D1 |
| Complex queries (CTEs, window functions) | Hyperdrive |
| Existing Postgres | Hyperdrive |
| Full-text search | Hyperdrive (or external) |
| Write-heavy | Hyperdrive |

### When to NOT Use Workers

| Scenario | Use Instead |
|----------|-------------|
| MCP servers (stdio) | Node.js + tsup |
| CLI tools | Node.js + tsup |
| Obsidian plugins | Electron (esbuild) |
| Long-running processes (> 30s) | Self-hosted |
| Native bindings required | Self-hosted |
| Private internal tools | Self-hosted + Tailscale |

---

## Environment Setup

### .dev.vars (Local Secrets)

```bash
# .dev.vars (gitignored)
JWT_SECRET=dev-secret-123
API_KEY=dev-api-key
STRIPE_SECRET_KEY=sk_test_xxx
```

### Environment-Specific Config

**wrangler.toml:**
```toml
name = "my-api"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[vars]
ENVIRONMENT = "production"

[env.staging]
name = "my-api-staging"
[env.staging.vars]
ENVIRONMENT = "staging"

[env.development]
name = "my-api-dev"
[env.development.vars]
ENVIRONMENT = "development"
```

```bash
wrangler deploy              # Production
wrangler deploy --env staging
wrangler dev --env development
```

### CRITICAL: wrangler.toml Environment Inheritance

**When deploying with `wrangler deploy --env <environment>`, BINDINGS are NOT inherited from the top-level configuration.**

#### NOT Inherited (must define per-environment):
- `[[kv_namespaces]]` → Must define `[[env.production.kv_namespaces]]`
- `[[d1_databases]]` → Must define `[[env.production.d1_databases]]`
- `[[r2_buckets]]` → Must define `[[env.production.r2_buckets]]`
- `[vars]` → Must define `[env.production.vars]`

#### IS Inherited (do NOT define per-environment):
- `[assets]` → Top-level config applies to all environments
- `[observability]` → Inherited
- `compatibility_date` → Inherited

**WARNING:** Do NOT add `[env.production.assets]` - this syntax causes SPA routing to fail!

#### Multi-Environment Pattern

```toml
# TOP-LEVEL CONFIG
# - Assets config: inherited by all environments
# - Bindings: NOT inherited, must define per-environment

[[kv_namespaces]]
binding = "ROUTES"
id = "xxx-production-id"
preview_id = "xxx-preview-id"

# Assets IS inherited - only define at top level!
[assets]
directory = "./dist"
binding = "ASSETS"
html_handling = "force-trailing-slash"
not_found_handling = "single-page-application"

[vars]
ENVIRONMENT = "production"
VERSION = "1.0.0"

# PRODUCTION ENVIRONMENT
# Bindings must be duplicated, but NOT [assets]!
[env.production]
name = "my-worker"

[env.production.vars]
ENVIRONMENT = "production"
VERSION = "1.0.0"

[[env.production.kv_namespaces]]
binding = "ROUTES"
id = "xxx-production-id"

[[env.production.d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxx-db-id"

[[env.production.r2_buckets]]
binding = "FILES_BUCKET"
bucket_name = "files"
```

#### Failure Symptoms

If bindings are missing from the environment section:
- `c.env.ROUTES` → `undefined` (KV operations fail)
- `c.env.DB` → `undefined` (D1 queries fail)
- `c.env.ASSETS` → `undefined` (Static assets fail with "Internal Server Error")
- `c.env.FILES_BUCKET` → `undefined` (R2 file serving fails)

---

## Quick Reference

### New Project Checklist

```bash
# 1. Initialize
mkdir my-api && cd my-api
pnpm init
pnpm add hono drizzle-orm zod
pnpm add -D wrangler drizzle-kit typescript @types/node

# 2. Create wrangler.toml
# 3. Create src/index.ts (Hono app)
# 4. Create src/db/schema.ts (Drizzle)
# 5. Create D1 database
wrangler d1 create my-db

# 6. Generate & apply migrations
pnpm drizzle-kit generate
wrangler d1 execute my-db --local --file=./drizzle/0001_init.sql

# 7. Dev & deploy
wrangler dev
wrangler deploy
```

### Common Patterns

```typescript
// Get client IP
const ip = c.req.header('CF-Connecting-IP');

// Get country
const country = c.req.header('CF-IPCountry');

// Get request ID
const requestId = c.req.header('CF-Ray');

// Check if bot
const isBot = c.req.header('CF-Bot-Score');

// Get city/region (Enterprise)
const city = c.req.header('CF-IPCity');
```

---

---

---

*Companion to: typescript-ironclad-stack.md, typescript-ironclad-infra.md*
*Last updated: 2026-02-03*
