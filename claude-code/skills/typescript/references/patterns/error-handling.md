# Error Handling Patterns

Type-safe error handling for predictable, maintainable code.

---

## Philosophy

1. **Errors are data** - Type them explicitly, don't just throw
2. **Fail fast** - Validate at boundaries, catch errors early
3. **Provide context** - Error messages should be actionable
4. **Distinguish error types** - Expected errors vs unexpected exceptions

---

## Result Pattern

### Basic Result Type

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// Usage
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) {
    return { success: false, error: 'Division by zero' };
  }
  return { success: true, data: a / b };
}

// Handling
const result = divide(10, 2);
if (result.success) {
  console.log(result.data); // 5
} else {
  console.error(result.error);
}
```

### Typed Error Variants

```typescript
type ApiError =
  | { type: 'network'; message: string }
  | { type: 'validation'; fields: Record<string, string> }
  | { type: 'auth'; reason: 'expired' | 'invalid' }
  | { type: 'notFound'; resource: string; id: string };

type ApiResult<T> = Result<T, ApiError>;

function fetchUser(id: string): Promise<ApiResult<User>> {
  // Implementation
}

// Exhaustive handling
const result = await fetchUser('123');
if (!result.success) {
  switch (result.error.type) {
    case 'network':
      return showNetworkError(result.error.message);
    case 'validation':
      return showFieldErrors(result.error.fields);
    case 'auth':
      return redirectToLogin();
    case 'notFound':
      return show404(result.error.resource);
  }
}
```

### Result Utilities

```typescript
// Create success result
function ok<T>(data: T): Result<T, never> {
  return { success: true, data };
}

// Create error result
function err<E>(error: E): Result<never, E> {
  return { success: false, error };
}

// Map over successful result
function mapResult<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => U
): Result<U, E> {
  if (result.success) {
    return ok(fn(result.data));
  }
  return result;
}

// Chain results (flatMap)
function flatMapResult<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => Result<U, E>
): Result<U, E> {
  if (result.success) {
    return fn(result.data);
  }
  return result;
}

// Usage
const result = ok(5)
  |> mapResult(%, x => x * 2)      // ok(10)
  |> flatMapResult(%, x =>
       x > 5 ? ok(x) : err('too small')
     );                             // ok(10)
```

---

## Zod Validation

### Schema-First Validation

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email format'),
  age: z.number().int().min(0).max(150),
});

type User = z.infer<typeof UserSchema>;
```

### Safe Parsing (Returns Result)

```typescript
// safeParse returns { success, data } or { success, error }
function parseUser(input: unknown): Result<User, z.ZodError> {
  const result = UserSchema.safeParse(input);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, error: result.error };
}

// Usage
const result = parseUser(requestBody);
if (!result.success) {
  const errors = result.error.flatten().fieldErrors;
  return Response.json({ errors }, { status: 400 });
}
const user = result.data;
```

### Error Formatting

```typescript
function formatZodErrors(error: z.ZodError): Record<string, string> {
  const flattened = error.flatten();
  const errors: Record<string, string> = {};

  for (const [field, messages] of Object.entries(flattened.fieldErrors)) {
    if (messages && messages.length > 0) {
      errors[field] = messages[0];
    }
  }

  return errors;
}

// { email: "Invalid email format", age: "Expected number" }
```

### Custom Error Messages

```typescript
const CreateOrderSchema = z.object({
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().positive(),
  })).min(1, 'Order must have at least one item'),

  shippingAddress: z.object({
    street: z.string().min(1),
    city: z.string().min(1),
    postalCode: z.string().regex(/^\d{5}$/, 'Invalid postal code'),
  }),
}).refine(
  data => data.items.every(item => item.quantity <= 100),
  { message: 'Maximum quantity per item is 100' }
);
```

---

## Custom Error Classes

### Base Application Error

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AppError';
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      error: this.code,
      message: this.message,
      details: this.details,
    };
  }
}
```

### Specific Error Types

```typescript
class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(
      `${resource} not found: ${id}`,
      'NOT_FOUND',
      404,
      { resource, id }
    );
    this.name = 'NotFoundError';
  }
}

class ValidationError extends AppError {
  constructor(message: string, fields?: Record<string, string>) {
    super(message, 'VALIDATION_ERROR', 400, { fields });
    this.name = 'ValidationError';
  }
}

class UnauthorizedError extends AppError {
  constructor(reason: string = 'Authentication required') {
    super(reason, 'UNAUTHORIZED', 401);
    this.name = 'UnauthorizedError';
  }
}

class ForbiddenError extends AppError {
  constructor(action: string) {
    super(`Not allowed to ${action}`, 'FORBIDDEN', 403);
    this.name = 'ForbiddenError';
  }
}

class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 'CONFLICT', 409);
    this.name = 'ConflictError';
  }
}
```

### Type Guard

```typescript
function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}
```

---

## Error Boundaries

### Hono Error Middleware

```typescript
import { Hono } from 'hono';
import { HTTPException } from 'hono/http-exception';

const app = new Hono();

