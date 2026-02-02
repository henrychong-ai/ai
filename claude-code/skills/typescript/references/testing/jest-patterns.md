# Jest Patterns

Testing with Jest for legacy TypeScript projects. Use for existing projects with Jest infrastructure; prefer Vitest for new projects.

---

## When to Use Jest vs Vitest

| Use Jest When | Use Vitest When |
|---------------|-----------------|
| Existing Jest test suite | New projects |
| Create React App (CRA) | Vite-based projects |
| Jest-specific plugins required | Native ESM needed |
| Team familiar with Jest | TypeScript-first priority |
| Migration cost too high | Speed is critical |

### Migration Decision

**Migrate to Vitest if:**
- Starting major refactor anyway
- Jest config is complex and fragile
- ESM compatibility issues
- Test suite is slow

**Stay on Jest if:**
- Large stable test suite (1000+ tests)
- Custom Jest plugins in use
- No significant pain points
- Team bandwidth limited

---

## Configuration

### Basic Setup

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.test.ts', '**/*.spec.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/types/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

export default config;
```

### React/DOM Testing

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss)$': 'identity-obj-proxy',
  },
};

export default config;

// tests/setup.ts
import '@testing-library/jest-dom';
```

### ESM Support

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest/presets/default-esm',
  extensionsToTreatAsEsm: ['.ts', '.tsx'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        useESM: true,
      },
    ],
  },
};

export default config;
```

---

## Test Structure

### Basic Test

```typescript
import { add } from './math';

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

  beforeAll(async () => {
    db = await createTestDatabase();
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.clear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should insert record', async () => {
    await db.insert({ id: '1', name: 'Test' });
    expect(await db.count()).toBe(1);
  });
});
```

---

## Mocking

### Mock Functions

```typescript
describe('notification service', () => {
  it('should call email service', async () => {
    const sendEmail = jest.fn().mockResolvedValue({ sent: true });

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
// Mock entire module
jest.mock('./email-service', () => ({
  sendEmail: jest.fn().mockResolvedValue({ sent: true }),
}));

import { sendEmail } from './email-service';
import { notifyUser } from './notification-service';

describe('notification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should send email notification', async () => {
    await notifyUser({ email: 'test@example.com' });
    expect(sendEmail).toHaveBeenCalled();
  });
});
```

### Partial Mocks

```typescript
// Mock only specific exports
jest.mock('./utils', () => {
  const actual = jest.requireActual('./utils');
  return {
    ...actual,
    fetchData: jest.fn().mockResolvedValue({ data: 'mocked' }),
  };
});
```

### Spy on Methods

```typescript
describe('logger', () => {
  it('should log errors', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

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
const mockFn = jest.fn();

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
expect(value).toBeCloseTo(0.3, 5);

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
describe('scheduled tasks', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should execute after delay', () => {
    const callback = jest.fn();

    setTimeout(callback, 1000);

    expect(callback).not.toHaveBeenCalled();

    jest.advanceTimersByTime(1000);

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should run all pending timers', () => {
    const callback = jest.fn();

    setTimeout(callback, 1000);
    setTimeout(callback, 2000);

    jest.runAllTimers();

    expect(callback).toHaveBeenCalledTimes(2);
  });

  it('should mock Date.now', () => {
    jest.setSystemTime(new Date('2025-01-01'));

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

// Update snapshots: jest --updateSnapshot
```

---

## Coverage

### Configuration

```typescript
// jest.config.ts
const config: Config = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.test.ts',
    '!src/**/*.d.ts',
    '!src/types/**',
    '!src/index.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### Running Coverage

```bash
# Run with coverage
jest --coverage

# Watch mode with coverage
jest --watchAll --coverage
```

### Ignoring Lines

```typescript
/* istanbul ignore next */
if (process.env.NODE_ENV === 'development') {
  console.log('debug');
}

/* istanbul ignore if */
if (someRareCondition) {
  handleRareCase();
}
```

---

## CLI Commands

```bash
# Run all tests
jest

# Run once (CI mode)
jest --ci

# Run specific file
jest src/utils.test.ts

# Run tests matching pattern
jest -t "should create user"

# Watch mode
jest --watch

# Watch all files
jest --watchAll

# Update snapshots
jest --updateSnapshot

# Run with coverage
jest --coverage

# Run in band (no parallelism)
jest --runInBand

# Debug mode
node --inspect-brk node_modules/.bin/jest --runInBand
```

---

## Package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage"
  }
}
```

---

## Jest vs Vitest Syntax Comparison

| Feature | Jest | Vitest |
|---------|------|--------|
| Mock function | `jest.fn()` | `vi.fn()` |
| Mock module | `jest.mock()` | `vi.mock()` |
| Spy | `jest.spyOn()` | `vi.spyOn()` |
| Clear mocks | `jest.clearAllMocks()` | `vi.clearAllMocks()` |
| Fake timers | `jest.useFakeTimers()` | `vi.useFakeTimers()` |
| Advance time | `jest.advanceTimersByTime()` | `vi.advanceTimersByTime()` |
| Set system time | `jest.setSystemTime()` | `vi.setSystemTime()` |
| Restore mocks | `jest.restoreAllMocks()` | `vi.restoreAllMocks()` |
| Require actual | `jest.requireActual()` | `await importOriginal()` |
| Coverage ignore | `/* istanbul ignore */` | `/* v8 ignore */` |

---

## Migration to Vitest

### Step 1: Install Dependencies

```bash
pnpm remove jest ts-jest @types/jest
pnpm add -D vitest @vitest/coverage-v8
```

### Step 2: Convert Config

```typescript
// vitest.config.ts (from jest.config.ts)
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // or 'jsdom'
    include: ['**/*.test.ts', '**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.d.ts'],
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

### Step 3: Update Test Files

```bash
# Search and replace (use IDE or sed)
# jest.fn() → vi.fn()
# jest.mock() → vi.mock()
# jest.spyOn() → vi.spyOn()
# jest.clearAllMocks() → vi.clearAllMocks()
# jest.useFakeTimers() → vi.useFakeTimers()
# jest.useRealTimers() → vi.useRealTimers()
# jest.advanceTimersByTime() → vi.advanceTimersByTime()
# jest.setSystemTime() → vi.setSystemTime()

# Add import if not using globals
import { describe, it, expect, vi } from 'vitest';
```

### Step 4: Update Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

### Step 5: Handle Edge Cases

- `jest.requireActual()` → Use async `importOriginal` in vi.mock
- `jest.doMock()` → Use `vi.doMock()`
- Timer-related issues → Vitest timer API is slightly different
- Snapshot format → May need to update snapshots

---

## Common Issues

### ESM Compatibility

```typescript
// jest.config.ts - for ESM projects
const config: Config = {
  preset: 'ts-jest/presets/default-esm',
  extensionsToTreatAsEsm: ['.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { useESM: true }],
  },
};
```

### Path Aliases Not Resolving

```typescript
// jest.config.ts
const config: Config = {
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
  },
};
```

### Slow Tests

```bash
# Run in parallel (default)
jest

# Run sequentially for debugging
jest --runInBand

# Use --maxWorkers to limit parallelism
jest --maxWorkers=4
```

---

*Companion to: vitest-patterns.md, testing-strategies.md, ai-testing-protocols.md*
*Last updated: 2026-01-15*
