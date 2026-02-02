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
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

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
Object.defineProperty(window, 'matchMedia', {
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

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

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
process.env.NODE_ENV = 'test';
process.env.TZ = 'UTC';

// ============================================================================
// Console Suppression (Optional)
// ============================================================================

// Suppress specific console methods during tests
// Useful for reducing noise from expected errors/warnings
const originalError = console.error;
console.error = (...args: unknown[]) => {
  // Ignore React act() warnings in tests
  if (
    typeof args[0] === 'string' &&
    args[0].includes('Warning: An update to')
  ) {
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