// Global error handler
app.onError((error, c) => {
  console.error(error);

  // Handle custom app errors
  if (isAppError(error)) {
    return c.json(error.toJSON(), error.statusCode);
  }

  // Handle Hono HTTP exceptions
  if (error instanceof HTTPException) {
    return c.json(
      { error: 'HTTP_ERROR', message: error.message },
      error.status
    );
  }

  // Handle Zod errors
  if (error instanceof z.ZodError) {
    return c.json(
      { error: 'VALIDATION_ERROR', fields: formatZodErrors(error) },
      400
    );
  }

  // Unknown error - don't leak details
  return c.json(
    { error: 'INTERNAL_ERROR', message: 'An unexpected error occurred' },
    500
  );
});
```

### React Error Boundary

```typescript
import { Component, ReactNode } from 'react';

type Props = {
  children: ReactNode;
  fallback: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
};

type State = {
  hasError: boolean;
  error?: Error;
};

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />} onError={logError}>
  <App />
</ErrorBoundary>
```

---

## Async Error Handling

### try-catch Pattern

```typescript
async function fetchUserSafe(id: string): Promise<Result<User, ApiError>> {
  try {
    const response = await fetch(`/api/users/${id}`);

    if (!response.ok) {
      if (response.status === 404) {
        return err({ type: 'notFound', resource: 'user', id });
      }
      if (response.status === 401) {
        return err({ type: 'auth', reason: 'expired' });
      }
      return err({ type: 'network', message: `HTTP ${response.status}` });
    }

    const data = await response.json();
    const parsed = UserSchema.safeParse(data);

    if (!parsed.success) {
      return err({
        type: 'validation',
        fields: formatZodErrors(parsed.error),
      });
    }

    return ok(parsed.data);
  } catch (error) {
    return err({
      type: 'network',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}
```

### Promise.allSettled

Handle multiple async operations gracefully:

```typescript
async function fetchAllUsers(ids: Array<string>): Promise<{
  succeeded: Array<User>;
  failed: Array<{ id: string; error: string }>;
}> {
  const results = await Promise.allSettled(
    ids.map(id => fetchUser(id))
  );

  const succeeded: Array<User> = [];
  const failed: Array<{ id: string; error: string }> = [];

  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      succeeded.push(result.value);
    } else {
      failed.push({
        id: ids[index],
        error: result.reason?.message ?? 'Unknown error',
      });
    }
  });

  return { succeeded, failed };
}
```

### Retry with Backoff

```typescript
type RetryOptions = {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffFactor: number;
};

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxAttempts, initialDelay, maxDelay, backoffFactor } = options;
  let lastError: Error | undefined;
  let delay = initialDelay;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxAttempts) break;

      await sleep(delay);
      delay = Math.min(delay * backoffFactor, maxDelay);
    }
  }

  throw lastError;
}

// Usage
const user = await withRetry(
  () => fetchUser(id),
  { maxAttempts: 3, initialDelay: 1000, maxDelay: 10000, backoffFactor: 2 }
);
```

---

## Best Practices

### 1. Validate at Boundaries

```typescript
// API boundary
app.post('/users', async (c) => {
  const body = await c.req.json();
  const input = CreateUserSchema.parse(body); // Throws if invalid
  return c.json(await createUser(input));
});

// Internal functions trust their input
function createUser(input: CreateUserInput): Promise<User> {
  // No validation needed - already validated at boundary
  return db.users.create(input);
}
```

### 2. Don't Catch Everything

```typescript
// ❌ Bad: swallows all errors
try {
  await doSomething();
} catch (e) {
  // Silently fails
}

// ✅ Good: handle specific cases
try {
  await doSomething();
} catch (error) {
  if (error instanceof NetworkError) {
    return showRetryDialog();
  }
  if (error instanceof ValidationError) {
    return showFieldErrors(error.fields);
  }
  throw error; // Re-throw unexpected errors
}
```

### 3. Provide Context

```typescript
// ❌ Bad: no context
throw new Error('Failed');

// ✅ Good: actionable message
throw new NotFoundError('user', userId);
// "User not found: user-123"

// ✅ Good: include relevant data
throw new ValidationError('Invalid order', {
  items: 'At least one item required',
  shippingAddress: 'Missing postal code',
});
```

### 4. Log Appropriately

```typescript
app.onError((error, c) => {
  // Log full error for debugging
  console.error({
    error: error.message,
    stack: error.stack,
    path: c.req.path,
    method: c.req.method,
  });

  // Return safe message to client
  if (isAppError(error)) {
    return c.json(error.toJSON(), error.statusCode);
  }

  return c.json({ error: 'Internal error' }, 500);
});
```

---

## Libraries

| Library | Use Case |
|---------|----------|
| **zod** | Schema validation with type inference |
| **neverthrow** | Full Result/Option implementation |
| **effect** | Comprehensive effect system |
| **fp-ts** | Functional programming utilities |

---

*Companion to: async-patterns.md, api-patterns.md*
*Last updated: 2025-12-31*
