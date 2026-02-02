/**
 * Vitest Workspace Configuration - Monorepo Template
 *
 * Usage: Copy to monorepo root as vitest.workspace.ts
 *
 * Features:
 * - Multi-package test execution
 * - Shared configuration with per-package overrides
 * - Workspace-level coverage reporting
 *
 * @see https://vitest.dev/guide/workspace.html
 */
import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  // Include all packages with vitest.config.ts
  './packages/*/vitest.config.ts',

  // Include all apps with vitest.config.ts
  './apps/*/vitest.config.ts',

  // Or define inline configurations for specific packages
  // {
  //   extends: './vitest.config.ts',
  //   test: {
  //     name: 'core',
  //     root: './packages/core',
  //     environment: 'node',
  //   },
  // },
  // {
  //   extends: './vitest.config.ts',
  //   test: {
  //     name: 'ui',
  //     root: './packages/ui',
  //     environment: 'jsdom',
  //   },
  // },
]);

/**
 * Package-level vitest.config.ts example:
 *
 * // packages/core/vitest.config.ts
 * import { defineProject } from 'vitest/config';
 *
 * export default defineProject({
 *   test: {
 *     name: 'core',
 *     environment: 'node',
 *   },
 * });
 */
