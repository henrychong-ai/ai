# AI Testing Protocols

Testing requirements and protocols for AI-driven TypeScript development across agent harnesses.

---

## Core Principle

**Testing is non-negotiable for AI-generated code.**

AI systems can generate syntactically correct code that contains subtle logic errors. Tests serve as:
1. **Executable specifications** - Define expected behavior before/during implementation
2. **Validation gates** - Catch errors before they reach production
3. **Refactoring safety nets** - Enable confident code changes
4. **Documentation** - Tests demonstrate how code should be used

---

## Mandatory Testing Rules

### When Tests Are REQUIRED

| Scenario | Rationale | Test Type |
|----------|-----------|-----------|
| **New function with logic** | Validate AI-generated logic correctness | Unit |
| **Bug fix** | Prove bug exists, then prove fix works | Unit/Integration |
| **API endpoint** | Request/response contract validation | Integration |
| **Data transformation** | Input→Output correctness | Unit |
| **Error handling** | Verify graceful failure paths | Unit |
| **Security-sensitive code** | Prevent vulnerabilities | Unit + Integration |
| **Complex algorithms** | Verify edge cases and correctness | Unit |
| **State management** | Validate state transitions | Unit/Integration |

### When Tests Are OPTIONAL

| Scenario | Rationale |
|----------|-----------|
| Simple getters/setters | No logic to test |
| Configuration constants | Static values |
| Type-only exports (*.d.ts) | No runtime behavior |
| Trivial wrapper functions | One-line pass-through |
| Generated code | Test the generator, not the output |
| Index/barrel files | Just re-exports |

---

## Test-First Development Triggers

Use TDD (write tests BEFORE implementation) when:

1. **User explicitly requests TDD** - Honor the request
2. **Bug fix requests** - Write failing test first, then fix
3. **Complex algorithm implementation** - Define expected behavior first
4. **Security-related code** - Specify security requirements as tests
5. **API contract changes** - Define new contract in tests first
6. **Refactoring existing code** - Ensure tests pass before and after

### Agent TDD Workflow

```
1. User describes feature/fix
2. The agent writes failing test(s) first
3. The agent implements minimum code to pass
4. The agent refactors while keeping tests green
5. The agent runs the full test suite
6. Commit with tests and implementation together
```

---

## Coverage Requirements

### Example thresholds when no repository policy exists

The approved repository policy takes precedence. Choose package and security-file
floors based on risk and source inventory; the following values are illustrative.

| Metric | Example starting floor | Example higher target |
|--------|---------|-------------|
| **Lines** | 80% | 90% |
| **Functions** | 80% | 90% |
| **Branches** | 80% | 85% |
| **Statements** | 80% | 90% |

### Enforcement

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

### Coverage Exceptions

Use sparingly with explicit comments:

```typescript
/* v8 ignore next 3 - Platform-specific code unreachable in tests */
if (process.platform === 'win32') {
  return windowsSpecificPath();
}
```

Valid exception reasons:
- Platform-specific branches
- Error conditions impossible to trigger in tests
- Debug/development-only code
- Third-party integration error paths

---

## Harness Integration

### Task Tracking

When implementing features with tests, use the active harness's task plan or checklist to track:

```
1. [ ] Write unit tests for [feature]
2. [ ] Implement [feature]
3. [ ] Verify tests pass
4. [ ] Check complete-source coverage meets the repository policy
5. [ ] Run full test suite
```

### Test Verification Workflow

After writing code, the agent should:

1. **Run the canonical gate** — inspect the repo scripts and use the CI-equivalent command
2. **Consume fresh coverage** — if that gate already runs tests with coverage, do not repeat an uninstrumented pass
3. **Report results** - Show pass/fail and coverage percentages
4. **Fix failures** - Iterate until tests pass

### Commit Protocol

Tests and implementation should be committed together:

