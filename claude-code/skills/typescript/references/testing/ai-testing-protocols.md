# AI Testing Protocols

Testing requirements and protocols for AI-driven TypeScript development with Claude Code.

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

### TDD Workflow for Claude Code

```
1. User describes feature/fix
2. Claude writes failing test(s) first
3. Claude implements minimum code to pass
4. Claude refactors while keeping tests green
5. Claude runs full test suite
6. Commit with tests and implementation together
```

---

## Coverage Requirements

### Minimum Thresholds

| Metric | Minimum | Recommended |
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

## Claude Code Integration

### TodoWrite for Test Tracking

When implementing features with tests, use TodoWrite to track:

```
1. [ ] Write unit tests for [feature]
2. [ ] Implement [feature]
3. [ ] Verify tests pass
4. [ ] Check coverage meets 80%
5. [ ] Run full test suite
```

### Test Verification Workflow

After writing code, Claude Code should:

1. **Run tests** - `pnpm test:run`
2. **Check coverage** - `pnpm test:coverage`
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

---

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
- [ ] Coverage meets 80% threshold (`pnpm test:coverage`)
- [ ] No skipped tests without justification
- [ ] No `console.log` in test files
- [ ] Tests run in < 2 minutes total

---

*Companion to: vitest-patterns.md, jest-patterns.md, testing-strategies.md*
*Last updated: 2026-01-15*
