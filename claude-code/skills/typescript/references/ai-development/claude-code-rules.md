# Claude Code TypeScript Rules

TypeScript conventions optimized for Claude Code development. These rules help Claude Code generate consistent, high-quality TypeScript code.

---

## Core Type Safety Rules

### Never Use `any`

```typescript
// ❌ Never
function parse(data: any): any { ... }
const value: any = response.data;

// ✅ Always use unknown and narrow
function parse(data: unknown): Result<User, ParseError> {
  const parsed = UserSchema.safeParse(data);
  if (!parsed.success) {
    return { success: false, error: new ParseError(parsed.error) };
  }
  return { success: true, data: parsed.data };
}
```

### Explicit Return Types

Always declare return types on exported functions:

```typescript
// ✅ Explicit return types
export function calculateTotal(items: Array<Item>): number { ... }
export async function fetchUser(id: string): Promise<User> { ... }
export function createHandler(): (req: Request) => Response { ... }
```

### Use Type Imports

```typescript
// ✅ Separate type imports
import type { User, Order } from './types';
import { createUser, updateUser } from './users';
```

### Const Objects Over Enums

```typescript
// ❌ Don't use enums
enum Status {
  Pending = 'pending',
  Active = 'active',
}

// ✅ Use const objects
const Status = {
  Pending: 'pending',
  Active: 'active',
} as const;

type Status = typeof Status[keyof typeof Status];
```

---

## Functional Patterns

### Prefer Pure Functions

```typescript
// ❌ Side effects
let counter = 0;
function increment(): number {
  return ++counter;
}

// ✅ Pure function
function increment(counter: number): number {
  return counter + 1;
}
```

### Immutability

```typescript
// ❌ Mutation
function addItem(cart: Array<Item>, item: Item): void {
  cart.push(item);
}

// ✅ Return new data
function addItem(cart: ReadonlyArray<Item>, item: Item): Array<Item> {
  return [...cart, item];
}
```

### Single Object Arguments

```typescript
// ❌ Many parameters
function createUser(
  name: string,
  email: string,
  age: number,
  role: string
): User { ... }

// ✅ Options object
type CreateUserInput = {
  name: string;
  email: string;
  age: number;
  role: string;
};

function createUser(input: CreateUserInput): User { ... }
```

---

## Naming Conventions

### Variables and Functions

```typescript
// camelCase for variables and functions
const userCount = 10;
const isActive = true;
const hasPermission = user.role === 'admin';

function getUserById(id: string): User { ... }
function calculateTotalWithTax(items: Array<Item>): number { ... }
```

### Boolean Prefixes

Always use descriptive prefixes for booleans:

```typescript
// ✅ Clear boolean names
const isLoading = true;
const hasError = false;
const shouldRefresh = true;
const canEdit = true;
const willExpire = true;
const didComplete = false;
```

### Types and Constants

```typescript
// PascalCase for types
type User = { ... };
type ApiResponse<T> = { ... };

// SCREAMING_SNAKE_CASE for constants
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';
```

### Files and Directories

```typescript
// kebab-case for files and directories
// src/user-service.ts
// src/api-client/index.ts
// src/utils/format-currency.ts

// PascalCase for React components
// src/components/UserProfile.tsx
```

---

## Safe Editing Rules

When modifying existing code:

### Don't Remove Existing Functionality

```typescript
// ❌ Don't delete working code without explicit request
// ❌ Don't change function signatures unexpectedly
// ❌ Don't modify unrelated code

// ✅ Extend functionality
// ✅ Add new functions alongside existing ones
// ✅ Preserve backwards compatibility
```

### Minimal Changes

```typescript
// ✅ Only change what's necessary for the task
// ✅ Keep existing patterns consistent
// ✅ Match surrounding code style
// ✅ Preserve existing comments and documentation
```

### Preserve Types

```typescript
// ❌ Don't weaken types
function getUser(id: string): User | null { ... }
// Changed to:
function getUser(id: string): any { ... }  // ❌ Wrong!

// ✅ Maintain or strengthen type safety
function getUser(id: string): User | null { ... }
// Can become:
function getUser(id: UserId): User { ... }  // ✅ Stronger types OK
```

---

## Error Handling

### Type Error States

```typescript
// ✅ Explicit error types
type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError };

type ApiError =
  | { type: 'network'; message: string }
  | { type: 'validation'; fields: Record<string, string> }
  | { type: 'notFound'; resource: string };
```

### Always Handle Errors

