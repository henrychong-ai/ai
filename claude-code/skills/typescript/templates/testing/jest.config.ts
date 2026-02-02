/**
 * Jest Configuration - Legacy Project Template
 *
 * Usage: Copy to project root as jest.config.ts
 *
 * For new projects, prefer Vitest (vitest.config.ts).
 * Use Jest for:
 * - Existing Jest test suites
 * - Create React App (CRA) projects
 * - Projects with Jest-specific plugins
 *
 * Required dependencies:
 *   pnpm add -D jest ts-jest @types/jest
 *
 * @see https://jestjs.io/docs/configuration
 */
import type { Config } from 'jest';

const config: Config = {
  // Use ts-jest for TypeScript support
  preset: 'ts-jest',

  // Environment: 'node' for backend, 'jsdom' for frontend
  testEnvironment: 'node',

  // Root directories for tests
  roots: ['<rootDir>/src'],

  // Test file patterns
  testMatch: ['**/*.test.ts', '**/*.spec.ts'],

  // Files to ignore
  testPathIgnorePatterns: ['/node_modules/', '/dist/', '/e2e/'],

  // Module path aliases (must match tsconfig.json)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },

  // Setup files to run after Jest is initialized
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],

  // Transform TypeScript files
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.json',
      },
    ],
  },

  // Coverage configuration
  collectCoverage: false, // Enable with --coverage flag
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts',
    '!src/**/*.d.ts',
    '!src/types/**',
    '!src/index.ts',
  ],

  // Coverage thresholds (80% minimum - ENFORCED)
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
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
};

export default config;
