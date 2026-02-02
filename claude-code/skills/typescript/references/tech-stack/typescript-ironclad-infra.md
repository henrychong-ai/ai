# The Ironclad Infrastructure: Personal Deployment

Companion to the Ironclad Stack. Two deployment options: Cloudflare (primary) and Self-hosted (private).

**Core Principle:** *Cloudflare for everything public. Self-hosted for everything private.*

> **Comprehensive Cloudflare Reference:** See `cloudflare.md` for complete Wrangler CLI, Workers runtime details, Hono patterns, D1/Drizzle setup, and all Cloudflare services.

---

## The Two Stacks

| Stack | When to Use |
|-------|-------------|
| **Cloudflare** | APIs, websites, public services, edge compute |
| **Self-hosted (VPS2 + Tailscale)** | Private internal tools, admin dashboards |

```
Is it public-facing?
├─► YES → Cloudflare (Workers, Pages, D1)
└─► NO  → Self-hosted + Tailscale
```

---

## Stack 1: Cloudflare Developer Platform

### Platform Overview

| Service | Purpose | Ironclad Integration |
|---------|---------|---------------------|
| **Workers** | Serverless compute (V8 isolates) | Hono + tRPC |
| **Pages** | Static sites + edge functions | Astro, Next.js, SPAs |
| **D1** | SQLite at the edge | Drizzle (sqlite-core + d1) |
| **KV** | Key-value storage | Sessions, cache |
| **R2** | Object storage (S3-compatible) | File uploads |
| **Hyperdrive** | External Postgres connection | Neon integration |
| **Queues** | Message queues | Background jobs |
| **Durable Objects** | Stateful edge compute | Real-time, WebSockets |

### Workers Runtime vs Node.js

Workers run on V8 isolates, NOT Node.js:

| Feature | Node.js | Workers | Solution |
|---------|---------|---------|----------|
| `fs` module | ✅ | ❌ | Use R2/KV |
| Native bindings | ✅ | ❌ | Pure JS only |
| `process.env` | ✅ | ❌ | Use env bindings |
| TCP sockets | ✅ | ❌ | Use Hyperdrive |
| Execution time | Unlimited | 30s | Durable Objects |
| `crypto` | Full Node | Web Crypto | Use Web Crypto API |

**What works on Workers:** Hono, tRPC, Zod, Drizzle (D1 adapter), jose (JWT).

**Enable partial Node.js compat:**
```toml
compatibility_flags = ["nodejs_compat"]
```

### Quick Start: Workers API

```bash
# Initialize
mkdir my-api && cd my-api
pnpm init
pnpm add hono drizzle-orm zod
pnpm add -D wrangler drizzle-kit typescript

# Create D1 database
wrangler d1 create my-db

# Development
wrangler dev

# Deploy
wrangler deploy
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

**src/index.ts:**
```typescript
import { Hono } from 'hono';
import type { Bindings } from './env';

const app = new Hono<{ Bindings: Bindings }>();

app.get('/health', (c) => c.json({ status: 'ok' }));

export default app;
```

**src/env.ts:**
```typescript
export type Bindings = {
  DB: D1Database;
  JWT_SECRET: string;
};
```

> **Full setup details:** See `cloudflare.md` for complete Hono patterns, Drizzle D1 setup, middleware, error handling, and all services.

### Essential Wrangler Commands

```bash
# Development
wrangler dev                    # Local dev server
wrangler dev --remote           # Use production bindings

# Deploy
wrangler deploy                 # Deploy Workers
wrangler pages deploy dist      # Deploy Pages

# D1 Database
wrangler d1 create my-db
wrangler d1 execute my-db --local --file=./migration.sql
wrangler d1 execute my-db --remote --file=./migration.sql

# Secrets
wrangler secret put JWT_SECRET  # Set secret (prompts)
wrangler secret list

# Logs
wrangler tail                   # Live production logs
```

> **Full CLI reference:** See `cloudflare.md` for complete Wrangler commands including KV, R2, Queues, Hyperdrive.

### D1 + Drizzle Migration Workflow

```bash
# 1. Edit src/db/schema.ts
# 2. Generate migration
pnpm drizzle-kit generate

# 3. Apply locally
wrangler d1 execute my-db --local --file=./drizzle/0001_init.sql

# 4. Test
wrangler dev

# 5. Apply to production
wrangler d1 execute my-db --remote --file=./drizzle/0001_init.sql

