# Testing Protocols for Version Upgrades

Comprehensive testing requirements for safe version migrations.

## Testing Philosophy

**Principle:** Version upgrades must not change application behavior. Tests prove this.

```
Pre-Upgrade Tests = Post-Upgrade Tests
Same inputs → Same outputs
Same coverage → Same coverage
```

## Testing Phases

### Phase 1: Baseline Establishment

Before any upgrade work:

```bash
# Create test baseline
mkdir -p .upgrade-baseline

# Capture test results
pnpm test 2>&1 | tee .upgrade-baseline/test-results.txt

# Capture coverage
pnpm test -- --coverage 2>&1 | tee .upgrade-baseline/coverage.txt

# Capture build output
pnpm build 2>&1 | tee .upgrade-baseline/build.txt

# Capture type checking
pnpm exec tsc --noEmit 2>&1 | tee .upgrade-baseline/typecheck.txt

# Document versions
node --version > .upgrade-baseline/versions.txt
pnpm --version >> .upgrade-baseline/versions.txt
cat package.json | grep -A5 '"dependencies"' >> .upgrade-baseline/versions.txt
```

### Phase 2: Continuous Validation

After each modification:

```bash
# Quick validation (after each file change)
pnpm exec tsc --noEmit  # Type checking
pnpm test --changed     # Tests for changed files

# Full validation (after each phase)
pnpm test               # All tests
pnpm build              # Full build
```

### Phase 3: Final Verification

Before committing:

```bash
# Complete validation suite
pnpm test -- --coverage
pnpm build
pnpm lint

# Compare to baseline
diff .upgrade-baseline/coverage.txt <(pnpm test -- --coverage 2>&1)
```

## Test Categories

### Category 1: Unit Tests (Required)

**Must pass:** 100%

```bash
pnpm test
```

| Metric | Requirement |
|--------|-------------|
| Pass rate | 100% |
| Coverage | ≥ baseline |
| Duration | ≤ 150% of baseline |

### Category 2: Type Checking (Required)

**Must pass:** No errors

```bash
pnpm exec tsc --noEmit
```

| Metric | Requirement |
|--------|-------------|
| Errors | 0 |
| Warnings | Document any new ones |

### Category 3: Linting (Required)

**Must pass:** No errors

```bash
pnpm lint
```

| Metric | Requirement |
|--------|-------------|
| Errors | 0 |
| New warnings | Explain or fix |

### Category 4: Integration Tests (If Available)

```bash
pnpm test:integration
```

| Metric | Requirement |
|--------|-------------|
| Pass rate | 100% |
| API contracts | Unchanged |

### Category 5: E2E Tests (If Available)

```bash
pnpm test:e2e
```

| Metric | Requirement |
|--------|-------------|
| Critical flows | All pass |
| Visual regression | No changes |

## Coverage Requirements

### Minimum Coverage Standards

| Metric | Minimum | Ideal |
|--------|---------|-------|
| Line coverage | ≥ baseline | ≥ baseline |
| Branch coverage | ≥ baseline | ≥ baseline |
| Function coverage | ≥ baseline | ≥ baseline |

### Coverage Comparison Script

```bash
#!/bin/bash
# compare-coverage.sh

BASELINE=".upgrade-baseline/coverage.txt"
CURRENT=$(pnpm test -- --coverage 2>&1)

echo "Baseline coverage:"
grep -E "All files" "$BASELINE"

echo "Current coverage:"
echo "$CURRENT" | grep -E "All files"

# Extract numbers and compare
# (implementation depends on test runner output format)
```

## Test Failure Protocol

### When Tests Fail

```
1. STOP all upgrade work
2. Identify which test(s) failed
3. Identify most recent change
4. Determine if failure is:
   a) Due to upgrade (expected) → Fix the upgrade code
   b) Due to bug introduced → Revert and investigate
   c) Flaky test → Document and report
5. Never modify test assertions to make them pass
```

### Acceptable Reasons for Test Changes

| Reason | Example | Action |
|--------|---------|--------|
| API signature changed | Method renamed | Update test import |
| Error message changed | New Node.js version | Update assertion |
| Deprecation warning | New warning in output | Filter or acknowledge |

### Unacceptable Reasons

| Reason | Why Bad |
|--------|---------|
| "Test was wrong" | Needs separate investigation |
| "Behavior improved" | Scope creep |
| "Test too strict" | May catch real bugs |

## Performance Testing

### When Required

- Upgrading to new Node.js major version
- Upgrading framework (Next.js, etc.)
- After TypeScript upgrade (compilation time)

### Performance Baseline

```bash
# Create performance baseline
mkdir -p .upgrade-baseline/perf

# Build time
time pnpm build 2>&1 | tee .upgrade-baseline/perf/build-time.txt

# Test time
time pnpm test 2>&1 | tee .upgrade-baseline/perf/test-time.txt

# Startup time (if applicable)
time node dist/index.js --version 2>&1 | tee .upgrade-baseline/perf/startup.txt
```

### Performance Thresholds

| Metric | Acceptable Change |
|--------|-------------------|
| Build time | ≤ 120% of baseline |
| Test time | ≤ 120% of baseline |
| Startup time | ≤ 110% of baseline |
| Memory usage | ≤ 110% of baseline |

## Vitest Configuration

### Recommended Test Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        '**/*.test.ts',
        'vitest.config.ts',
      ],
    },
    reporters: ['verbose'],
    include: ['**/*.test.ts', '**/*.spec.ts'],
    watchExclude: ['node_modules/', 'dist/'],
  },
});
```

### Running Tests

```bash
# All tests with coverage
pnpm vitest run --coverage

# Watch mode (development)
pnpm vitest

# Specific file
pnpm vitest run src/utils.test.ts

# With UI
pnpm vitest --ui
```

## Jest Configuration (Legacy)

If using Jest:

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
  ],
};
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Upgrade Validation

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'

      - run: corepack enable
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec tsc --noEmit
      - run: pnpm lint
      - run: pnpm test -- --coverage
      - run: pnpm build

      - name: Check coverage
        run: |
          # Compare coverage to baseline
          # Fail if coverage decreased
```

## Rollback Testing

### Verification After Rollback

If rollback required:

```bash
# Restore previous state
git checkout main
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Verify functionality
pnpm test
pnpm build

# Confirm baseline state restored
diff .upgrade-baseline/test-results.txt <(pnpm test 2>&1)
```

## Checklist

### Before Upgrade
- [ ] All tests passing
- [ ] Coverage baseline captured
- [ ] Performance baseline captured
- [ ] CI/CD green

### During Upgrade
- [ ] Tests run after each change
- [ ] No test modifications without justification
- [ ] Coverage monitored continuously

### After Upgrade
- [ ] All tests passing
- [ ] Coverage ≥ baseline
- [ ] Performance ≤ 120% baseline
- [ ] CI/CD green
- [ ] No new warnings

---

*Tests are the safety net. Never compromise them.*
