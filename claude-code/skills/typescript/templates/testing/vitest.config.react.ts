/**
 * Vitest Configuration - React/DOM Template
 *
 * Usage: Copy to project root as vitest.config.ts
 *
 * Features:
 * - jsdom environment for DOM testing
 * - React Testing Library integration
 * - 80% coverage thresholds (enforced)
 * - Setup file for custom matchers
 *
 * Required dependencies:
 *   pnpm add -D vitest @vitest/coverage-v8 jsdom
 *   pnpm add -D @testing-library/react @testing-library/jest-dom
 *
 * @see https://vitest.dev/config/
 */
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  test: {
    // Enable global test APIs (describe, it, expect)
    globals: true,

    // jsdom environment for DOM testing
    environment: 'jsdom',

    // Setup file for React Testing Library matchers
    setupFiles: ['./tests/setup.ts'],

    // Test file patterns
    include: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
    exclude: ['**/node_modules/**', '**/dist/**', '**/e2e/**'],

    // Path aliases (must match tsconfig.json)
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/': path.resolve(__dirname, './src/'),
    },

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.ts', 'src/**/*.tsx'],
      exclude: [
        'src/**/*.test.ts',
        'src/**/*.test.tsx',
        'src/**/*.spec.ts',
        'src/**/*.spec.tsx',
        'src/**/*.d.ts',
        'src/types/**',
        'src/index.ts',
        'src/main.tsx', // Entry points
        'src/App.tsx', // Root component (test children instead)
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // CSS handling
    css: {
      modules: {
        classNameStrategy: 'non-scoped',
      },
    },

    // Timeout configuration
    testTimeout: 10000,
    hookTimeout: 10000,
  },
});