```bash
git add src/feature.ts src/feature.test.ts
git commit -m "feat: add user validation with tests"
```

Never commit:
- Implementation without tests (for mandatory scenarios)
- Failing tests
- Tests that skip/ignore without justification

### Cloudflare Workers Test Isolation (workerd Process Leaks)

When using `@cloudflare/vitest-pool-workers`, each vitest invocation spawns `workerd` child processes. In multi-agent sessions where several agents run tests in parallel, these processes accumulate and are not cleaned up when agents finish, causing memory exhaustion.

**Rule: Agents write tests only, never execute them in parallel.**

In team/multi-agent workflows:
1. Each agent writes and modifies test files but does **not** run `pnpm test` or `vitest`
2. The coordinating agent runs the full test suite once after all agents complete: `pnpm run check`
3. Before heavy test sessions, kill stale processes: `pkill -f workerd 2>/dev/null`

**Single-agent sessions** are unaffected — run tests normally.

---

## Auth failure and browser acceptance

For authentication changes, exercise never-settling upstream calls, cancellation,
and a subsequent request after the failed attempt. Distinguish optional profile
enrichment from mandatory identity/organisation/permission checks: the latter fail
closed. Check that the real browser exits loading with a useful retry/error state.
Mocked JWT success and a green health probe do not establish real-provider login
acceptance; use separately scoped admin, writer, read-only, and restricted personas.

## Test Quality Standards

### Good Tests Are

1. **Independent** - Can run in any order
2. **Deterministic** - Same result every run
3. **Fast** - Unit tests < 100ms each
4. **Focused** - Test one thing per test
5. **Readable** - Clear intent from test name

### Test Naming Convention

```typescript
// Pattern: should [expected behavior] when [condition]
it('should return user when id exists', async () => { ... });
it('should throw NotFoundError when id is invalid', async () => { ... });

// Or: [action] [result]
it('creates user with generated id', async () => { ... });
it('throws on duplicate email', async () => { ... });
```

### Arrange-Act-Assert Pattern

```typescript
it('should apply discount to order', () => {
  // Arrange
  const order = createOrder({ total: 100 });
  const discount = { percent: 20 };

  // Act
  const result = applyDiscount(order, discount);

  // Assert
  expect(result.total).toBe(80);
});
```

---

## Test Types by Layer

### Unit Tests (Many, Fast)

```typescript
// Pure function - easiest to test
describe('formatCurrency', () => {
  it('should format USD correctly', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });
});
```

### Integration Tests (Some, Medium)

```typescript
// API endpoint test
describe('POST /users', () => {
  it('should create user and return 201', async () => {
    const res = await app.request('/users', {
      method: 'POST',
      body: JSON.stringify({ name: 'John', email: 'john@example.com' }),
    });

    expect(res.status).toBe(201);
    expect(await res.json()).toHaveProperty('id');
  });
});
```

### E2E Tests (Few, Slow)

```typescript
// Critical user journey
test('user can complete checkout', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('#email', 'test@example.com');
  await page.click('[data-testid="place-order"]');

  await expect(page.locator('.order-confirmation')).toBeVisible();
});
```

---

## Common Testing Patterns

### Testing Error Paths

```typescript
describe('fetchUser', () => {
  it('should throw NotFoundError for invalid id', async () => {
    await expect(fetchUser('invalid')).rejects.toThrow(NotFoundError);
  });

  it('should throw NetworkError on connection failure', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('ECONNREFUSED'));
    await expect(fetchUser('123')).rejects.toThrow(NetworkError);
  });
});
```

### Testing Async Code

```typescript
describe('async operations', () => {
  it('should resolve with data', async () => {
    const result = await fetchData();
    expect(result.data).toBeDefined();
  });

  it('should handle timeout', async () => {
    vi.useFakeTimers();
    const promise = fetchWithTimeout(5000);
    vi.advanceTimersByTime(5001);
    await expect(promise).rejects.toThrow('Timeout');
    vi.useRealTimers();
  });
});
```

