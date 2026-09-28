/**
 * Vitest Configuration - React/DOM Template
 *
 * Usage: Copy to project root as vitest.config.ts
 *
 * Features:
 * - jsdom environment for DOM testing
 * - React Testing Library integration
 * - Example 80% coverage floor (the repository's approved policy wins)
 * - Setup file for custom matchers
 *
 * Required dependencies (Vitest major pinned per version-policy.md):
 *   pnpm add -D vitest@^4.1 @vitest/coverage-v8@^4.1 @vitejs/plugin-react jsdom
 *   pnpm add -D @testing-library/react @testing-library/jest-dom
 *
 * @see https://vitest.dev/config/
 */

import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],

  test: {
    // Enable global test APIs (describe, it, expect)
    globals: true,

    // jsdom environment for DOM testing
    environment: "jsdom",

    // Setup file for React Testing Library matchers
    setupFiles: ["./tests/setup.ts"],

    // Test file patterns
    include: ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"],
    exclude: ["**/node_modules/**", "**/dist/**", "**/e2e/**"],

    // Path aliases (must match tsconfig.json)
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },

    // Coverage configuration
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      include: ["src/**/*.ts", "src/**/*.tsx"],
      // Exclude a file only after checking it has no runtime code worth testing
      exclude: ["src/**/*.{test,spec}.{ts,tsx}", "src/**/*.d.ts", "src/main.tsx"],
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
        classNameStrategy: "non-scoped",
      },
    },

    // Timeout configuration
    testTimeout: 10000,
    hookTimeout: 10000,
  },
});
