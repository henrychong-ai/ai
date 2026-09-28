/**
 * Vitest Configuration - Monorepo Root Template (Vitest 4 `test.projects`)
 *
 * Usage: Copy to the monorepo root as vitest.config.ts.
 * Vitest 4 removed vitest.workspace.ts / defineWorkspace; projects are declared here.
 *
 * - Glob entries pick up each package's own vitest.config.ts (use defineProject there).
 * - Inline entries with `extends: true` inherit the root options below.
 * - Run one project: `vitest --project <name>`.
 *
 * @see https://vitest.dev/guide/projects
 */
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    projects: [
      // Every package with its own vitest.config.ts
      "packages/*",

      // Or inline definitions that inherit the root config:
      // {
      //   extends: true,
      //   test: { name: 'api', root: './packages/api', environment: 'node' },
      // },
      // {
      //   extends: true,
      //   test: { name: 'app', root: './packages/app', environment: 'jsdom' },
      // },
    ],

    // Root-level coverage covers all projects (example floor; the repository's policy wins)
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      include: ["packages/*/src/**/*.{ts,tsx}"],
      exclude: ["**/*.test.{ts,tsx}", "**/*.d.ts"],
    },
  },
});

/**
 * Package-level config example:
 *
 * // packages/api/vitest.config.ts
 * import { defineProject } from 'vitest/config';
 *
 * export default defineProject({
 *   test: {
 *     name: 'api',
 *     environment: 'node',
 *   },
 * });
 */
