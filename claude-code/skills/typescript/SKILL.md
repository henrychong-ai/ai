---
name: typescript
description: "TypeScript development — type-safe JavaScript, fintech platforms, TypeScript compiler, React/Node.js, type system, async patterns, testing (Vitest), Cloudflare Workers. Owns an opinionated back-to-front ironclad stack (recommended default for back-end/services/internal tools): the Option-B @hono/zod-openapi single-source pattern where ONE createRoute() drives request+response validation, the generated OpenAPI doc, dashboard client types, and MCP tool schemas (API Shield parity/freshness guards + gotchas in api-patterns.md). Also covers API development (Hono, tRPC, REST, GraphQL) and the front-to-back Next.js full-stack boundary for when not to use it. Use for TypeScript code, type definitions, framework development, picking an API/stack architecture, and fintech applications."
---

# TypeScript Development Specialist

## When to Use This Skill

- Writing or refactoring TypeScript code
- Type definitions and advanced type patterns
- React or Node.js framework implementation
- API development (Hono, tRPC, REST, GraphQL)
- Cloudflare Workers and edge deployment
- Fintech and financial calculations
- Vitest/TypeScript testing strategies
- Performance optimization and async patterns

## Reference Files

Load as needed based on the task at hand:

### Coding Standards
- `references/coding-standards/style-guide.md` - Naming, formatting, organization (mkosir-based)
- `references/coding-standards/type-patterns.md` - Advanced TypeScript type patterns
- `references/coding-standards/clean-code.md` - Clean code principles for TypeScript
- `references/coding-standards/tooling.md` - tsconfig.json, Biome, editor integration

**Linting Setup:** For comprehensive linting configuration, invoke the `/lint` skill. The lint skill is the single source of truth for Oxlint + Biome setup with residual ESLint gap plugins.

### Implementation Patterns
- `references/patterns/error-handling.md` - Result/Either patterns, Zod, error boundaries
- `references/patterns/async-patterns.md` - Concurrency, cancellation, retries
- `references/patterns/api-patterns.md` - Hono, tRPC, REST/GraphQL **and the `@hono/zod-openapi` single-source pattern — the recommended DEFAULT for back-end / back-to-front projects** (one `createRoute()` drives request+response validation, the OpenAPI doc, dashboard client types, and MCP tool schemas; API Shield parity, auth-before-validation ordering, and the migration gotchas)
- `references/patterns/security-patterns.md` - Input depth limiting, DoS prevention, CVE mitigations
- `references/patterns/nestjs-patterns.md` - **Core NestJS** (modules, DI, the request lifecycle order, guards/interceptors/pipes/filters, custom param decorators, config, testing) — *not part of the ironclad stack; for existing or inherited NestJS codebases; core only — codebase-specific conventions live in that repository's `AGENTS.md`*

### Testing
- `references/testing/vitest-patterns.md` - Vitest config, mocking, coverage
- `references/testing/testing-strategies.md` - TDD, testing pyramid, E2E with Playwright

### AI Development
- `references/ai-development/claude-code-rules.md` - TypeScript conventions for Claude Code
- `references/ai-development/project-configuration.md` - Multi-environment project setup (rules, @import, environments)

### Tech Stack (Ironclad Stack)
- `references/tech-stack/typescript-ironclad-stack.md` - Core tech stack decisions, incl. **the Option-B back-to-front pattern (recommended default)** + the back-to-front vs front-to-back boundary (when not to use it)
- `references/tech-stack/typescript-ironclad-infra.md` - Deployment infrastructure
- `references/tech-stack/cloudflare.md` - Cloudflare Workers/D1/KV complete reference
- `references/tech-stack/when-to-use-astro.md` - Decision guide: when a content-driven site should use Astro
- `references/tech-stack/astro-content-site-stack.md` - Astro 5 content-site stack on Cloudflare (optional Payload CMS)
- `references/tech-stack/obsidian.md` - Obsidian plugin development stack (official sample-plugin template)

### Debugging
- `references/debug/debug-statements.md` - Unconditional debug output in production code: symptoms, levelled-logger fix, detection greps

### Frontend Resources
- https://www.builtatlightspeed.com - Frontend themes, templates, and UI kits

## Core Capabilities

### 1. Type System Mastery
- Advanced types (generics, conditional, mapped, template literal)
- Type narrowing and type guards
- Utility types and custom type builders
- Strict compiler configuration
- Type-safe API design with Zod

