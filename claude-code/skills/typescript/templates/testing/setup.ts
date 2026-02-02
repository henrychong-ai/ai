/**
 * Vitest Global Setup File - Base Template
 *
 * Usage: Copy to tests/setup.ts and reference in vitest.config.ts:
 *   setupFiles: ['./tests/setup.ts']
 *
 * Features:
 * - Custom matchers
 * - Global test utilities
 * - Environment setup
 */
import { expect, vi } from 'vitest';

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

  /**
   * Check if a date is recent (within N seconds of now)
   * @example expect(date).toBeRecentDate(5) // within 5 seconds
   */
  toBeRecentDate(received: Date, withinSeconds = 5) {
    const now = Date.now();
    const diff = Math.abs(now - received.getTime()) / 1000;
    const pass = diff <= withinSeconds;
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received.toISOString()} not to be within ${withinSeconds}s of now`
          : `expected ${received.toISOString()} to be within ${withinSeconds}s of now (diff: ${diff.toFixed(2)}s)`,
    };
  },
});

// ============================================================================
// TypeScript Type Augmentation
// ============================================================================

interface CustomMatchers<R = unknown> {
  toBeWithinRange(floor: number, ceiling: number): R;
  toBeUUID(): R;
  toBeRecentDate(withinSeconds?: number): R;
}

declare module 'vitest' {
  interface Assertion<T = unknown> extends CustomMatchers<T> {}
  interface AsymmetricMatchersContaining extends CustomMatchers {}
}

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

// ============================================================================
// Global Hooks
// ============================================================================

// Clear all mocks after each test
afterEach(() => {
  vi.clearAllMocks();
});

// Reset modules between tests if needed
// afterEach(() => {
//   vi.resetModules();
// });

// ============================================================================
// Environment Setup
// ============================================================================

// Set timezone for consistent date testing
process.env.TZ = 'UTC';

// Suppress console during tests (optional)
// vi.spyOn(console, 'log').mockImplementation(() => {});
// vi.spyOn(console, 'warn').mockImplementation(() => {});
