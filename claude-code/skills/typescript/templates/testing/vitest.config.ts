/**
 * Vitest Configuration - Base Template (Node.js/Backend)
 *
 * Usage: Copy to project root as vitest.config.ts
 *
 * Features:
 * - TypeScript support with globals
 * - 80% coverage thresholds (enforced)
 * - V8 coverage provider
 * - Path aliases (update to match your tsconfig.json)
 *
 * @see https://vitest.dev/config/
 */
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Enable global test APIs (describe, it, expect)
    globals: true,

    // Environment: 'node' for backend, 'jsdom' for frontend
    environment: 'node',

    // Test file patterns
    include: ['**/*.test.ts', '**/*.spec.ts'],
    exclude: ['**/node_modules/**', '**/dist/**', '**/e2e/**'],

    // Path aliases (must match tsconfig.json)
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/': path.resolve(__dirname, './src/'),
    },

    // Coverage configuration
    coverage: {
      // Use V8 for fast, accurate coverage
      provider: 'v8',

      // Output formats
      reporter: ['text', 'json', 'html', 'lcov'],

      // Files to include in coverage
      include: ['src/**/*.ts'],

      // Files to exclude from coverage
      exclude: [
        'src/**/*.test.ts',
        'src/**/*.spec.ts',
        'src/**/*.d.ts',
        'src/types/**',
        'src/index.ts', // Entry points often just re-export
      ],

      // Coverage thresholds (80% minimum - ENFORCED)
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Reporter configuration
    reporters: ['default'],

    // Pool configuration (threads for speed, forks for isolation)
    pool: 'threads',

    // Timeout for individual tests (ms)
    testTimeout: 10000,

    // Timeout for hooks (beforeAll, afterAll, etc.)
    hookTimeout: 10000,
  },
});
