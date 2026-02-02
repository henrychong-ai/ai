/**
 * Jest Global Setup File - Legacy Project Template
 *
 * Usage: Copy to tests/setup.ts and reference in jest.config.ts:
 *   setupFilesAfterEnv: ['<rootDir>/tests/setup.ts']
 *
 * For React projects, add:
 *   import '@testing-library/jest-dom';
 */

// ============================================================================
// Custom Matchers
// ============================================================================

expect.extend({
  /**
   * Check if a number is within a range
   * @example expect(value).toBeWithinRange(1, 10)
   */
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

  /**
   * Check if a value is a valid UUID
   * @example expect(id).toBeUUID()
   */
  toBeUUID(received: string) {
    const uuidRegex =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    const pass = uuidRegex.test(received);
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid UUID`
          : `expected ${received} to be a valid UUID`,
    };
  },
});

// ============================================================================
// TypeScript Type Augmentation
// ============================================================================

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
      toBeUUID(): R;
    }
  }
}

// ============================================================================
// Global Hooks
// ============================================================================

// Clear all mocks after each test
afterEach(() => {
  jest.clearAllMocks();
});

// ============================================================================
// Environment Setup
// ============================================================================

// Set timezone for consistent date testing
process.env.TZ = 'UTC';

// ============================================================================
// Global Utilities
// ============================================================================

/**
 * Wait for a condition to be true
 */
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout = 5000,
  interval = 100
): Promise<void> {
  const start = Date.now();
  while (!(await condition())) {
    if (Date.now() - start > timeout) {
      throw new Error(`waitFor timeout after ${timeout}ms`);
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }
}

/**
 * Create a deferred promise for testing async flows
 */
export function createDeferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (reason?: unknown) => void;
} {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

// Export for TypeScript module augmentation
export {};
