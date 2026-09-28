# TypeScript Style Guide

How to write TypeScript in this stack: naming, types, functions, modules, comments, clean-code principles, and the rules a coding agent follows when editing existing code. Based on [mkosir/typescript-style-guide](https://github.com/mkosir/typescript-style-guide). Advanced type techniques: `type-patterns.md`. Formatting and lint rules are enforced by Oxlint + Biome (`/lint`); do not restate what the formatter decides.

---

## Core principles

1. **Consistency** — follow the conventions below uniformly; match the surrounding code when a repository has its own established style.
2. **Enforce with tooling** — the compiler (strict tsconfig, `tooling.md`), Oxlint and Biome catch what they can; reviews cover the rest.
3. **Functional first** — pure functions, immutable data, composition. Classes where a framework requires them (NestJS providers, React error boundaries, custom `Error` subclasses).
4. **Type safety** — no `any`; validate external data with Zod; let the types describe every valid state.

---

## Naming

| Kind | Convention | Example |
|------|------------|---------|
| Variables, functions | camelCase; functions start with a verb | `userCount`, `getUserById`, `calculateTotalWithTax` |
| Booleans, predicates | `is`, `has`, `should`, `can`, `will`, `did` prefix | `isActive`, `hasPermission`, `didComplete` |
| Constants (module-level primitives) | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| Const objects used as enums | PascalCase, singular, `as const` | `Status`, `Color` |
| Types | PascalCase | `User`, `OrderStatus` |
| Generics | `T` + descriptive name when more than one | `TInput`, `TOutput`, `TData` |
| Files and directories | kebab-case | `user-service.ts`, `api-client/` |
| React components | PascalCase files and names | `UserProfile.tsx` |
| React hooks | `use` prefix | `useUserData` |
| Event props / handlers | `on*` props, `handle*` handlers | `onClick`, `handleSubmit` |
| Tests | `*.test.ts` next to the code | `user-service.test.ts` |

- **Acronyms are words**: `HttpClient`, `getApiUrl`, `userId`, `JsonResponse` (not `HTTPClient`, `userID`).
- **Full words** unless universally understood (`id`, `url`, `api` are fine; `usr`, `btn`, `idx` are not).
- **Searchable constants** instead of magic numbers: `const WEEK_IN_MS = 7 * 24 * 60 * 60 * 1000;`.

---

## Types

### `type` by default

Use `type` for object shapes, unions, intersections and utility compositions. Use `interface` only when you need declaration merging, module augmentation (for example extending a library's types) or a class `implements` contract.

```typescript
type User = {
  readonly id: string;
  name: string;
  email: string;
};

type CreateUserInput = Omit<User, 'id'>;
type AdminUser = User & { permissions: Array<string> };
```

### Arrays: generic syntax

```typescript
type Users = Array<User>;
type ReadonlyUsers = ReadonlyArray<User>;
```

### No enums: const objects or literal unions

```typescript
const Status = {
  Pending: 'pending',
  Active: 'active',
  Inactive: 'inactive',
} as const;

type Status = (typeof Status)[keyof typeof Status]; // 'pending' | 'active' | 'inactive'

// or, when no runtime object is needed:
type Role = 'admin' | 'user' | 'guest';
```

### No `any`

Use `unknown` and narrow, or parse with Zod. A weakened type (`any`, an unchecked `as`, a non-null `!`) needs a comment saying why it is safe.

### Type imports

`verbatimModuleSyntax` (tsconfig standard) requires type-only imports to be marked:

```typescript
import type { Order, User } from './types';
import { createUser, type CreateUserInput } from './users';
```

### `null` vs `undefined`

| Value | Use |
|-------|-----|
| `null` | Deliberately empty ("looked, found nothing") |
| `undefined` | Missing, optional or not yet set |

Return an empty array for "no results", never `null`.

---

## Functions

- **One job per function.** Split validation, transformation, persistence and notification into separate functions and compose them.
- **Single options object** once a function takes more than one or two parameters, or any optional ones:

  ```typescript
  type CreateUserInput = { name: string; email: string; role: Role; department?: string };
  function createUser(input: CreateUserInput): User { /* ... */ }
  ```
- **Explicit return types on exported functions**; let inference handle local helpers.
- **Pure where possible**: no hidden reads or writes of module state. Return new data instead of mutating arguments:

  ```typescript
  function addItem(cart: ReadonlyArray<Item>, item: Item): Array<Item> {
    return [...cart, item];
  }
  ```
- **Command–query separation**: a function either changes state or returns data, not both.
- **Dependencies are parameters.** Pass collaborators in (`createUserService({ db, logger })`) rather than constructing them inside, so tests can substitute them.

---

## Immutability

- Mark fields that must not change `readonly`; accept `ReadonlyArray<T>` / `Readonly<T>` parameters.
- Use `as const` for literal configuration and `satisfies` to check a shape without widening:

  ```typescript
  const routes = {
    home: '/',
    users: '/users',
  } as const satisfies Record<string, string>;
  ```
- Update with spreads (`{ ...user, name }`), not assignment.

---

## Modules and organisation

- **Organise by feature**, not by kind: `src/users/{user-service.ts, user-service.test.ts, user-types.ts}` rather than `src/services/`, `src/types/`.
- **Named exports by default.** Default exports only where a framework or runtime requires them: a Worker's `export default app`, Next.js pages/layouts/route config, Astro and Vite config files, `vitest.config.ts`.
- **Import order**: external packages, then aliased internal imports (`@/…`), then relative imports. Biome's organize-imports action sorts them; do not hand-sort.
- **Law of Demeter**: avoid `a.getB().getC().getD()`; expose what callers need, or destructure at the boundary.
- **Composition over inheritance**: build capabilities from small types and factory functions, not deep class hierarchies.

---

## Errors

Validate at boundaries, type expected failures, and never swallow exceptions. Full patterns: `../patterns/error-handling.md`.

---

## React

```typescript
type UserCardProps = {
  user: User;
  onDelete?: (id: string) => void;
};

export function UserCard({ user, onDelete }: UserCardProps) {
  return <div>{user.name}</div>;
}
```

- Function components with typed destructured props; props type named `[Component]Props`. Do not use `React.FC`.
- Custom hooks return objects (`{ user, isLoading, error }`) except for the `useState`-style tuple pattern.
- Performance and framework rules: the React and Next.js documentation.

---

## Comments

- Make the code say **what**; comments say **why** (a constraint, a workaround, a non-obvious decision).
- Replace a comment that explains unclear code with clearer names:

  ```typescript
  const isAdmin = user.role === 'admin';
  const isActive = user.isActive && !user.isDeleted;
  if (isAdmin && isActive) { /* ... */ }
  ```
- TSDoc on exported APIs: purpose, parameters, return, thrown errors, an example when usage is not obvious.
- Delete commented-out code; version control keeps it.

---

## Editing existing code (rules for developers and coding agents)

- **Stay in scope.** Change what the task needs; leave unrelated code, formatting and comments alone.
- **Preserve behaviour and signatures** unless the task is to change them; if a signature must change, update every caller in the same change.
- **Match the surrounding style**, even where it differs from this guide, unless the task is a style migration.
- **Keep or strengthen types.** Never weaken a type to make an error disappear (`any`, `as unknown as`, `!`, `@ts-ignore`); fix the cause, or use `@ts-expect-error` with a reason.
- **Tests travel with the change**: add tests for new behaviour and a failing-then-passing test for a bug fix; do not delete or skip tests to get green (`../testing/ai-testing-protocols.md`).
- **Run the repository's own check script** (`pnpm check` or the CI-equivalent) before calling the work done.

---

## Summary

| Area | Convention |
|------|------------|
| Variables / functions | camelCase, verb-first functions |
| Booleans | `is`/`has`/`should`/`can`/`will`/`did` |
| Constants | SCREAMING_SNAKE_CASE |
| Types | PascalCase, `type` by default |
| Generics | `T` + descriptive name |
| Files / directories | kebab-case; React components PascalCase |
| Acronyms | Capitalise the first letter only |
| Arrays | `Array<T>` / `ReadonlyArray<T>` |
| Enums | Const objects or literal unions |
| `any` | Never; `unknown` + narrowing or Zod |
| Exports | Named, except framework-required defaults |
| Functions | Pure, single options object, explicit return types on exports |
| Comments | Why, not what |
