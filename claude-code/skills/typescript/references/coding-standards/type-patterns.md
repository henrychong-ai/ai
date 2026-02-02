# TypeScript Type Patterns

Advanced type system patterns for type-safe, maintainable code.

---

## Type Safety Configuration

### Strict Mode (Required)

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true
  }
}
```

### Key Flags

| Flag | Effect |
|------|--------|
| `noUncheckedIndexedAccess` | Array access returns `T \| undefined` |
| `exactOptionalPropertyTypes` | Optional props can't be `undefined` unless explicit |
| `noImplicitOverride` | Require `override` keyword for inherited methods |

---

## Never Use `any`

### Use `unknown` Instead

```typescript
// ❌ Bad: any disables type checking
function parse(json: string): any {
  return JSON.parse(json);
}

// ✅ Good: unknown requires narrowing
function parse(json: string): unknown {
  return JSON.parse(json);
}

// Narrow before use
const data = parse('{"name": "foo"}');
if (isUser(data)) {
  console.log(data.name); // Now type-safe
}
```

### Type Guards for Narrowing

```typescript
// Custom type guard
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'name' in value &&
    typeof (value as User).name === 'string'
  );
}

// Zod for runtime validation (preferred)
import { z } from 'zod';

const UserSchema = z.object({
  name: z.string(),
  email: z.string().email(),
});

type User = z.infer<typeof UserSchema>;

function parseUser(data: unknown): User {
  return UserSchema.parse(data); // Throws if invalid
}
```

---

## Type Declarations

### Types vs Interfaces

```typescript
// Use `type` for:
// - Unions and intersections
// - Mapped types
// - Conditional types
// - Utility type compositions

type Status = 'pending' | 'active' | 'inactive';
type UserWithRole = User & { role: Role };
type Nullable<T> = T | null;

// Use `interface` for:
// - Object shapes that may be extended
// - Declaration merging (rare)
// - Class implementations

interface User {
  id: string;
  name: string;
  email: string;
}

interface AdminUser extends User {
  permissions: string[];
}
```

### Prefer Types for Consistency

Following mkosir's style guide, prefer `type` for all declarations:

```typescript
// ✅ Consistent: all types
type User = {
  id: string;
  name: string;
};

type AdminUser = User & {
  permissions: Array<string>;
};

type CreateUserInput = Pick<User, 'name'>;
```

---

## Generics

### Basic Generics

```typescript
// Generic function
function first<T>(items: Array<T>): T | undefined {
  return items[0];
}

// Generic with constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Generic with default
type Container<T = string> = {
  value: T;
};
```

### Descriptive Generic Names

```typescript
// ❌ Bad: single letters are unclear
function transform<T, U>(input: T, fn: (x: T) => U): U {
  return fn(input);
}

// ✅ Good: descriptive names with T prefix
function transform<TInput, TOutput>(
  input: TInput,
  fn: (x: TInput) => TOutput
): TOutput {
  return fn(input);
}

// Common patterns
type ApiResponse<TData, TError = Error> =
  | { success: true; data: TData }
  | { success: false; error: TError };
```

---

## Discriminated Unions

### Eliminating Optional Properties

```typescript
// ❌ Bad: optional properties lead to invalid states
type User = {
  type: 'guest' | 'member' | 'admin';
  name?: string;        // Only for member/admin
  permissions?: string[]; // Only for admin
};

// ✅ Good: discriminated union - each state is explicit
type User =
  | { type: 'guest' }
  | { type: 'member'; name: string }
  | { type: 'admin'; name: string; permissions: Array<string> };
```

### Exhaustive Switch

```typescript
type Action =
  | { type: 'increment'; amount: number }
  | { type: 'decrement'; amount: number }
  | { type: 'reset' };

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'increment':
      return state + action.amount;
    case 'decrement':
      return state - action.amount;
    case 'reset':
      return 0;
    default:
      // Exhaustiveness check - errors if a case is missing
      const _exhaustive: never = action;
      return state;
  }
}
```

---

## Const Assertions

### Immutable Constants

```typescript
// ❌ Bad: type is widened
const config = {
  api: 'https://api.example.com',
  timeout: 5000,
};
// Type: { api: string; timeout: number }

// ✅ Good: literal types preserved
const config = {
  api: 'https://api.example.com',
  timeout: 5000,
} as const;
// Type: { readonly api: "https://api.example.com"; readonly timeout: 5000 }
```

### Const Arrays for Union Types

```typescript
// ❌ Bad: enum generates runtime code
enum Status {
  Pending = 'pending',
  Active = 'active',
  Inactive = 'inactive',
}

// ✅ Good: const array + type extraction
const STATUSES = ['pending', 'active', 'inactive'] as const;
type Status = typeof STATUSES[number];
// Type: "pending" | "active" | "inactive"

// Validate at runtime
function isValidStatus(value: string): value is Status {
  return STATUSES.includes(value as Status);
}
```

### With `satisfies` for Type Checking

```typescript
// Ensures type compliance while preserving literal types
const routes = {
  home: '/',
  users: '/users',
  userDetail: '/users/:id',
} as const satisfies Record<string, string>;

// routes.home is typed as "/" not string
```

---

## Utility Types

### Built-in Utilities

```typescript
type User = {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
};

