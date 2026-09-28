/**
 * Jest Configuration - Legacy Project Template
 *
 * Usage: Copy to project root as jest.config.ts, with tsconfig.jest.json beside it.
 * tsconfig.jest.json extends the project tsconfig and compiles tests as CommonJS
 * (module Node16 in a package without "type": "module"), which ts-jest needs.
 *
 * For new projects, use Vitest (vitest.config.ts).
 * Use Jest for:
 * - NestJS codebases (the Nest CLI scaffolds Jest)
 * - Existing Jest test suites not yet migrated
 *
 * Required dependencies:
 *   pnpm add -D jest ts-jest @types/jest ts-node typescript@~6.0
 *   (ts-jest requires TypeScript < 7; Jest loads a .ts config through ts-node)
 *
 * @see https://jestjs.io/docs/configuration
 */
import type { Config } from "jest";

const config: Config = {
  // Use ts-jest for TypeScript support
  preset: "ts-jest",

  // Environment: 'node' for backend, 'jsdom' for frontend
  testEnvironment: "node",

  // Root directories for tests
  roots: ["<rootDir>/src"],

  // Test file patterns
  testMatch: ["**/*.test.ts", "**/*.spec.ts"],

  // Files to ignore
  testPathIgnorePatterns: ["/node_modules/", "/dist/", "/e2e/"],

  // Module path aliases (must match tsconfig.json)
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },

  // Setup files to run after Jest is initialized
  setupFilesAfterEnv: ["<rootDir>/tests/setup.ts"],

  // Transform TypeScript files
  transform: {
    "^.+\\.tsx?$": [
      "ts-jest",
      {
        tsconfig: "tsconfig.jest.json", // CommonJS test compile (see header)
      },
    ],
  },

  // Coverage configuration
  collectCoverage: false, // Enable with --coverage flag
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov", "html"],
  collectCoverageFrom: ["src/**/*.ts", "!src/**/*.test.ts", "!src/**/*.spec.ts", "!src/**/*.d.ts"],

  // Example floor: replace with the repository's approved coverage policy
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },

  // Clear mocks between tests
  clearMocks: true,

  // Fail fast on first error (useful in CI)
  // bail: 1,

  // Verbose output
  verbose: true,

  // Timeout for tests (ms)
  testTimeout: 10000,

  // Module file extensions
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
};

export default config;
