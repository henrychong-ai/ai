# Async Patterns

Patterns for handling asynchronous operations in TypeScript.

---

## Async/Await Best Practices

### Always Use Async/Await

```typescript
// ❌ Bad: mixing .then() and await
async function getUser(id: string) {
  return fetch(`/api/users/${id}`)
    .then(res => res.json())
    .then(data => data.user);
}

// ✅ Good: consistent async/await
async function getUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  return data.user;
}
```

### Explicit Return Types

```typescript
// ✅ Always annotate async function return types
async function fetchUsers(): Promise<Array<User>> {
  const response = await fetch('/api/users');
  return response.json();
}

async function saveUser(user: User): Promise<void> {
  await db.users.save(user);
}
```

### Error Handling

```typescript
async function fetchData(): Promise<Result<Data, Error>> {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) {
      return { success: false, error: new Error(`HTTP ${response.status}`) };
    }
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error : new Error('Unknown error'),
    };
  }
}
```

---

## Concurrency Patterns

### Promise.all (Parallel Execution)

Execute multiple promises in parallel, fail if any fails:

```typescript
// All succeed or all fail
async function fetchUserData(userId: string) {
  const [user, orders, preferences] = await Promise.all([
    fetchUser(userId),
    fetchOrders(userId),
    fetchPreferences(userId),
  ]);

  return { user, orders, preferences };
}
```

### Promise.allSettled (Graceful Parallel)

Execute in parallel, handle individual failures:

```typescript
async function fetchMultipleUsers(ids: Array<string>) {
  const results = await Promise.allSettled(
    ids.map(id => fetchUser(id))
  );

  return results.map((result, index) => ({
    id: ids[index],
    status: result.status,
    data: result.status === 'fulfilled' ? result.value : undefined,
    error: result.status === 'rejected' ? result.reason : undefined,
  }));
}
```

### Promise.race (First to Complete)

Return first promise to resolve/reject:

```typescript
// Timeout pattern
async function fetchWithTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error('Timeout')), timeoutMs);
  });

  return Promise.race([promise, timeout]);
}

// Usage
const user = await fetchWithTimeout(fetchUser(id), 5000);
```

### Promise.any (First Success)

Return first promise to succeed:

```typescript
// Try multiple sources, use first that works
async function fetchFromAnySource<T>(
  sources: Array<() => Promise<T>>
): Promise<T> {
  return Promise.any(sources.map(source => source()));
}

// Usage
const data = await fetchFromAnySource([
  () => fetch('https://primary.api/data').then(r => r.json()),
  () => fetch('https://backup.api/data').then(r => r.json()),
  () => fetch('https://fallback.api/data').then(r => r.json()),
]);
```

---

## Sequential Execution

### When Order Matters

```typescript
// Process items one at a time
async function processSequentially<T, R>(
  items: Array<T>,
  processor: (item: T) => Promise<R>
): Promise<Array<R>> {
  const results: Array<R> = [];

  for (const item of items) {
    const result = await processor(item);
    results.push(result);
  }

  return results;
}

// Usage
const processed = await processSequentially(users, async (user) => {
  await notifyUser(user);
  return { userId: user.id, notified: true };
});
```

### Reduce Pattern

```typescript
// Chain async operations
async function processWithAccumulator<T>(
  items: Array<T>,
  processor: (acc: number, item: T) => Promise<number>,
  initial: number
): Promise<number> {
  return items.reduce(
    async (accPromise, item) => {
      const acc = await accPromise;
      return processor(acc, item);
    },
    Promise.resolve(initial)
  );
}
```

---

## Controlled Concurrency

### Limiting Parallel Operations

```typescript
async function mapWithConcurrency<T, R>(
  items: Array<T>,
  mapper: (item: T) => Promise<R>,
  concurrency: number
): Promise<Array<R>> {
  const results: Array<R> = [];
  const executing: Set<Promise<void>> = new Set();

  for (const item of items) {
    const promise = (async () => {
      const result = await mapper(item);
      results.push(result);
    })();

    executing.add(promise);
    promise.finally(() => executing.delete(promise));

    if (executing.size >= concurrency) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
}

// Usage: process 100 items, max 5 at a time
const results = await mapWithConcurrency(
  items,
  processItem,
  5
);
```

### Batch Processing

```typescript
function chunk<T>(array: Array<T>, size: number): Array<Array<T>> {
  const chunks: Array<Array<T>> = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

async function processBatches<T, R>(
  items: Array<T>,
  processor: (item: T) => Promise<R>,
  batchSize: number
): Promise<Array<R>> {
  const batches = chunk(items, batchSize);
  const results: Array<R> = [];

  for (const batch of batches) {
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
  }

  return results;
}
```

---

## Cancellation

### AbortController

```typescript
async function fetchWithAbort(
  url: string,
  signal?: AbortSignal
): Promise<Response> {
  const response = await fetch(url, { signal });
  return response;
}

// Usage
const controller = new AbortController();

// Start request
const promise = fetchWithAbort('/api/data', controller.signal);

// Cancel if needed
controller.abort();

// Handle cancellation
try {
  const response = await promise;
} catch (error) {
  if (error instanceof DOMException && error.name === 'AbortError') {
    console.log('Request was cancelled');
  } else {
    throw error;
  }
}
```

