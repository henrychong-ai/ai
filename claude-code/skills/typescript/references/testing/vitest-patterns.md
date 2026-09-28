# Vitest Patterns

Testing with Vitest, the default test runner for this stack. Target version and the Workers constraint: `../tech-stack/version-policy.md` (Vitest `^4.1`). Workers-specific setup (`cloudflareTest()`): `../tech-stack/cloudflare.md`.

---

## Configuration

### Basic Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,           // describe, it, expect globally
    environment: 'node',     // or 'jsdom' for browser
    include: ['**/*.test.ts', '**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.{test,spec}.{ts,tsx}', 'src/**/*.d.ts'],
    },
  },
});
```

### Coverage measurement checks

Choose a provider supported by the actual test runtime. A Workers isolate does
not supply Node inspector coverage; validate transform-based instrumentation in
that runtime. When includes omit a hosted entrypoint or package, inspect resolved
paths and the complete source inventory before adding tests or changing floors.
Use absolute include paths if required by the installed pool integration; verify
the report contains every owned executable file, including files never imported.

Keep per-package reports separate. Merge only compatible provider mappings for
the same source/build, without counting both source and compiled output. Report
raw covered/total counters and explain denominator changes; rounded percentages
alone cannot establish non-regression. Test coverage-checker exemptions with
negative cases: an enclosing declaration hit must not cover an unexecuted
operation, and partially mapped executable changes must not silently pass.

### With Path Aliases

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### React/DOM Testing

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});

// tests/setup.ts
import '@testing-library/jest-dom/vitest';
```

### Projects (Monorepo)

Vitest 4 removed `vitest.workspace.ts` and `defineWorkspace`. Declare projects in the root `vitest.config.ts` with `test.projects`:

```typescript
// vitest.config.ts (repository root)
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    projects: [
      'packages/*',                       // each package's own vitest.config.ts
      {
        extends: true,                    // inherit root options
        test: { name: 'ui', root: './packages/ui', environment: 'jsdom' },
      },
    ],
  },
});
```

Run one project with `vitest --project ui`. Template: `templates/testing/vitest.config.projects.ts`.

---

## Test Structure

### Basic Test

```typescript
import { describe, it, expect } from 'vitest';

describe('add', () => {
  it('should add two numbers', () => {
    expect(add(1, 2)).toBe(3);
  });

  it('should handle negative numbers', () => {
    expect(add(-1, 1)).toBe(0);
  });
});
```

### Async Tests

```typescript
describe('fetchUser', () => {
  it('should fetch user by id', async () => {
    const user = await fetchUser('123');
    expect(user.id).toBe('123');
  });

  it('should throw for invalid id', async () => {
    await expect(fetchUser('invalid')).rejects.toThrow('Not found');
  });
});
```

### Setup and Teardown

```typescript
describe('database operations', () => {
  let db: Database;

  // Run once before all tests in this describe
  beforeAll(async () => {
    db = await createTestDatabase();
  });

  // Run once after all tests
  afterAll(async () => {
    await db.close();
  });

  // Run before each test
  beforeEach(async () => {
    await db.clear();
  });

  // Run after each test
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should insert record', async () => {
    await db.insert({ id: '1', name: 'Test' });
    expect(await db.count()).toBe(1);
  });
});
```

### Grouping with describe

```typescript
describe('UserService', () => {
  describe('create', () => {
    it('should create user with valid input', () => { ... });
    it('should throw on invalid email', () => { ... });
  });

  describe('update', () => {
    it('should update existing user', () => { ... });
    it('should throw on non-existent user', () => { ... });
  });

  describe('delete', () => {
    it('should delete user', () => { ... });
  });
});
```

---

## Mocking

### Mock Functions

```typescript
import { vi, describe, it, expect } from 'vitest';

describe('notification service', () => {
  it('should call email service', async () => {
    const sendEmail = vi.fn().mockResolvedValue({ sent: true });

    await notifyUser({ email: 'test@example.com' }, sendEmail);

    expect(sendEmail).toHaveBeenCalledTimes(1);
    expect(sendEmail).toHaveBeenCalledWith(
      expect.objectContaining({ to: 'test@example.com' })
    );
  });
});
```

### Mock Modules

```typescript
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock entire module
vi.mock('./email-service', () => ({
  sendEmail: vi.fn().mockResolvedValue({ sent: true }),
}));

import { sendEmail } from './email-service';
import { notifyUser } from './notification-service';

describe('notification', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should send email notification', async () => {
    await notifyUser({ email: 'test@example.com' });
    expect(sendEmail).toHaveBeenCalled();
  });
});
```

