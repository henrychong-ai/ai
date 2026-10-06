# Security Patterns for TypeScript/Node.js

Defensive patterns for preventing DoS attacks, uncatchable crashes, and input-based vulnerabilities in Node.js applications.

---

## Input Depth Limiting

### Background: CVE-2025-59466 (async_hooks Stack Overflow)

When `async_hooks` is enabled (by Next.js, React Server Components, or APM tools), stack overflow errors cause immediate process exit (code 7) instead of a catchable `RangeError`. Try/catch blocks cannot intercept this.

**Attack vector:** Deeply nested JSON (50,000+ levels) causes recursive processing to overflow the stack, crashing the process.

**Patched in:** Node.js 24.13.0, 22.22.0 and 20.20.0 (January 2026). Later security releases supersede these; run the latest patch of a supported line (`../tech-stack/version-policy.md`).

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
import type { MiddlewareHandler } from 'hono';
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

// Annotated: an exported middleware needs a nameable type when the tsconfig emits declarations
export const jsonDepthLimit: MiddlewareHandler = createMiddleware(async (c, next) => {
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

  return next(); // `return` keeps noImplicitReturns satisfied
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
  const createLevel = (depth: number): z.ZodType => {
    if (depth >= maxDepth) {
      // Leaf level: strictObject REJECTS deeper `children` (z.object would silently strip them)
      return z.strictObject({
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
  { error: 'Input nesting exceeds maximum depth' }
);
```

---

## Storage and Remote Reads Are Trust Boundaries

Data read back from storage or from another service is input, even when your own code wrote it. Typed reads hide that:

- `kv.get<T>(key, 'json')`, `(await object.json()) as T`, `(await res.json()) as T` and `JSON.parse(text) as T` are unchecked casts. TypeScript trusts the type argument, and type-aware lint rules such as `no-unsafe-assignment` do not flag them, because the call already returns `T`.
- A runtime JSON parser's `SyntaxError` can quote part of the stored value. If stored values hold secrets or personal data, a parse failure copies them into logs.

Pattern:

1. Read as text (or `unknown`), parse locally inside `try`/`catch`, and validate with a Zod schema, or a small hand-written guard on hot paths (keep it in step with the schema with a parity test).
2. Return a three-way result so every caller handles each case deliberately:

```typescript
type BoundaryRead<T> =
  | { status: 'missing' }
  | { status: 'ok'; value: T }
  | { status: 'invalid' };

export async function readKvJson<T>(
  kv: KVNamespace,
  key: string,
  schema: z.ZodType<T>,
): Promise<BoundaryRead<T>> {
  const text = await kv.get(key); // text read, never 'json'
  if (text === null) return { status: 'missing' };
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    return { status: 'invalid' }; // the parser's message may quote the value: drop it
  }
  const parsed = schema.safeParse(raw);
  return parsed.success ? { status: 'ok', value: parsed.data } : { status: 'invalid' };
}
```

3. Log an invalid record with fixed text and the key's category, never the stored value or the parser's message.
4. Decide what `invalid` means at each call site. A record that carries authorisation, such as an access-restricted entry overlaying a broader public rule, must fail closed: refuse the request rather than fall through to the broader rule.
5. Enforce the rule with a small CI gate script that rejects the typed-read patterns above in production code, with a `// boundary-ok: <reason>` escape hatch for vetted cases. Lint rules alone do not catch them.

Tests: for each boundary, store an invalid value and assert the documented behaviour, and that no stored content reaches a log line or an error response.

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
| **Node.js version** | Latest patch of a supported LTS line (`../tech-stack/version-policy.md`) |
| **Middleware** | JSON depth check right after parsing, before any recursive processing |
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

*Companion to: api-patterns.md, error-handling.md.*
