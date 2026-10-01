---
name: typescript
description: "TypeScript development standards — strict tsconfig, style and type patterns, Zod 4 validation, async/error handling, Vitest/Jest testing, and the single owner of Node, TypeScript, pnpm and JS/TS tool version policy and upgrade protocol. Owns a back-to-front ironclad stack, default for services and internal tools: the Option-B @hono/zod-openapi pattern where ONE createRoute() drives runtime request validation, compile-time response typing, the OpenAPI doc (documented responses, API Shield guards), dashboard client types and MCP tool schemas. Also covers the ORM standard (Drizzle for internal tools/Workers, Prisma 7 for product apps), Fastify + Temporal services, Next.js apps, Cloudflare Workers, Astro sites and NestJS. Use when writing, reviewing or testing TypeScript, choosing versions or a stack, designing an API, or upgrading: bump Node, end-of-life runtime, Node CVE/security patch, Node Docker/CI images, TypeScript 5→6→7, React 19, Next.js 16, ES target/lib, or auditing runtime versions."
---

# TypeScript Development Standards

How to write, structure, version, upgrade and test TypeScript across repositories. Repository-specific facts belong in each repository's own `AGENTS.md`, not here.

## Related skills

| Need | Skill |
|------|-------|
| Lint, format and git-hook configuration (Oxlint, Biome, residual ESLint, husky, lint-staged, gitleaks) | `/lint` |

## Reference files

Load what the task needs.

### Stack and versions
- `references/tech-stack/version-policy.md` — **single owner** of Node, TypeScript, pnpm (via pinned Corepack) and tool versions, with live-check commands
- `references/tech-stack/typescript-ironclad-stack.md` — the stack, **the canonical Option-B back-to-front pattern**, back-to-front vs front-to-back, project shapes, decision tree
- `references/tech-stack/orm.md` — Drizzle (internal tools, Workers) and Prisma 7 (product apps, PostgreSQL and SQL Server)
- `references/tech-stack/cloudflare.md` — TypeScript on Workers: generated `Env`, `nodejs_compat`, D1 migrations, Vitest with `cloudflareTest()`
- `references/tech-stack/astro.md` — when to use Astro, and current Astro (Content Layer, Workers adapter)

### Coding standards
- `references/coding-standards/style-guide.md` — naming, types, functions, modules, comments, clean-code principles, rules for editing existing code
- `references/coding-standards/type-patterns.md` — advanced type patterns (discriminated unions, branded types, conditional and template literal types)
- `references/coding-standards/tooling.md` — **the tsconfig standard** (TS 7-ready), package scripts, editor settings

### Patterns
- `references/patterns/api-patterns.md` — Hono, tRPC, REST, **the `@hono/zod-openapi` single-source implementation**, API Shield parity and freshness guards, migration gotchas
- `references/patterns/node-services.md` — Fastify 5 + Temporal workers + Zod config
- `references/patterns/error-handling.md` — Result types, Zod validation, error classes, error boundaries
- `references/patterns/async-patterns.md` — concurrency, cancellation, retries
- `references/patterns/security-patterns.md` — input depth limiting and DoS defences
- `references/patterns/nestjs-patterns.md` — core NestJS, for existing NestJS codebases (not part of the default stack)

### Testing
- `references/testing/vitest-patterns.md` — Vitest config, `test.projects`, mocking, coverage
- `references/testing/testing-strategies.md` — test pyramid, integration and E2E (Playwright), CI gate
- `references/testing/ai-testing-protocols.md` — testing requirements for agent-assisted work, behavioural evidence
- `references/testing/jest-patterns.md` — Jest for NestJS and unmigrated suites

### Upgrades
- `references/version-upgrade/upgrade-protocol.md` — **the upgrade protocol**: production safety, approval and test-edit precedence, modes, live checks, detection matrix, package-manager commands, phases 1–7, rollback, ES target
- Node: `references/version-upgrade/node/` — `migration-overview.md`, `legacy-node-to-24.md`, `node-20-to-22.md`, `node-22-to-24.md`, `node-24-to-26.md`
- TypeScript: `references/version-upgrade/typescript/` — `typescript-legacy-to-5.md`, `typescript-5-to-6.md`, `typescript-6-to-7.md`
- React: `references/version-upgrade/react/react-to-19.md`
- Next.js: `references/version-upgrade/frameworks/nextjs-migrations.md`
- ECMAScript: `references/version-upgrade/ecmascript/` — `es-upgrade-checklist.md`, `es-version-features.md`, `browser-support.md`, `bundler-configuration.md`, `polyfill-strategies.md`
- Safety: `references/version-upgrade/safety/ai-guardrails.md`, `references/version-upgrade/safety/testing-protocols.md`