### Partial Mocks

```typescript
import { vi } from 'vitest';

// Mock only specific exports
vi.mock('./utils', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./utils')>();
  return {
    ...actual,
    fetchData: vi.fn().mockResolvedValue({ data: 'mocked' }),
  };
});
```

### Spy on Methods

```typescript
import { vi, describe, it, expect } from 'vitest';

describe('logger', () => {
  it('should log errors', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    logError(new Error('Test error'));

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Test error')
    );

    consoleSpy.mockRestore();
  });
});
```

### Mock Return Values

```typescript
const mockFn = vi.fn();

// Return value
mockFn.mockReturnValue(42);

// Return value once
mockFn.mockReturnValueOnce(1).mockReturnValueOnce(2).mockReturnValue(3);

// Async return value
mockFn.mockResolvedValue({ data: 'async' });
mockFn.mockResolvedValueOnce({ data: 'first' });

// Rejection
mockFn.mockRejectedValue(new Error('Failed'));

// Implementation
mockFn.mockImplementation((x: number) => x * 2);
```

---

## Assertions

### Basic Assertions

```typescript
// Equality
expect(value).toBe(expected);           // === strict equality
expect(value).toEqual(expected);        // Deep equality
expect(value).toStrictEqual(expected);  // Deep + type equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeLessThanOrEqual(10);
expect(value).toBeCloseTo(0.3, 5); // Floating point

// Strings
expect(value).toMatch(/pattern/);
expect(value).toContain('substring');

// Arrays
expect(array).toContain(item);
expect(array).toHaveLength(3);
expect(array).toEqual(expect.arrayContaining([1, 2]));

// Objects
expect(object).toHaveProperty('key');
expect(object).toHaveProperty('nested.key', 'value');
expect(object).toMatchObject({ key: 'value' });
expect(object).toEqual(expect.objectContaining({ key: 'value' }));
```

### Error Assertions

```typescript
// Sync errors
expect(() => throwingFn()).toThrow();
expect(() => throwingFn()).toThrow('message');
expect(() => throwingFn()).toThrow(CustomError);
expect(() => throwingFn()).toThrowError(/pattern/);

// Async errors
await expect(asyncFn()).rejects.toThrow();
await expect(asyncFn()).rejects.toThrow(NotFoundError);
```

### Mock Assertions

```typescript
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenLastCalledWith('last arg');
expect(mockFn).toHaveBeenNthCalledWith(1, 'first call arg');
expect(mockFn).toHaveReturnedWith('value');
```

---

## Fake Timers

```typescript
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('scheduled tasks', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should execute after delay', () => {
    const callback = vi.fn();

    setTimeout(callback, 1000);

    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1000);

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should run all pending timers', () => {
    const callback = vi.fn();

    setTimeout(callback, 1000);
    setTimeout(callback, 2000);

    vi.runAllTimers();

    expect(callback).toHaveBeenCalledTimes(2);
  });

  it('should mock Date.now', () => {
    vi.setSystemTime(new Date('2025-01-01'));

    expect(new Date().getFullYear()).toBe(2025);
  });
});
```

---

## Snapshot Testing

```typescript
describe('component rendering', () => {
  it('should match snapshot', () => {
    const result = renderComponent({ name: 'Test' });
    expect(result).toMatchSnapshot();
  });

  it('should match inline snapshot', () => {
    const result = formatUser({ name: 'John', age: 30 });
    expect(result).toMatchInlineSnapshot(`"John (30)"`);
  });
});

// Update snapshots: vitest --update
```

**Use sparingly** - snapshots are best for:
- Serializable output (JSON, HTML, formatted strings)
- Detecting unintended changes
- NOT for testing logic

---

## Test Utilities

### Custom Matchers

```typescript
// tests/setup.ts
import { expect } from 'vitest';

expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be within range ${floor} - ${ceiling}`
          : `expected ${received} to be within range ${floor} - ${ceiling}`,
    };
  },
});

// Augment types
interface CustomMatchers<R = unknown> {
  toBeWithinRange(floor: number, ceiling: number): R;
}

// One `Matchers` augmentation types expect(x).*, expect.* and expect.extend (Vitest 3.2+).
// The `any` default must match Vitest's own declaration for the interfaces to merge.
declare module 'vitest' {
  // oxlint-disable-next-line typescript/no-explicit-any
  interface Matchers<T = any> extends CustomMatchers<T> {}
}

