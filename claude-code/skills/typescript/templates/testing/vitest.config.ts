/**
 * Vitest Configuration - Base Template (Node.js/Backend)
 *
 * Usage: Copy to project root as vitest.config.ts
 *
 * Features:
 * - TypeScript support with globals
 * - Example 80% coverage floor (the repository's approved policy wins)
 * - V8 coverage provider
 * - Path aliases (update to match your tsconfig.json)
 *
 * @see https://vitest.dev/config/
 */

import path from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // Enable global test APIs (describe, it, expect)
    globals: true,

    // Environment: 'node' for backend, 'jsdom' for frontend
    environment: "node",

    // Test file patterns
    include: ["**/*.test.ts", "**/*.spec.ts"],
    exclude: ["**/node_modules/**", "**/dist/**", "**/e2e/**"],

    // Path aliases (must match tsconfig.json)
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },

    // Coverage configuration
    coverage: {
      // Use V8 for fast, accurate coverage
      provider: "v8",

      // Output formats
      reporter: ["text", "json", "html", "lcov"],

      // Files to include in coverage
      include: ["src/**/*.ts"],

      // Files to exclude from coverage
      // Exclude a file only after checking it has no runtime code
      exclude: ["src/**/*.test.ts", "src/**/*.spec.ts", "src/**/*.d.ts"],

      // Example floor: replace with the repository's approved coverage policy
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Reporter configuration
    reporters: ["default"],

    // Timeout for individual tests (ms)
    testTimeout: 10000,

    // Timeout for hooks (beforeAll, afterAll, etc.)
    hookTimeout: 10000,
  },
});