### Testing with Mocks

```typescript
// Mock external dependencies, not internal logic
vi.mock('./email-service', () => ({
  sendEmail: vi.fn().mockResolvedValue({ sent: true }),
}));

describe('notification service', () => {
  it('should send email notification', async () => {
    await notifyUser({ email: 'test@example.com' });
    expect(sendEmail).toHaveBeenCalledWith(
      expect.objectContaining({ to: 'test@example.com' })
    );
  });
});
```

---

## Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```typescript
// Bad - tests HOW, not WHAT
it('should call database.save', () => {
  const spy = vi.spyOn(database, 'save');
  createUser({ name: 'John' });
  expect(spy).toHaveBeenCalled();
});

// Good - tests observable behavior
it('should create user with given name', async () => {
  const user = await createUser({ name: 'John' });
  expect(user.name).toBe('John');
});
```

### ❌ Over-Mocking

```typescript
// Bad - testing mocks, not code
it('should process', async () => {
  mockDb.find.mockResolvedValue(order);
  mockValidator.validate.mockReturnValue(true);
  mockPayment.charge.mockResolvedValue({ success: true });
  mockEmail.send.mockResolvedValue(true);
  // ... 10 more mocks
});

// Good - minimal mocks, test real behavior
it('should process order', async () => {
  // Only mock external services
  mockPaymentGateway.charge.mockResolvedValue({ success: true });
  const result = await processOrder(testOrder);
  expect(result.status).toBe('completed');
});
```

### ❌ Non-Deterministic Tests

```typescript
// Bad - depends on current time
it('should show greeting', () => {
  expect(getGreeting()).toBe('Good morning'); // Fails at night!
});

// Good - control the clock
it('should show morning greeting at 9am', () => {
  vi.setSystemTime(new Date('2025-01-01T09:00:00'));
  expect(getGreeting()).toBe('Good morning');
});
```

---

## CI Integration Checklist

Before merging any PR:

- [ ] All tests pass (`pnpm test:run`)
- [ ] Coverage meets the approved repository policy (use its canonical coverage command)
- [ ] No skipped tests without justification
- [ ] No `console.log` in test files
- [ ] Runtime meets the repository's measured budget; investigate regressions without weakening coverage or assertions

---

*Companion to: vitest-patterns.md, jest-patterns.md, testing-strategies.md*
*Last updated: 2026-01-15*

## Behavioural evidence and review

For a substantial coverage remediation, inventory and review the existing test
files as well as the new ones. A passing suite is execution evidence, not a review.
Record gaps and their resolution in the repository; routine small changes need
only proportionate review of their affected tests.

- Exercise production handlers and permission decisions; mock external service
  boundaries rather than copying the implementation into a test router.
- Assert exact observable results and side effects. A denial should also prove
  that the write did not happen; a cancellation test must actually cancel and
  prove no retry. Avoid accepting multiple status codes merely to make a test pass.
- Keep titles aligned with what assertions prove. Source-text checks can protect
  a static contract but do not prove runtime behaviour.
- For a bug fix, demonstrate the regression against the defective implementation
  when practical, then its closure. Use deterministic clocks, isolated fixtures,
  and restore globals/spies after each test.
- For critical predicates, focused mutation probes should fail assertions when
  the predicate is removed or inverted; compilation failures are not a killed
  behavioural mutation. Do not imply a whole-repository mutation score.
- Self-test fuzz oracles with known leaking and safe samples, including the
  representations they claim to recognise. Document grammar, decoding, fragment,
  and size bounds; seeded success is not universal security proof.

DOM tests establish state and request contracts. Use a real browser for browser
capabilities such as canvas pixel output and important real control interactions;
use actual SDK transport tests for protocol startup/dispatch/shutdown. Controlled
identity fixtures do not prove a live identity-provider login or deployment.