# 6. Deploy
wrangler deploy
```

### Pages Deployment

**Static site:**
```bash
pnpm build
wrangler pages deploy dist
```

**Astro:**
```bash
pnpm add @astrojs/cloudflare
# Configure adapter in astro.config.mjs
pnpm build
wrangler pages deploy dist
```

**Next.js:**
```bash
pnpm add @cloudflare/next-on-pages
npx @cloudflare/next-on-pages
wrangler pages deploy .vercel/output/static
```

### Storage Decision Matrix

| Need | Use | Why |
|------|-----|-----|
| Relational data | D1 | SQL queries, joins |
| Session/cache | KV | Fast, TTL support |
| Files/uploads | R2 | Large objects, streaming |
| Complex Postgres | Hyperdrive | External DB pooling |

---

## Stack 2: Self-Hosted (VPS2 + Tailscale)

### When to Use

- Private internal tools (not public-facing)
- Admin dashboards
- Long-running processes (Workers have time limits)
- Full Node.js runtime required
- Native bindings needed
- Sensitive data that shouldn't leave infrastructure

### Docker Deployment

**Dockerfile:**
```dockerfile
# Pin to security-patched version (CVE-2025-59466)
FROM node:24.13.0-alpine AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:24.13.0-alpine AS runner
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**docker-compose.yml:**
```yaml
services:
  app:
    build: .
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=file:/app/data/app.db
    volumes:
      - ./data:/app/data
```

**Deploy:**
```bash
# On VPS2
git clone <repo>
cd <repo>
docker compose up -d
```

### Tailscale Private Access

```bash
# Expose on tailnet (private HTTPS)
tailscale serve --bg --https=443 http://localhost:3000

# Access at:
# https://vps2.<tailnet>.ts.net
```

**Benefits:**
- Automatic HTTPS (Tailscale handles certs)
- Only accessible to tailnet members
- No firewall configuration needed
- No public exposure

**Multiple services:**
```bash
tailscale serve --bg --https=443 --set-path /api http://localhost:3000
tailscale serve --bg --https=443 --set-path /admin http://localhost:3001
```

---

## Decision Framework

### Deployment Decision Tree

```
What are you building?
│
├─► API / Microservice
│   ├─► Public? → Cloudflare Workers + D1
│   └─► Private? → Self-hosted + Tailscale
│
├─► Static website → Cloudflare Pages
│
├─► SSR website (Astro/Next)
│   ├─► Public? → Cloudflare Pages
│   └─► Private? → Self-hosted
│
├─► Real-time / WebSocket
│   ├─► Coordination needed? → Durable Objects
│   └─► Simple? → Workers or Self-hosted
│
├─► Background jobs
│   ├─► < 30s? → Workers + Queues
│   └─► Long-running? → Self-hosted
│
├─► MCP Server → Self-hosted (Node.js required)
│
└─► CLI Tool → Local Node.js (not deployed)
```

### Workers vs Self-Hosted

| Requirement | Cloudflare | Self-Hosted |
|-------------|------------|-------------|
| Public API | ✅ | ⚠️ |
| Private dashboard | ⚠️ | ✅ |
| Edge latency | ✅ | ❌ |
| Native bindings | ❌ | ✅ |
| Long-running | ❌ | ✅ |
| Full Node.js | ❌ | ✅ |
| Cost at scale | ✅ | ⚠️ |

### Database Choice

| Scenario | Use |
|----------|-----|
| Simple app, edge latency | D1 |
| Complex queries | Hyperdrive + Neon |
| Existing Postgres | Hyperdrive |
| Private/internal | Self-hosted SQLite/Postgres |

---

## Environment & Secrets

### Cloudflare

```bash
# Set secrets (production)
wrangler secret put JWT_SECRET

# Local development (.dev.vars)
echo "JWT_SECRET=dev-secret" >> .dev.vars
```

### Self-Hosted

```bash
# .env file
DATABASE_URL=file:./data/app.db
JWT_SECRET=your-secret

# Or Docker Compose environment
environment:
  - JWT_SECRET=${JWT_SECRET}
```

---

## Quick Reference

### Cloudflare Project Setup

```bash
mkdir my-api && cd my-api
pnpm init
pnpm add hono drizzle-orm zod
pnpm add -D wrangler drizzle-kit typescript
wrangler d1 create my-db
echo "24.13.0" > .nvmrc
```

### Self-Hosted Project Setup

```bash
mkdir my-tool && cd my-tool
pnpm init
pnpm add hono drizzle-orm better-sqlite3 zod
pnpm add -D tsup typescript @types/node @types/better-sqlite3
echo "24.13.0" > .nvmrc
```

---

## Summary

```
┌─────────────────────────────────────┐
│         CLOUDFLARE (Primary)        │
├─────────────────────────────────────┤
│ Workers     - APIs (Hono + tRPC)    │
│ Pages       - Static sites, SPAs    │
│ D1          - SQLite database       │
│ R2          - Object storage        │
│ KV          - Cache, sessions       │
│ Hyperdrive  - External Postgres     │
│                                     │
│ See: cloudflare.md for full details │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    SELF-HOSTED (Private Only)       │
├─────────────────────────────────────┤
│ VPS2        - Docker containers     │
│ Tailscale   - Private access        │
│ SQLite/PG   - Full database         │
│ Node.js     - Full runtime          │
└─────────────────────────────────────┘
```

**Decision:**
```
Is it public? → Cloudflare
Is it private? → Self-hosted + Tailscale
```

---

*Companion to: typescript-ironclad-stack.md, cloudflare.md*
*Last updated: 2026-01-14 (Docker pinned to Node 24.13.0 for CVE-2025-59466)*