### 2. Framework Integration
- **Hono**: Type-safe routes, middleware, Workers integration
- **tRPC**: End-to-end type-safe APIs
- **React**: Hooks, context, performance optimization
- **Node.js**: Async patterns, streams
- **GraphQL**: Type-safe queries with generated types
- **NestJS** (core): modules, DI, guards/interceptors/pipes/filters, custom decorators — see `references/patterns/nestjs-patterns.md` (non-ironclad; for existing or inherited NestJS codebases)

### 3. Cloudflare Workers
- Edge-first API development
- D1 database with Drizzle ORM
- KV, R2, Queues, Durable Objects
- Wrangler CLI operations

### 4. Fintech Applications
- Financial calculations with proper decimal handling
- Real-time trading systems and WebSocket streams
- Payment processing integration
- Blockchain and cryptocurrency APIs

### 5. Testing & Quality (MANDATORY for AI Development)

**Testing is non-negotiable for AI-driven development.** All code generated by Claude Code must have corresponding tests to validate correctness.

#### Framework Selection
| Project Type | Framework | Rationale |
|--------------|-----------|-----------|
| **New projects** | Vitest | Native ESM, fast, TypeScript-first |
| **Legacy/CRA projects** | Jest | Existing infrastructure, gradual migration |

#### Coverage Requirements
- Follow the approved repository coverage policy; generic examples do not override it.
- If no policy exists, propose thresholds by package and risk; 80% is a starting example, not a universal minimum.
- Measure complete owned runtime source, including unimported TS/TSX; apply additional per-file floors to critical security decisions.
- Document and review exclusions; a filename such as `types.ts` does not prove the file has no runtime code.
- See testing references for assertion quality, provider compatibility, and evidence limits.

#### When Tests Are MANDATORY
- Any new function/method with business logic
- Any bug fix (test proves bug exists → proves fix works)
- Any API endpoint (request/response validation)
- Any data transformation or calculation
- Any error handling path

#### When Tests Are OPTIONAL
- Simple getters/setters with no logic
- Pure configuration/constant exports
- Type-only files (*.d.ts)
- Trivial wrapper functions

#### Quick Setup (Vitest)
```bash
pnpm add -D vitest @vitest/coverage-v8
```

#### Test Commands
```bash
pnpm test              # Watch mode
pnpm test:run          # Single run (CI)
pnpm test:coverage     # With coverage report
pnpm test:ui           # Visual UI
```

#### File Conventions
- Co-locate tests: `src/utils.ts` → `src/utils.test.ts`
- Or use `__tests__/` directory for complex modules
- Naming: `*.test.ts` or `*.spec.ts`

#### Reference Files
- `references/testing/vitest-patterns.md` - Vitest config, mocking, assertions
- `references/testing/jest-patterns.md` - Jest for legacy projects
- `references/testing/testing-strategies.md` - TDD, testing pyramid, E2E
- `references/testing/ai-testing-protocols.md` - Claude Code testing requirements

#### Templates
- `templates/testing/vitest.config.ts` - Base config with 80% coverage
- `templates/testing/setup.ts` - Global test setup
- `templates/testing/vitest.config.react.ts` - React/DOM (jsdom) Vitest config
- `templates/testing/setup.react.ts` - React Testing Library setup
- `templates/testing/vitest.workspace.ts` - Monorepo Vitest workspace config
- `templates/testing/jest.config.ts` - Legacy Jest config
- `templates/testing/jest.setup.ts` - Legacy Jest global setup

## Quick Reference

### Project Setup (Ironclad Stack)
```bash
mkdir my-project && cd my-project
pnpm init
pnpm add typescript zod hono
pnpm add -D vitest @types/node@^24 oxlint @biomejs/biome
echo "24" > .nvmrc
```

### Type Patterns
```typescript
// Result type for error handling
type Result<T, E> =
  | { success: true; data: T }
  | { success: false; error: E };

// Type guards
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value
  );
}

// Const objects over enums
const Status = {
  Pending: 'pending',
  Active: 'active',
} as const;
type Status = typeof Status[keyof typeof Status];
```

## Proactive Coaching

**When reviewing TypeScript code, check:**
1. Strict mode enabled in tsconfig.json
2. No `any` types (use `unknown` + narrowing)
3. Zod schemas for external data
4. Result types for error handling
5. Proper async/await patterns (no floating promises)

**When debugging:**
1. Check type narrowing issues
2. Verify Zod schema matches expected data
3. Look for unhandled promise rejections
4. Check for null/undefined access

**When optimizing:**
1. Profile with Chrome DevTools or clinic.js
2. Use proper memoization (useMemo, useCallback)
3. Consider edge deployment for latency
4. Bundle analysis with source-map-explorer

---
