# Security Patterns for TypeScript/Node.js

Defensive patterns for preventing DoS attacks, uncatchable crashes, and input-based vulnerabilities in Node.js applications.

---

## Input Depth Limiting

### Background: CVE-2025-59466 (async_hooks Stack Overflow)

When `async_hooks` is enabled (by Next.js, React Server Components, or APM tools), stack overflow errors cause immediate process exit (code 7) instead of a catchable `RangeError`. Try/catch blocks cannot intercept this.

**Attack vector:** Deeply nested JSON (50,000+ levels) causes recursive processing to overflow the stack, crashing the process.

**Patched in:** Node.js 24.13.0+, 22.22.0+, 20.20.0+ (January 13, 2026)

**Reference:** [Node.js Security Release - January 2026](https://nodejs.org/en/blog/vulnerability/december-2025-security-releases)

Even with patched Node.js, depth limiting remains a defense-in-depth best practice.

---

### Iterative Depth Check (Stack-Safe)

Use this utility to validate JSON depth before processing. The function itself is iterative (not recursive) so it cannot trigger the vulnerability.

```typescript
/**
 * Check if an object's nesting depth exceeds the maximum allowed.
 * Uses iterative traversal to avoid stack overflow.
 *
 * @param obj - The object to check
 * @param maxDepth - Maximum allowed depth (default: 50)
 * @returns true if depth exceeds limit, false if within limit
 */
export function exceedsMaxDepth(obj: unknown, maxDepth = 50): boolean {
  const stack: Array<{ value: unknown; depth: number }> = [
    { value: obj, depth: 0 },
  ];

  while (stack.length > 0) {
    const { value, depth } = stack.pop()!;

    if (depth > maxDepth) return true;
    if (typeof value !== 'object' || value === null) continue;

    for (const child of Object.values(value)) {
      stack.push({ value: child, depth: depth + 1 });
    }
  }

  return false;
}
```

**Usage:**
```typescript
const userInput = await request.json();

if (exceedsMaxDepth(userInput, 100)) {
  return new Response('Request body nesting too deep', { status: 400 });
}

// Safe to process
processData(userInput);
```

---

### Hono Middleware for JSON Depth Protection

```typescript
// middleware/json-depth-limit.ts
import { createMiddleware } from 'hono/factory';

const MAX_JSON_DEPTH = 50;

function exceedsMaxDepth(obj: unknown, maxDepth: number): boolean {
  const stack: Array<{ value: unknown; depth: number }> = [
    { value: obj, depth: 0 },
  ];

  while (stack.length > 0) {
    const { value, depth } = stack.pop()!;
    if (depth > maxDepth) return true;
    if (typeof value !== 'object' || value === null) continue;

    for (const child of Object.values(value)) {
      stack.push({ value: child, depth: depth + 1 });
    }
  }

  return false;
}

export const jsonDepthLimit = createMiddleware(async (c, next) => {
  const contentType = c.req.header('content-type');

  if (contentType?.includes('application/json')) {
    try {
      const body = await c.req.json();

      if (exceedsMaxDepth(body, MAX_JSON_DEPTH)) {
        return c.json(
          { error: 'Request body nesting exceeds maximum depth' },
          400
        );
      }

      // Store parsed body for downstream handlers
      c.set('jsonBody', body);
    } catch {
      return c.json({ error: 'Invalid JSON' }, 400);
    }
  }

  await next();
});
```

**Usage in Hono app:**
```typescript
import { Hono } from 'hono';
import { jsonDepthLimit } from './middleware/json-depth-limit';

const app = new Hono();

// Apply globally
app.use('*', jsonDepthLimit);

// Or apply to specific routes
app.use('/api/*', jsonDepthLimit);
```

---

### Depth-Limited Recursive Processing

When you must process nested data recursively, always include depth guards:

```typescript
// VULNERABLE - unbounded recursion
function processData(data: unknown): unknown {
  if (Array.isArray(data)) {
    return data.map(processData); // No depth limit!
  }
  if (typeof data === 'object' && data !== null) {
    return Object.fromEntries(
      Object.entries(data).map(([k, v]) => [k, processData(v)])
    );
  }
  return data;
}

// SAFE - depth-limited recursion
function processDataSafe(data: unknown, depth = 0, maxDepth = 100): unknown {
  if (depth > maxDepth) {
    throw new Error(`Maximum nesting depth (${maxDepth}) exceeded`);
  }

  if (Array.isArray(data)) {
    return data.map((item) => processDataSafe(item, depth + 1, maxDepth));
  }
  if (typeof data === 'object' && data !== null) {
    return Object.fromEntries(
      Object.entries(data).map(([k, v]) => [
        k,
        processDataSafe(v, depth + 1, maxDepth),
      ])
    );
  }
  return data;
}
```

---

### Zod Depth-Limited Schemas

For recursive Zod schemas, implement depth limiting:

```typescript
import { z } from 'zod';

// VULNERABLE - unbounded recursive schema
const UnsafeNestedSchema: z.ZodType<NestedData> = z.lazy(() =>
  z.object({
    value: z.string(),
    children: z.array(UnsafeNestedSchema).optional(),
  })
);

// SAFE - depth-limited recursive schema
function createNestedSchema(maxDepth: number) {
  const createLevel = (depth: number): z.ZodTypeAny => {
    if (depth >= maxDepth) {
      // Leaf level - no more nesting allowed
      return z.object({
        value: z.string(),
      });
    }

    return z.object({
      value: z.string(),
      children: z
        .array(z.lazy(() => createLevel(depth + 1)))
        .max(100) // Also limit array size
        .optional(),
    });
  };

  return createLevel(0);
}

const SafeNestedSchema = createNestedSchema(20);
```

**Alternative - Zod refinement for depth check:**
```typescript
const JsonInputSchema = z.unknown().refine(
  (data) => !exceedsMaxDepth(data, 50),
  { message: 'Input nesting exceeds maximum depth' }
);
```

---

## Best Practices Summary

### Always Apply These Patterns When:

1. **Processing user-submitted JSON** - API endpoints, webhooks, form data
2. **Parsing configuration files** - Especially from untrusted sources
3. **Recursive data transformations** - Tree traversal, nested object mapping
4. **Using libraries that enable async_hooks** - Next.js, APM tools, OpenTelemetry

### Defense in Depth Layers:

| Layer | Protection |
|-------|------------|
| **Node.js version** | Use 24.13.0+ or 22.22.0+ (patched) |
| **Middleware** | JSON depth limit before parsing |
| **Zod schemas** | Depth-limited recursive types |
| **Processing functions** | Depth parameter with guards |

### Recommended Limits:

| Context | Max Depth | Rationale |
|---------|-----------|-----------|
| API JSON body | 50 | Typical REST payloads rarely exceed 10 |
| Configuration files | 20 | Config should be flat |
| Tree data structures | 100 | Document trees, org charts |
| GraphQL responses | 30 | Query depth limiting |

---

## Related Vulnerabilities

| CVE | Description | Mitigation |
|-----|-------------|------------|
| CVE-2025-59466 | async_hooks stack overflow DoS | Update Node.js + depth limiting |
| ReDoS | Regular expression DoS | Use safe-regex, limit input length |
| Prototype pollution | Object injection | Use `Object.create(null)`, validate keys |

---

*Last updated: 2026-01-14*
