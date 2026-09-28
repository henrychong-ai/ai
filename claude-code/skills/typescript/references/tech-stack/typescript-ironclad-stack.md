# The Ironclad Stack — TypeScript Architecture

An opinionated TypeScript stack: end-to-end type safety from database to browser, one validation library, one lint/format toolchain, one package manager.

**Core principle:** *one source of truth, one type chain, one set of tools.*

Versions for everything below: `version-policy.md`. Lint, format and hook configuration: `/lint`.

---

## Design Principles

1. **Types flow without gaps.** Strict TypeScript + Zod runtime validation + schema-derived types catch errors at compile time and at the boundary, not deep inside handlers.
2. **Mainstream tools.** Prefer tools with large ecosystems and documentation, so developers and coding agents produce correct code first time.
3. **One core, many shapes.** Services, dashboards, CLIs, MCP servers and libraries share the same language settings, validation, lint, test and package-manager choices; only the framework varies.
4. **Enforced, not remembered.** Pre-commit hooks (`/lint`) and the CI quality gate apply the standards on every change.

---

## The Core Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | TypeScript, strict | `typescript@~6.0`; tsconfig in `coding-standards/tooling.md` |
| Runtime | Node.js LTS | Node 24 now, Node 26 for new projects once LTS (`version-policy.md`) |
| Package manager | pnpm | One major pinned via `packageManager` (hash-checked by Corepack) |
| Validation | Zod 4 | Runtime validation + type inference at every boundary |
| API — internal tools, services with a dashboard or MCP consumer | Hono + `@hono/zod-openapi` | **Recommended default** — the Option-B pattern below |
| API — internal-only RPC, both ends in one TS monorepo, no external/MCP consumer | tRPC 11 | |
| API — product web apps | Next.js App Router (+ tRPC) | Front-to-back; see the boundary below |
| API — Node services with durable workflows | Fastify 5 + Temporal | `patterns/node-services.md` |
| ORM | Drizzle (internal tools, Workers) · Prisma 7 (product apps) | `orm.md` |
| Run / build | tsx to run · `tsc` to emit · tsdown to bundle · Vite for frontends · Wrangler for Workers | tsup is unmaintained upstream |
| Testing | Vitest 4 + Playwright | `testing/` references |
| Lint / format | Oxlint + Biome (residual ESLint only for gap plugins) | `/lint` |
| Git hooks | husky + lint-staged + gitleaks | `/lint` |
| Styling | Tailwind CSS 4 + shadcn/ui | |

---

## Environment and Configuration

Environment variables are strings. Parse them once at startup with Zod so a missing or malformed value fails the boot, not a request at 3 a.m.

```typescript
// src/env.ts
import { z } from 'zod';

const EnvSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  DATABASE_URL: z.url(),
  API_KEY: z.string().min(1),
});

export const env = EnvSchema.parse(process.env);
```

- Local development loads `.env` with `node --env-file=.env` (or `tsx --env-file=.env`); `dotenv` is not needed on current Node.
- Next.js: `@t3-oss/env-nextjs` separates server and client variables and fails the build on missing values.
- Workers: configuration arrives as bindings on `env` (see `cloudflare.md`).
- Secrets come from the platform's secret store at deploy time; never commit `.env` files.

---

## Path Aliases

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Use relative `paths` entries **without `baseUrl`** (TS 7 rejects `baseUrl`). Vite needs the same alias in `vite.config.ts` (or `vite-tsconfig-paths`); tsx, Vitest (with `vite-tsconfig-paths` or `resolve.alias`), Next.js and tsdown read tsconfig paths.

---

## Complete Type Flow

```
┌───────────────────────────────────────────────┐
│ DATABASE: Drizzle table (TypeScript)          │   Prisma apps: generated client types
└───────────────────────────────────────────────┘
                     ↓ drizzle-zod
┌───────────────────────────────────────────────┐
│ VALIDATION: Zod schemas (+ refinements)       │
│ type X = z.infer<typeof XSchema>              │
└───────────────────────────────────────────────┘
          ↓                          ↓
┌───────────────────────┐   ┌───────────────────────┐
│ API: createRoute()    │   │ FRONTEND: forms       │
│ (or tRPC .input())    │   │ zodResolver(XSchema)  │
└───────────────────────┘   └───────────────────────┘
          ↓                          ↓
┌───────────────────────────────────────────────┐
│ TYPES everywhere: handlers, clients, MCP tools │
└───────────────────────────────────────────────┘
```

Change the table → the Zod schema changes → the route, form and client types change → the compiler lists every place that needs fixing.

---

## The Option-B Back-to-Front Pattern (Recommended Default) — CANONICAL