### Timeout with AbortController

```typescript
function fetchWithTimeout(url: string, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  return fetch(url, { signal: controller.signal }).finally(() => {
    clearTimeout(timeoutId);
  });
}
```

### Cancellable Async Operation

```typescript
type CancellablePromise<T> = Promise<T> & { cancel: () => void };

function makeCancellable<T>(promise: Promise<T>): CancellablePromise<T> {
  let cancelled = false;

  const wrappedPromise = new Promise<T>((resolve, reject) => {
    promise
      .then(value => {
        if (!cancelled) resolve(value);
      })
      .catch(error => {
        if (!cancelled) reject(error);
      });
  }) as CancellablePromise<T>;

  wrappedPromise.cancel = () => {
    cancelled = true;
  };

  return wrappedPromise;
}
```

---

## Retry Patterns

### Simple Retry

```typescript
async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts: number
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt === maxAttempts) break;
    }
  }

  throw lastError;
}
```

### Exponential Backoff

```typescript
type RetryConfig = {
  maxAttempts: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
  shouldRetry?: (error: Error, attempt: number) => boolean;
};

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  const {
    maxAttempts,
    initialDelayMs,
    maxDelayMs,
    backoffMultiplier,
    shouldRetry = () => true,
  } = config;

  let delay = initialDelayMs;
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxAttempts || !shouldRetry(lastError, attempt)) {
        break;
      }

      // Add jitter to prevent thundering herd
      const jitter = Math.random() * 0.3 * delay;
      await sleep(delay + jitter);

      delay = Math.min(delay * backoffMultiplier, maxDelayMs);
    }
  }

  throw lastError;
}

// Helper
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Usage
const result = await retryWithBackoff(
  () => fetchData(),
  {
    maxAttempts: 5,
    initialDelayMs: 1000,
    maxDelayMs: 30000,
    backoffMultiplier: 2,
    shouldRetry: (error) => error.message.includes('ECONNRESET'),
  }
);
```

---

## Debounce and Throttle

### Debounce

Execute only after a pause in calls:

```typescript
function debounce<T extends (...args: Array<unknown>) => unknown>(
  fn: T,
  delayMs: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delayMs);
  };
}

// Async version that returns a promise
function debounceAsync<T extends (...args: Array<unknown>) => Promise<unknown>>(
  fn: T,
  delayMs: number
): (...args: Parameters<T>) => Promise<Awaited<ReturnType<T>>> {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  let pendingPromise: Promise<Awaited<ReturnType<T>>> | undefined;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);

    pendingPromise = new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await fn(...args);
          resolve(result as Awaited<ReturnType<T>>);
        } catch (error) {
          reject(error);
        }
      }, delayMs);
    });

    return pendingPromise;
  };
}
```

### Throttle

Execute at most once per interval:

```typescript
function throttle<T extends (...args: Array<unknown>) => unknown>(
  fn: T,
  intervalMs: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;

  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= intervalMs) {
      lastCall = now;
      fn(...args);
    }
  };
}
```

---

## Queue Pattern

### Simple Async Queue

```typescript
class AsyncQueue<T> {
  private queue: Array<() => Promise<T>> = [];
  private processing = false;
  private results: Array<T> = [];

  add(task: () => Promise<T>): void {
    this.queue.push(task);
    this.process();
  }

  private async process(): Promise<void> {
    if (this.processing) return;
    this.processing = true;

    while (this.queue.length > 0) {
      const task = this.queue.shift();
      if (task) {
        const result = await task();
        this.results.push(result);
      }
    }

    this.processing = false;
  }

  getResults(): Array<T> {
    return [...this.results];
  }
}
```

---

## Common Anti-Patterns

### Avoid Floating Promises

```typescript
// ❌ Bad: promise not awaited or handled
function saveData(data: Data) {
  db.save(data); // Floating promise!
}

// ✅ Good: await or return the promise
async function saveData(data: Data): Promise<void> {
  await db.save(data);
}

// ✅ Also good: handle with .catch()
function saveDataFireAndForget(data: Data): void {
  db.save(data).catch(error => {
    logger.error('Failed to save data', error);
  });
}
```

### Avoid Async in Constructors

```typescript
// ❌ Bad: can't await constructor
class UserService {
  constructor() {
    this.init(); // Can't await, race condition
  }

  private async init() {
    this.config = await loadConfig();
  }
}

// ✅ Good: factory function
class UserService {
  private constructor(private config: Config) {}

  static async create(): Promise<UserService> {
    const config = await loadConfig();
    return new UserService(config);
  }
}

// Usage
const service = await UserService.create();
```

### Avoid Unnecessary Async

```typescript
// ❌ Bad: async adds overhead for no reason
async function double(n: number): Promise<number> {
  return n * 2;
}

// ✅ Good: only async when needed
function double(n: number): number {
  return n * 2;
}
```

---

*Companion to: error-handling.md, api-patterns.md*
*Last updated: 2025-12-31*
