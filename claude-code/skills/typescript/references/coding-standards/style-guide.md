# TypeScript Style Guide

Concise conventions for consistent, maintainable TypeScript code. Based on [mkosir/typescript-style-guide](https://github.com/mkosir/typescript-style-guide).

---

## Core Principles

1. **Consistency is key** - Follow conventions uniformly
2. **Enforce with tooling** - ESLint, Prettier, TypeScript compiler
3. **Functional-first** - Pure functions, immutability, composition
4. **Type safety** - Leverage TypeScript's full power

---

## Naming Conventions

### Variables

| Type | Convention | Example |
|------|------------|---------|
| Local variables | camelCase | `products`, `userList` |
| Boolean variables | `is*`, `has*`, `should*`, `can*`, `will*` | `isActive`, `hasPermission` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `API_URL` |
| Object/Array constants | Singular, PascalCase with `as const` | `Color`, `Status` |

```typescript
// Variables
const userCount = 10;
const filteredProducts = products.filter(p => p.active);

// Booleans
const isLoading = true;
const hasError = false;
const shouldRefresh = lastUpdate < threshold;
const canEdit = user.role === 'admin';
const willExpire = expiresAt < Date.now();

// Constants
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';

// Const objects
const Status = {
  Pending: 'pending',
  Active: 'active',
  Inactive: 'inactive',
} as const;
```

### Functions

| Context | Convention | Example |
|---------|------------|---------|
| Functions | camelCase, verb-first | `getUser`, `calculateTotal` |
| Predicates | `is*`, `has*`, `should*` | `isValid`, `hasAccess` |

```typescript
function getUserById(id: string): User { ... }
function calculateTotalWithTax(items: Array<Item>): number { ... }
function formatCurrency(amount: number): string { ... }

function isValidEmail(email: string): boolean { ... }
function hasPermission(user: User, action: string): boolean { ... }
```

### Types

| Type | Convention | Example |
|------|------------|---------|
| Type aliases | PascalCase | `User`, `OrderStatus` |
| Generics | T + descriptive name | `TRequest`, `TResponse` |

```typescript
type User = { id: string; name: string };
type OrderStatus = 'pending' | 'shipped' | 'delivered';
type ApiResponse<TData> = { success: true; data: TData };
```

### Files and Directories

| Type | Convention | Example |
|------|------------|---------|
| Directories | kebab-case | `user-management/`, `api-clients/` |
| Files | kebab-case | `user-service.ts`, `api-client.ts` |
| React components | PascalCase | `UserProfile.tsx`, `OrderList.tsx` |
| Test files | `*.test.ts` | `user-service.test.ts` |

### Acronyms

Treat acronyms as words - capitalize only first letter:

```typescript
// ✅ Good
type HttpClient = ...
function getApiUrl(): string { ... }
const userId = 'abc';
type JsonResponse = ...

// ❌ Bad
type HTTPClient = ...
function getAPIURL(): string { ... }
const userID = 'abc';
type JSONResponse = ...
```

### Avoid Abbreviations

Use full words unless universally understood:

```typescript
// ❌ Bad
const usr = getUsr();
const btn = document.querySelector('.btn');
const idx = arr.findIndex(x => x.active);

// ✅ Good
const user = getUser();
const button = document.querySelector('.button');
const index = items.findIndex(item => item.active);

// ✅ Acceptable abbreviations
const id = user.id;       // Universally understood
const url = config.apiUrl;
const api = createApiClient();
```

---

## Type Declarations

### Use `type` Over `interface`

For consistency, use `type` for all type declarations:

```typescript
// ✅ Preferred: type alias
type User = {
  id: string;
  name: string;
  email: string;
};

type CreateUserInput = Omit<User, 'id'>;

// Use interface only for:
// - Declaration merging (rare)
// - Extending third-party types
```

### Array Syntax

Use generic syntax for clarity:

```typescript
// ✅ Good: generic syntax
type Users = Array<User>;
type ReadonlyUsers = ReadonlyArray<User>;

// ❌ Avoid: bracket syntax
type Users = User[];
type ReadonlyUsers = readonly User[];
```

### No Enums

Use const objects instead:

```typescript
// ❌ Bad: enum
enum Status {
  Pending = 'pending',
  Active = 'active',
  Inactive = 'inactive',
}

// ✅ Good: const object
const Status = {
  Pending: 'pending',
  Active: 'active',
  Inactive: 'inactive',
} as const;

type Status = typeof Status[keyof typeof Status];
// Type: "pending" | "active" | "inactive"
```

### Separate Type Imports

```typescript
// ✅ Good: explicit type imports
import type { User, Order } from './types';
import { createUser, updateUser } from './users';

// Also acceptable: inline type imports
import { createUser, type User } from './users';
```

---

## Functions

### Single Object Argument

Use options object instead of multiple parameters:

```typescript
// ❌ Bad: multiple parameters
function createUser(
  name: string,
  email: string,
  role: string,
  department?: string
): User { ... }

// ✅ Good: options object
type CreateUserInput = {
  name: string;
  email: string;
  role: string;
  department?: string;
};

function createUser(input: CreateUserInput): User { ... }

// Exception: single primitive argument is fine
function getUserById(id: string): User { ... }
```

### Explicit Return Types

Always declare return types for public functions:

```typescript
// ✅ Good: explicit return type
function calculateTotal(items: Array<Item>): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Internal helper functions can use inference
const double = (n: number) => n * 2;
```

### Pure Functions

Prefer stateless, side-effect-free functions:

```typescript
// ❌ Bad: side effects
let total = 0;
function addToTotal(amount: number): void {
  total += amount;  // Modifies external state
}

// ✅ Good: pure function
function add(a: number, b: number): number {
  return a + b;
}

const total = items.reduce((sum, item) => add(sum, item.price), 0);
```

---

## Immutability

### Use Readonly

```typescript
// Readonly properties
type User = {
  readonly id: string;
  readonly createdAt: Date;
  name: string;  // Mutable if needed
};

// Readonly arrays
function processItems(items: ReadonlyArray<Item>): void {
  // Cannot modify items
}

// Readonly parameters
function updateUser(user: Readonly<User>, updates: Partial<User>): User {
  return { ...user, ...updates };
}
```

### Const Assertions

```typescript
// ✅ Immutable object
const config = {
  api: 'https://api.example.com',
  timeout: 5000,
} as const;

// ✅ Immutable array (for union types)
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number];

// ✅ With satisfies for type checking
const routes = {
  home: '/',
  users: '/users',
  settings: '/settings',
} as const satisfies Record<string, string>;
```

---

## Null vs Undefined

| Value | Use When |
|-------|----------|
| `null` | Explicit "no value" (intentionally empty) |
| `undefined` | Missing, excluded, or unset |

```typescript
// null: intentionally empty
function findUser(id: string): User | null {
  const user = db.find(id);
  return user ?? null;  // Explicitly no result
}

// undefined: optional/missing
type CreateUserInput = {
  name: string;
  email: string;
  phone?: string;  // Optional = may be undefined
};
```

---

## Code Organization

### Collocate by Feature

Organize code by feature, not by type:

```typescript
// ✅ Good: feature-based
src/
├── users/
│   ├── user-service.ts
│   ├── user-service.test.ts
│   ├── user-types.ts
│   └── user-validation.ts
├── orders/
│   ├── order-service.ts
│   └── ...
└── common/
    └── utils/

// ❌ Bad: type-based
src/
├── services/
│   ├── user-service.ts
│   └── order-service.ts
├── types/
│   ├── user-types.ts
│   └── order-types.ts
└── tests/
    └── ...
```

### Named Exports Only

```typescript
// ✅ Good: named exports
export function createUser() { ... }
export type User = { ... };

// ❌ Bad: default exports
export default function createUser() { ... }
```

**Why:**
- Named exports enable tree-shaking
- Consistent import names across codebase
- Easier refactoring
- Better IDE autocomplete

### Import Order

```typescript
// 1. External packages
import { z } from 'zod';
import { Hono } from 'hono';

// 2. Internal absolute imports
import { db } from '@/database';
import { logger } from '@/utils/logger';

// 3. Relative imports
import { validateUser } from './user-validation';
import type { User } from './user-types';

// Use tooling to auto-sort (prettier-plugin-sort-imports)
```

---

## React Conventions

### Component Naming

```typescript
// PascalCase for components
function UserProfile({ user }: UserProfileProps) { ... }
function OrderList({ orders }: OrderListProps) { ... }

// Props type: [ComponentName]Props
type UserProfileProps = {
  user: User;
  onEdit?: (user: User) => void;
};
```

### Props Pattern

```typescript
// Use typed destructured parameters
function UserCard({ user, onDelete }: UserCardProps) {
  return <div>{user.name}</div>;
}

// ❌ Avoid React.FC
const UserCard: React.FC<UserCardProps> = ({ user }) => { ... }
```

### Event Handlers

```typescript
// Props: on* prefix
type ButtonProps = {
  onClick: () => void;
  onHover?: () => void;
};

// Handlers: handle* prefix
function UserForm() {
  const handleSubmit = (event: FormEvent) => { ... };
  const handleNameChange = (value: string) => { ... };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Hooks

```typescript
// camelCase with use prefix
function useUserData(id: string) { ... }
function useLocalStorage<T>(key: string) { ... }

// Return objects, not arrays (except useState pattern)
function useUser(id: string) {
  return {
    user,
    isLoading,
    error,
    refetch,
  };
}
```

---

## Comments

### Self-Documenting Code

```typescript
// ❌ Bad: comment explains unclear code
// Check if user can access admin features
if (u.r === 1 && u.a && !u.d) { ... }

// ✅ Good: code is self-explanatory
const isAdmin = user.role === 'admin';
const isActive = user.isActive;
const isNotDeleted = !user.isDeleted;

if (isAdmin && isActive && isNotDeleted) { ... }
```

### Explain Why, Not What

```typescript
// ❌ Bad: explains what (obvious)
// Increment retry count
retryCount += 1;

// ✅ Good: explains why (not obvious)
// Start at 1 because initial request counts as first attempt
retryCount += 1;
```

### TSDoc for APIs

```typescript
/**
 * Calculates order total including tax and discounts.
 *
 * @param items - Line items in the order
 * @param taxRate - Tax rate as decimal (0.1 = 10%)
 * @returns Total in cents
 *
 * @example
 * const total = calculateTotal(items, 0.1);
 */
function calculateTotal(
  items: ReadonlyArray<LineItem>,
  taxRate: number
): number { ... }
```

---

## Summary

| Category | Convention |
|----------|------------|
| Variables | camelCase, descriptive |
| Booleans | `is*`, `has*`, `should*`, `can*` |
| Constants | SCREAMING_SNAKE_CASE |
| Functions | camelCase, verb-first |
| Types | PascalCase |
| Generics | T + descriptive name |
| Files | kebab-case |
| Components | PascalCase |
| Directories | kebab-case |
| Acronyms | Capitalize first letter only |
| Exports | Named only, no defaults |
| Arrays | `Array<T>` syntax |
| Enums | ❌ Use const objects |
| any | ❌ Use unknown |

---

*Based on: [mkosir/typescript-style-guide](https://github.com/mkosir/typescript-style-guide)*
*Companion to: type-patterns.md, clean-code.md*
*Last updated: 2025-12-31*