### Debugging
- `references/debug/debug-statements.md` — unconditional debug output: symptoms, levelled-logger fix, detection

### Templates (`templates/testing/`)
- `vitest.config.ts` — Node/backend base config
- `vitest.config.react.ts` — React/jsdom config
- `vitest.config.projects.ts` — monorepo root config with `test.projects`
- `setup.ts` — global Vitest setup (custom matchers, helpers)
- `setup.react.ts` — React Testing Library setup with constructible observer mocks
- `jest.config.ts`, `jest.setup.ts`, `tsconfig.jest.json` — Jest with ts-jest (the tsconfig compiles tests as CommonJS)

Templates are formatted with `/lint`'s Biome defaults (double quotes), so they pass `biome check` when copied. Code examples in `references/` are illustrative and use single quotes for brevity; the repository's formatter decides the final style.

## Core defaults

| Area | Default |
|------|---------|
| Runtime | Node 24 LTS now; Node 26 for new projects once it is LTS (2026-10-28) |
| Compiler | `typescript@~6.0`, strict; TS 7 only as an optional type-check-only lane |
| Package manager | pnpm (one pinned major), installed through a pinned Corepack from the hash-pinned `packageManager` field |
| Validation | Zod 4 at every boundary (requests, env, external data) |
| API | `@hono/zod-openapi` Option-B for services and internal tools; tRPC for internal-only RPC; Next.js for product web apps; Fastify + Temporal for durable workflows |
| ORM | Drizzle (internal tools, Workers) · Prisma 7 (product apps) |
| Run / build | tsx · `tsc` · tsdown · Vite · Wrangler |
| Test | Vitest `^4.1` (+ Playwright for E2E); Jest in NestJS codebases |
| Lint / format | Oxlint + Biome via `/lint` |

Never run an unpinned `pnpm add -D typescript`: npm's `latest` is TypeScript 7, which has no compiler API for typescript-eslint, ts-jest or declaration bundlers. Check live versions with the commands in `version-policy.md` before writing any version.

## Testing expectations

- New behaviour, bug fixes (a failing test first), API endpoints, data transformations and error paths get tests. Trivial getters, constants and type-only files do not need them.
- Coverage follows the repository's approved policy. Where none exists, propose thresholds by package and risk (80% is a starting example, not a universal minimum), measure all owned runtime source including files no test imports, and review every exclusion: a name like `types.ts` does not prove a file has no runtime code.
- Co-locate tests (`src/user-service.ts` → `src/user-service.test.ts`); name them `*.test.ts`.
- Run the repository's own gate (`pnpm check` or the CI-equivalent script) before calling work done.

## Quick reference

```bash
# Add dependencies with explicit ranges (see version-policy.md)
pnpm add zod@^4 hono@^4 @hono/zod-openapi@^1
pnpm add -D typescript@~6.0 @types/node@^24 vitest@^4.1 @vitest/coverage-v8@^4.1 tsx@^4
# Lint, format and hooks: /lint.
```

```typescript
// Result type for expected failures
type Result<T, E> = { success: true; data: T } | { success: false; error: E };

// Parse, don't cast
const User = z.object({ id: z.uuid(), email: z.email() });
type User = z.infer<typeof User>;
const user = User.parse(await response.json());

// Const object instead of enum
const Status = { Pending: 'pending', Active: 'active' } as const;
type Status = (typeof Status)[keyof typeof Status];
```

## Upgrading

For any Node, TypeScript, React, Next.js or ES target upgrade — including a Node security patch or an end-of-life runtime — follow `references/version-upgrade/upgrade-protocol.md` and load the per-step guide it names. Two rules win over anything in the guides:

- **Approval** comes at phase checkpoints: after the plan, after version-file and dependency changes, and before commit.
- **Test edits** are allowed only when the new version changes observable output that a test pins (an error message, a deprecation warning, a renamed import); list each one with its cause. Any other failing test is a behaviour change: stop and report it.

## Reviewing TypeScript

Check, in order:

1. The tsconfig matches `tooling.md` (strict, no `baseUrl`, TS 7-ready).
2. No `any`, unchecked `as` or `!` without a stated reason; external data parsed with Zod.
3. Expected failures typed (Result or specific error classes); no swallowed exceptions.
4. No floating promises; timeouts cancel work (`AbortSignal.timeout`); concurrency bounded.
5. Versions and ranges follow `version-policy.md`; no `"latest"` in `package.json`.
6. Tests cover the change and assert behaviour, not implementation.