```typescript
// ❌ Ignoring errors
try {
  await saveUser(user);
} catch (e) {
  // Silent failure
}

// ✅ Explicit handling
try {
  await saveUser(user);
} catch (error) {
  if (error instanceof ValidationError) {
    return { success: false, errors: error.fields };
  }
  logger.error('Failed to save user', { error, userId: user.id });
  throw error;
}
```

### Use Zod for Validation

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

type User = z.infer<typeof UserSchema>;

function parseUser(data: unknown): User {
  return UserSchema.parse(data);
}
```

---

## Testing Requirements

### Tests for New Functionality

```typescript
// When adding new functions, include tests
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

// tests/format-currency.test.ts
describe('formatCurrency', () => {
  it('should format positive amounts', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });
});
```

### Maintain Coverage

```typescript
// ❌ Don't reduce test coverage
// ❌ Don't delete existing tests without reason

// ✅ Add tests for new code paths
// ✅ Update tests when behavior changes intentionally
```

---

## Code Organization

### Named Exports Only

```typescript
// ❌ Don't use default exports
export default function createUser() { ... }

// ✅ Use named exports
export function createUser() { ... }
export type { User, CreateUserInput };
```

### Collocate by Feature

```typescript
// ✅ Feature-based organization
src/
├── users/
│   ├── user-service.ts
│   ├── user-service.test.ts
│   ├── user-types.ts
│   └── user-validation.ts
├── orders/
│   └── ...
```

### Import Order

```typescript
// 1. External packages
import { z } from 'zod';
import { Hono } from 'hono';

// 2. Internal absolute imports
import { db } from '@/database';

// 3. Relative imports
import { validateUser } from './user-validation';
import type { User } from './user-types';
```

---

## Comments

### Self-Documenting Code

```typescript
// ❌ Bad: comment explains unclear code
// Check if user can edit
if (u.r === 1 && u.a && !u.d) { ... }

// ✅ Good: code is clear
const isAdmin = user.role === 'admin';
const isActive = user.isActive;
const isNotDeleted = !user.isDeleted;

if (isAdmin && isActive && isNotDeleted) { ... }
```

### Explain Why, Not What

```typescript
// ❌ Explains what (obvious from code)
// Increment retry count
retryCount += 1;

// ✅ Explains why (not obvious)
// Retry count starts at 1 because initial request counts as first attempt
retryCount += 1;
```

### JSDoc for Public APIs

```typescript
/**
 * Calculates order total including tax.
 *
 * @param items - Line items in the order
 * @param taxRate - Tax rate as decimal (0.1 = 10%)
 * @returns Total in cents
 */
export function calculateTotal(
  items: ReadonlyArray<LineItem>,
  taxRate: number
): number { ... }
```

---

## Ironclad Stack Specifics

### Hono Routes

```typescript
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import type { Bindings } from './types';

const app = new Hono<{ Bindings: Bindings }>()
  .get('/users/:id', async (c) => {
    const id = c.req.param('id');
    const user = await getUser(c.env.DB, id);
    return c.json(user);
  })
  .post('/users', zValidator('json', CreateUserSchema), async (c) => {
    const input = c.req.valid('json');
    const user = await createUser(c.env.DB, input);
    return c.json(user, 201);
  });
```

### Drizzle Queries

```typescript
import { eq } from 'drizzle-orm';
import { users } from './schema';

async function getUser(db: D1Database, id: string): Promise<User | null> {
  const result = await db
    .select()
    .from(users)
    .where(eq(users.id, id))
    .get();

  return result ?? null;
}
```

### Zod Schemas

```typescript
import { z } from 'zod';

export const CreateUserSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
});

export type CreateUserInput = z.infer<typeof CreateUserSchema>;
```

---

## Quick Reference

| Rule | Do | Don't |
|------|-----|-------|
| **Types** | `unknown`, narrow with guards | `any` |
| **Return types** | Explicit on exports | Implicit |
| **Enums** | `const` objects | `enum` |
| **Booleans** | `isActive`, `hasError` | `active`, `error` |
| **Functions** | Pure, single object arg | Side effects, many args |
| **Data** | Immutable, `Readonly` | Mutations |
| **Exports** | Named | Default |
| **Errors** | Typed, handled | Silent catches |
| **Tests** | Required for new code | Optional |
| **Comments** | Why, not what | Obvious explanations |

---

*Apply these rules consistently for high-quality TypeScript with Claude Code.*
*Last updated: 2025-12-31*