> **This section is the canonical definition of the back-to-front pattern.** Other references point here; do not duplicate it. Keep project-specific adoption records in each project's own docs.

For back-end and back-to-front projects — a Worker or API that owns the contract, with a dashboard and/or MCP server consuming its types — this is the **default architecture**. The boundary for when *not* to use it is in "Back-to-Front vs Front-to-Back" below.

### Core principle: one shared Zod route definition is the single source of truth

Using `@hono/zod-openapi`, ONE `createRoute()` + `.openapi()` definition single-sources **all four** of:

1. **Request validation at runtime, and response typing.** The route's request schemas (params, query, headers, cookies, JSON and form bodies) are validated on every request. The response schemas are **not** validated at runtime: they type-check each handler's `c.json(...)` against the declared status codes at compile time, and they document the responses in the generated spec.
2. **The OpenAPI document** — *generated* from the route registry (never hand-written), with `info.version` taken from the build version so it cannot drift behind a deploy.
3. **The typed dashboard/client types** — the dashboard infers `z.input` (pre-default form shapes); Worker consumers infer `z.infer` / `z.output` (defaults applied).
4. **The MCP tool input schemas** — the MCP server's tools use the shared schema's `.shape`.

```
                 shared/  (single source of truth)
                 Zod route def: createRoute() + .openapi()
                              │
        ┌──────────┬──────────┴──────────┬──────────────┐
        ↓          ↓                      ↓              ↓
   request      OpenAPI doc          dashboard       MCP tool
   validation   (generated from      client types    input schemas
   + typed      route registry)      (z.input /      (shared .shape)
   responses    + API Shield         z.infer)
```

If a response must be checked at runtime (for example a proxied upstream payload), parse it explicitly with the response schema inside the handler or in a test; do not assume the library does it.

### Why `@hono/zod-openapi` (not a rewrite)

`OpenAPIHono` **extends `Hono`** — `.route()`, `.use()`, `.onError()` and `.request()` behave identically. Adoption is an **incremental, strangler-safe, per-router conversion**: converted `.openapi()` routers mount alongside plain Hono routers on the same instance. Convert in a deliberate order (lowest-risk, fewest-consumer routers first; auth-heavy and opaque-content routers last), shipping each conversion behind the full test suite.

### Reference stack

A pnpm workspace monorepo (directory names illustrative; a nested `packages/*` layout — `packages/api`, `packages/shared`, `packages/app` — works well for new projects):

| Workspace | Role |
|-----------|------|
| **API / Worker** | Hono + `@hono/zod-openapi` + Zod 4 — owns routes, generates the OpenAPI doc |
| **`shared/`** | The single-source-of-truth package: Zod schemas, inferred types, error catalog, the shared success/error response envelope |
| **dashboard** | React 19 + Vite + Tailwind + shadcn — imports types from `shared/` |
| **MCP** *(optional)* | MCP server — tool input schemas use `shared/` schema `.shape` |

Supporting (typical): your auth provider + RBAC; Drizzle (+ drizzle-zod where DB types feed the chain); Cloudflare KV / D1 / R2 on Workers or PostgreSQL on Node; Oxlint + Biome + Vitest; CI order `lint → format:check → typecheck (all workspaces) → test (all workspaces)`, then deploy.

### API Shield integration (Cloudflare)

The *generated* OpenAPI doc feeds **Cloudflare API Shield** schema validation in **BLOCK mode**. Two consequences make spec freshness a production concern:

- **A path absent from the uploaded spec is blocked for all traffic** when the zone's API Shield fallthrough/default action is block (as in BLOCK mode). Dropping a path from the generated doc is then an outage, not a docs nit.
- Upload the schema inside each environment's deploy step, for **that environment's host**, then sync the schema's operations into **Endpoint Management** — API Shield validates only managed operations, so an upload alone leaves unmanaged paths silently unvalidated.

Two guards protect this (detailed in `patterns/api-patterns.md`):

1. **Parity test** — the generated doc must be a *superset* of a committed baseline of live operations.
2. **Freshness gate** — wired into `pnpm run check`: the committed spec must equal the generator output, so CI fails on drift.

### Back-to-Front vs Front-to-Back: which to choose

| | **Back-to-front (this pattern — DEFAULT)** | **Front-to-back** |
|---|---|---|
| Owns the contract | The API/Worker (`shared/` Zod) | The frontend framework |
| Types flow | Out from the API → dashboard + MCP | Co-located in the framework (server actions / RSC / route handlers / tRPC) |
| Shape | API + SPA dashboard + MCP, split workspaces | One Next.js full-stack app |
| Choose when | The project is fundamentally an **API + SPA (+ MCP)** split — a service, internal tool, or platform API | The project is fundamentally a **Next.js web app** (customer portals, product front ends) |
| ORM | Drizzle | Prisma 7 |
| Reference | This section + `patterns/api-patterns.md` | Next.js App Router documentation |

