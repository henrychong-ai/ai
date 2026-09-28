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
// Timeout pattern: clear the timer whichever promise settles first
async function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error('Timeout')), timeoutMs);
  });
  try {
    return await Promise.race([promise, timeout]);
  } finally {
    clearTimeout(timeoutId);
  }
}

// Usage (for fetch, prefer AbortSignal.timeout below: it also cancels the request)
const user = await withTimeout(fetchUser(id), 5000);
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
// Results keep the input order; at most `concurrency` mappers run at once.
async function mapWithConcurrency<T, R>(
  items: ReadonlyArray<T>,
  mapper: (item: T, index: number) => Promise<R>,
  concurrency: number
): Promise<Array<R>> {
  if (!Number.isInteger(concurrency) || concurrency < 1) {
    throw new RangeError('concurrency must be a positive integer');
  }
  const results = new Array<R>(items.length);
  let next = 0;

  async function worker(): Promise<void> {
    while (next < items.length) {
      const index = next++;
      results[index] = await mapper(items[index] as T, index);
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, items.length) }, worker);
  await Promise.all(workers);
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

### Timeout with AbortSignal

```typescript
// Cancels the request itself when the timeout fires
function fetchWithTimeout(url: string, timeoutMs: number): Promise<Response> {
  return fetch(url, { signal: AbortSignal.timeout(timeoutMs) });
}

// Combine a caller's signal with a timeout
function fetchWithSignal(url: string, signal: AbortSignal, timeoutMs: number): Promise<Response> {
  return fetch(url, { signal: AbortSignal.any([signal, AbortSignal.timeout(timeoutMs)]) });
}
```

A timeout aborts with a `DOMException` named `TimeoutError`; a manual `abort()` uses `AbortError`.

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
// Generic over the argument tuple: a constraint like `(...args: Array<unknown>) => unknown`
// rejects any function with typed parameters under strictFunctionTypes.
function debounce<TArgs extends Array<unknown>>(
  fn: (...args: TArgs) => unknown,
  delayMs: number
): (...args: TArgs) => void {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;

  return (...args: TArgs) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delayMs);
  };
}

// Async version that returns a promise
// Calls superseded within the window never settle; callers must not await them for cleanup.
function debounceAsync<TArgs extends Array<unknown>, TResult>(
  fn: (...args: TArgs) => Promise<TResult>,
  delayMs: number
): (...args: TArgs) => Promise<TResult> {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  let pendingPromise: Promise<TResult> | undefined;

  return (...args: TArgs) => {
    clearTimeout(timeoutId);

    pendingPromise = new Promise<TResult>((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await fn(...args);
          resolve(result);
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
function throttle<TArgs extends Array<unknown>>(
  fn: (...args: TArgs) => unknown,
  intervalMs: number
): (...args: TArgs) => void {
  let lastCall = 0;

  return (...args: TArgs) => {
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
// Runs tasks one at a time. A failing task is reported and does not stop the queue.
class AsyncQueue<T> {
  private queue: Array<() => Promise<T>> = [];
  private processing = false;
  private results: Array<T> = [];

  constructor(private readonly onError: (error: unknown) => void) {}

  add(task: () => Promise<T>): void {
    this.queue.push(task);
    void this.process(); // process() never rejects: every task error goes to onError
  }

  private async process(): Promise<void> {
    if (this.processing) return;
    this.processing = true;

    try {
      while (this.queue.length > 0) {
        const task = this.queue.shift();
        if (!task) continue;
        try {
          this.results.push(await task());
        } catch (error) {
          this.onError(error);
        }
      }
    } finally {
      this.processing = false;
    }
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