// Usage
expect(100).toBeWithinRange(90, 110);
```

### Test Fixtures

```typescript
// tests/fixtures/users.ts
export const testUsers = {
  admin: {
    id: 'admin-1',
    name: 'Admin User',
    role: 'admin' as const,
  },
  regularUser: {
    id: 'user-1',
    name: 'Regular User',
    role: 'user' as const,
  },
} as const;

// Usage in tests
import { testUsers } from './fixtures/users';

describe('permissions', () => {
  it('should allow admin access', () => {
    expect(canAccessAdmin(testUsers.admin)).toBe(true);
  });
});
```

### Factory Functions

```typescript
// tests/factories/user.ts
import { faker } from '@faker-js/faker';

type UserOverrides = Partial<User>;

export function createTestUser(overrides: UserOverrides = {}): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    createdAt: faker.date.past(),
    ...overrides,
  };
}

// Usage
const user = createTestUser({ name: 'Specific Name' });
```

---

## Coverage

### Configuration

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.d.ts'],
      // Example floor only: the repository's approved coverage policy wins.
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

Exclude a file only after reading it: a name such as `types.ts` or `index.ts` does not prove the file has no runtime code. Vitest 4 reports only files matched by `coverage.include` (the old `coverage.all` option is gone), so keep `include` covering all owned source.

### Running Coverage

```bash
# Run with coverage
vitest run --coverage

# Watch mode with coverage
vitest --coverage
```

### Ignoring Lines

```typescript
/* v8 ignore next */
if (process.env.NODE_ENV === 'development') {
  console.log('debug');
}

/* v8 ignore start */
function debugOnly() {
  // This function is not covered
}
/* v8 ignore stop */
```

---

## CLI Commands

```bash
# Run all tests
vitest

# Run once (CI mode)
vitest run

# Run specific file
vitest src/utils.test.ts

# Run tests matching pattern
vitest -t "should create user"

# Watch mode (default)
vitest --watch

# Run with UI
vitest --ui

# Update snapshots
vitest --update

# Run with coverage
vitest --coverage

# Run in specific environment
vitest --environment jsdom

# Pool (forks is the default; threads is faster where native modules allow)
vitest --pool threads
vitest --pool forks

# One project in a monorepo
vitest --project ui

# Debug mode
vitest --inspect-brk
```

---

## Package.json Scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

---

## Quick Scaffolding for New Projects

### Minimal Setup (Ironclad Stack)

```bash
# Install dependencies (pinned major: see version-policy.md)
pnpm add -D vitest@^4.1 @vitest/coverage-v8@^4.1

# Create config
cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['**/*.test.ts', '**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.d.ts'],
      // Example floor only: the repository's approved coverage policy wins.
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
EOF

# Add scripts to package.json
npm pkg set scripts.test="vitest run"
npm pkg set scripts.test:watch="vitest"
npm pkg set scripts.test:coverage="vitest run --coverage"
```

### React/DOM Setup

```bash
# Additional dependencies
pnpm add -D @testing-library/react @testing-library/jest-dom jsdom

# Create setup file
mkdir -p tests
cat > tests/setup.ts << 'EOF'
import '@testing-library/jest-dom/vitest';
EOF

# Update vitest.config.ts
# - Change environment: 'node' to environment: 'jsdom'
# - Add setupFiles: ['./tests/setup.ts']
```

### Project Structure

```
project/
├── src/
│   ├── utils.ts
│   ├── utils.test.ts        # Co-located tests
│   └── services/
│       ├── user.ts
│       └── user.test.ts
├── tests/
│   ├── setup.ts             # Global setup
│   ├── fixtures/            # Test data
│   │   └── users.ts
│   └── e2e/                 # E2E tests (Playwright)
├── vitest.config.ts
└── package.json
```

### Templates Available

Pre-configured templates in `templates/testing/`:
- `vitest.config.ts` - Node/backend base config (example 80% floor)
- `vitest.config.react.ts` - React/jsdom variant
- `vitest.config.projects.ts` - Monorepo root config with `test.projects`
- `setup.ts` - Global test setup
- `setup.react.ts` - React Testing Library setup
- Workers: use the `cloudflareTest()` config in `../tech-stack/cloudflare.md`

---

*Companion to: testing-strategies.md, jest-patterns.md, ai-testing-protocols.md*