**Default to back-to-front** for services, APIs and internal tools. Use front-to-back only when the project genuinely *is* a Next.js web app. tRPC remains right for internal-only RPC when there is no external or MCP consumer and both ends live in one TypeScript monorepo.

> **Gotchas:** `defaultHook` error funnelling, validation-vs-middleware ordering, repeated query keys, MCP argument coercion, `.refine()` enum loss, opaque content types and request-only runtime validation are codified in `patterns/api-patterns.md` → "@hono/zod-openapi Single-Source Pattern".

---

## Project Shapes

| Shape | Framework | Build / run | Notes |
|-------|-----------|-------------|-------|
| Internal tool / service with dashboard or MCP | Hono + `@hono/zod-openapi` | Wrangler (Workers) or tsx (Node) | Option-B above |
| Product web app | Next.js App Router (+ tRPC) | Next | Prisma 7 |
| Node service with durable workflows | Fastify 5 + Temporal | tsx / `tsc` | `patterns/node-services.md` |
| Workers API or edge service | Hono | Wrangler | `cloudflare.md` |
| SPA | React + Vite | Vite | TanStack Query for server state |
| MCP server (stdio, local) | `@modelcontextprotocol/sdk` | tsx / tsdown | Node runtime |
| MCP server (remote) | Hono on Workers or Node | Wrangler / tsx | OAuth per the MCP authorization spec |
| CLI | `commander` + Zod | tsdown | `bin` + `#!/usr/bin/env node` banner |
| npm library | — | tsdown or `tsc` | ESM first; add CJS only for known consumers |
| Content / marketing site | Astro | Astro | `astro.md` |
| Existing NestJS codebase | NestJS | Nest CLI | `patterns/nestjs-patterns.md` |

`/lint` installs the lint, format and hook configuration for any of these.

---

## Decision Tree

```
What are you building?
│
├─► API or service
│   ├─► Owns the contract for a dashboard and/or MCP consumer?  ◄── DEFAULT
│   │   └─► Option-B: Hono + @hono/zod-openapi (Workers or Node)
│   ├─► Long-running, retry-heavy or scheduled business processes?
│   │   └─► Fastify 5 + Temporal (patterns/node-services.md)
│   └─► Internal-only RPC, both ends in one TS monorepo, no external/MCP consumer?
│       └─► Hono + tRPC
│
├─► Web app with SSR, SEO or a customer-facing UI
│   └─► Next.js App Router (+ tRPC) + Prisma 7
│
├─► SPA only → React + Vite
├─► MCP server → stdio (Node) or remote (Hono on Workers/Node)
├─► CLI → commander + tsdown
├─► npm package → tsdown or tsc
└─► Content / marketing site → Astro (astro.md)
```

Where it runs (Workers, containers, Docker hosts) is a separate deployment decision.

---

## Appendix: Bun

Bun is not part of the stack as a runtime. `bun install` is fast and usually compatible, but this stack standardises on pnpm, and services run on Node.js. Use Bun only where a repository has already chosen it, and run the test suite on Node before relying on it.

---

## Summary

```
Language:            TypeScript strict (typescript ~6.0)
Runtime:             Node.js 24 LTS (26 for new projects once LTS)
Package manager:     pnpm (one pinned major)
Validation:          Zod 4
API (default):       Hono + @hono/zod-openapi single-source (Option-B)
API (internal RPC):  tRPC 11
Web apps:            Next.js App Router (+ tRPC)
Durable services:    Fastify 5 + Temporal
ORM:                 Drizzle (internal tools, Workers) · Prisma 7 (product apps)
Run / build:         tsx · tsc · tsdown · Vite · Wrangler
Testing:             Vitest 4 + Playwright
Lint / format:       Oxlint + Biome (/lint)
Hooks:               husky + lint-staged + gitleaks (/lint)
Styling:             Tailwind CSS 4 + shadcn/ui
```

### Companion documents

| Document | Purpose |
|----------|---------|
| `version-policy.md` | Node, TypeScript, pnpm and tool versions |
| `orm.md` | Drizzle and Prisma standards |
| `cloudflare.md` | TypeScript on Cloudflare Workers |
| `astro.md` | Content sites |
| `patterns/api-patterns.md` | `@hono/zod-openapi` implementation, API Shield guards, gotchas |
| `patterns/node-services.md` | Fastify + Temporal services |