// Partial - all properties optional
type PartialUser = Partial<User>;

// Required - all properties required
type RequiredUser = Required<PartialUser>;

// Pick - select specific properties
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit - exclude properties
type CreateUserInput = Omit<User, 'id' | 'createdAt'>;

// Record - object with specific key/value types
type UserMap = Record<string, User>;

// Readonly - all properties readonly
type ImmutableUser = Readonly<User>;

// ReadonlyArray - immutable array
type UserList = ReadonlyArray<User>;
```

### Custom Utility Types

```typescript
// Make specific properties optional
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

type UserWithOptionalEmail = PartialBy<User, 'email'>;

// Make specific properties required
type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

// Deep partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Non-nullable properties
type NonNullableProperties<T> = {
  [P in keyof T]: NonNullable<T[P]>;
};
```

---

## Conditional Types

### Basic Conditional

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false
```

### Extract and Exclude

```typescript
type Status = 'pending' | 'active' | 'inactive' | 'deleted';

// Extract matching types
type ActiveStatus = Extract<Status, 'active' | 'pending'>;
// Type: "active" | "pending"

// Exclude matching types
type VisibleStatus = Exclude<Status, 'deleted'>;
// Type: "pending" | "active" | "inactive"
```

### Infer Keyword

```typescript
// Extract return type
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;

// Extract promise value
type Awaited<T> = T extends Promise<infer U> ? U : T;

// Extract array element type
type ElementOf<T> = T extends Array<infer E> ? E : never;

// Extract function parameters
type ParamsOf<T> = T extends (...args: infer P) => any ? P : never;
```

---

## Branded Types

### Type-Safe Identifiers

```typescript
// ❌ Bad: strings are interchangeable
function getUser(userId: string): User { ... }
function getOrder(orderId: string): Order { ... }

getUser(orderId); // Compiles but wrong!

// ✅ Good: branded types prevent mixing
type UserId = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

function createUserId(id: string): UserId {
  return id as UserId;
}

function getUser(userId: UserId): User { ... }
function getOrder(orderId: OrderId): Order { ... }

const userId = createUserId('user-123');
const orderId = createOrderId('order-456');

getUser(userId);  // ✅ OK
getUser(orderId); // ❌ Type error!
```

### Branded Primitives

```typescript
type Email = string & { readonly __brand: 'Email' };
type PositiveNumber = number & { readonly __brand: 'PositiveNumber' };

function validateEmail(input: string): Email {
  if (!input.includes('@')) {
    throw new Error('Invalid email');
  }
  return input as Email;
}

function validatePositive(input: number): PositiveNumber {
  if (input <= 0) {
    throw new Error('Must be positive');
  }
  return input as PositiveNumber;
}
```

---

## Template Literal Types

### String Pattern Enforcement

```typescript
// API routes
type ApiRoute = `/api/${string}`;
type UserRoute = `/api/users/${string}`;

// Version strings
type SemVer = `${number}.${number}.${number}`;

// CSS units
type CSSUnit = `${number}${'px' | 'rem' | 'em' | '%'}`;

// Event handlers
type EventHandler = `on${Capitalize<string>}`;
```

### Combining with Mapped Types

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type Setters<T> = {
  [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void;
};

type User = { name: string; age: number };
type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number }
```

---

## Type Imports and Exports

### Separate Type Imports

```typescript
// ✅ Good: explicit type imports
import type { User, Order } from './types';
import { createUser, updateUser } from './users';

// Enables proper tree-shaking
// Types are erased at compile time
```

### Inline Type Imports

```typescript
// Alternative syntax
import { createUser, type User } from './users';
```

---

## Common Anti-Patterns

### Avoid Type Assertions

```typescript
// ❌ Bad: bypasses type checking
const user = response.data as User;

// ✅ Good: validate at runtime
const user = UserSchema.parse(response.data);

// ✅ Good: use type guard
if (isUser(response.data)) {
  const user = response.data;
}
```

### Avoid Non-Null Assertions

```typescript
// ❌ Bad: ! assumes non-null
const name = user!.name;

// ✅ Good: handle the null case
const name = user?.name ?? 'Unknown';

// ✅ Good: narrow first
if (user) {
  const name = user.name;
}
```

### Avoid Over-Annotation

```typescript
// ❌ Bad: redundant type annotations
const name: string = 'John';
const users: Array<User> = [];
const double: (x: number) => number = (x) => x * 2;

// ✅ Good: let TypeScript infer
const name = 'John';
const users: Array<User> = []; // Array type needed for empty array
const double = (x: number) => x * 2; // Return type inferred
```

---

## Type Generation

### From Zod Schemas

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(['user', 'admin']),
  createdAt: z.date(),
});

// Derive type from schema
type User = z.infer<typeof UserSchema>;

// Input type (for creation)
const CreateUserSchema = UserSchema.omit({ id: true, createdAt: true });
type CreateUserInput = z.infer<typeof CreateUserSchema>;
```

### From API Contracts

```typescript
// OpenAPI → TypeScript
// Use: openapi-typescript

// GraphQL → TypeScript
// Use: graphql-codegen

// Database → TypeScript
// Drizzle: Types from schema definitions
// Prisma: prisma generate
```

---

*Companion to: style-guide.md, clean-code.md*
*Last updated: 2025-12-31*
