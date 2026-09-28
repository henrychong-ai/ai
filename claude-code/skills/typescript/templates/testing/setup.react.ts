/**
 * Vitest Setup File - React Template
 *
 * Usage: Copy to tests/setup.ts and reference in vitest.config.ts:
 *   setupFiles: ['./tests/setup.ts']
 *
 * Required dependencies:
 *   pnpm add -D @testing-library/react @testing-library/jest-dom jsdom
 *
 * Features:
 * - React Testing Library matchers
 * - DOM cleanup
 * - Custom React testing utilities
 */
// oxlint-disable-next-line import/no-unassigned-import -- registers the jest-dom matchers
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// ============================================================================
// React Testing Library Setup
// ============================================================================

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// ============================================================================
// Mock Window APIs
// ============================================================================

// Mock matchMedia (for responsive components)
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver / IntersectionObserver.
// Vitest 4: a vi.fn() with an arrow-function implementation is not constructible,
// so components calling `new ResizeObserver()` need a class.
class ResizeObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;

class IntersectionObserverMock {
  readonly root = null;
  readonly rootMargin = "";
  readonly thresholds: ReadonlyArray<number> = [];
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn(() => []);
}
globalThis.IntersectionObserver =
  IntersectionObserverMock as unknown as typeof IntersectionObserver;

// Mock scrollTo
window.scrollTo = vi.fn();

// ============================================================================
// Mock fetch (if not using MSW)
// ============================================================================

// Basic fetch mock - consider using MSW for more realistic mocking
// global.fetch = vi.fn();

// ============================================================================
// Environment Variables
// ============================================================================

// Set test environment variables
process.env["TZ"] = "UTC"; // Vitest already sets NODE_ENV=test

// ============================================================================
// Console Suppression (Optional)
// ============================================================================

// Suppress specific console methods during tests
// Useful for reducing noise from expected errors/warnings
const originalError = console.error;
console.error = (...args: unknown[]) => {
  // Ignore React act() warnings (React 19 dropped the old "Warning: " prefix)
  if (typeof args[0] === "string" && args[0].includes("not wrapped in act(")) {
    return;
  }
  originalError.apply(console, args);
};

// ============================================================================
// Custom Test Utilities
// ============================================================================

/**
 * Wait for next tick (useful for async state updates)
 */
export const nextTick = () => new Promise((resolve) => setTimeout(resolve, 0));

/**
 * Create a mock function that tracks render count
 */
export function createRenderCounter() {
  const counter = { count: 0 };
  const increment = () => {
    counter.count += 1;
    return counter.count;
  };
  return { counter, increment };
}
