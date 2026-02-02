# Testing Strategies

High-level testing philosophy and strategies for TypeScript projects.

---

## Testing Pyramid

```
        /\
       /  \       E2E (Few)
      /----\      Critical user journeys
     /      \
    /--------\    Integration (Some)
   /          \   Component + API tests
  /------------\
 /              \ Unit (Many)
/________________\ Pure functions, utilities
```

| Level | Count | Speed | Scope |
|-------|-------|-------|-------|
| **Unit** | Many | Fast (ms) | Single function/module |
| **Integration** | Some | Medium (s) | Multiple modules together |
| **E2E** | Few | Slow (s-min) | Full user flow |

---

## What to Test

### Test Behavior, Not Implementation

```typescript
// ❌ Bad: tests implementation details
it('should call database.save with correct params', () => {
  const spy = vi.spyOn(database, 'save');
  createUser({ name: 'John' });
  expect(spy).toHaveBeenCalledWith({
    name: 'John',
    createdAt: expect.any(Date),
  });
});

// ✅ Good: tests observable behavior
it('should create a user with the given name', async () => {
  const user = await createUser({ name: 'John' });

  expect(user.name).toBe('John');
  expect(user.id).toBeDefined();
  expect(user.createdAt).toBeInstanceOf(Date);
});
```

### Focus on Public APIs

```typescript
// ✅ Test the public interface
describe('OrderCalculator', () => {
  it('should calculate total with tax', () => {
    const calculator = new OrderCalculator();
    const total = calculator.calculateTotal(items, 0.1);
    expect(total).toBe(110);
  });
});

// ❌ Don't test private methods directly
// If you need to test private methods, they might
// belong in a separate, testable module
```

### Test Edge Cases

```typescript
describe('divide', () => {
  it('should divide two numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  // Edge cases
  it('should handle division by zero', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('should handle negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  it('should handle floating point', () => {
    expect(divide(1, 3)).toBeCloseTo(0.333, 2);
  });
});
```

### Test Error Paths

```typescript
describe('fetchUser', () => {
  it('should return user when found', async () => {
    const user = await fetchUser('valid-id');
    expect(user.id).toBe('valid-id');
  });

  it('should throw NotFoundError when user does not exist', async () => {
    await expect(fetchUser('invalid-id')).rejects.toThrow(NotFoundError);
  });

  it('should throw NetworkError on connection failure', async () => {
    mockFetch.mockRejectedValue(new Error('ECONNREFUSED'));
    await expect(fetchUser('any-id')).rejects.toThrow(NetworkError);
  });
});
```

---

## Arrange-Act-Assert (AAA)

```typescript
it('should apply discount to order', () => {
  // Arrange: Set up test data and dependencies
  const order = createOrder({
    items: [
      { name: 'Widget', price: 100 },
      { name: 'Gadget', price: 50 },
    ],
  });
  const discount = createDiscount({ percent: 20 });

  // Act: Execute the behavior being tested
  const result = applyDiscount(order, discount);

  // Assert: Verify the outcome
  expect(result.total).toBe(120); // (100 + 50) * 0.8
  expect(result.discountApplied).toBe(30);
});
```

---

## Test Naming Conventions

### Pattern: `should [expected behavior] when [condition]`

```typescript
describe('UserValidator', () => {
  it('should return valid when email is correct format', () => { ... });
  it('should return invalid when email is missing @ symbol', () => { ... });
  it('should throw when input is null', () => { ... });
});
```

### Pattern: `[action] [result]`

```typescript
describe('createUser', () => {
  it('creates user with generated id', () => { ... });
  it('hashes password before storing', () => { ... });
  it('throws on duplicate email', () => { ... });
});
```

---

## Test Isolation

### Each Test Should Be Independent

```typescript
// ❌ Bad: tests depend on each other
let user: User;

it('should create user', async () => {
  user = await createUser({ name: 'John' });
  expect(user.id).toBeDefined();
});

it('should update user', async () => {
  // Depends on previous test!
  await updateUser(user.id, { name: 'Jane' });
});

// ✅ Good: each test is self-contained
describe('UserService', () => {
  let user: User;

  beforeEach(async () => {
    user = await createUser({ name: 'John' });
  });

  it('should update user name', async () => {
    await updateUser(user.id, { name: 'Jane' });
    const updated = await getUser(user.id);
    expect(updated.name).toBe('Jane');
  });

  it('should delete user', async () => {
    await deleteUser(user.id);
    await expect(getUser(user.id)).rejects.toThrow(NotFoundError);
  });
});
```

### Clean Up After Tests

```typescript
describe('file operations', () => {
  const testDir = '/tmp/test-files';

  beforeEach(async () => {
    await fs.mkdir(testDir, { recursive: true });
  });

  afterEach(async () => {
    await fs.rm(testDir, { recursive: true, force: true });
  });

  it('should write file', async () => {
    await writeFile(path.join(testDir, 'test.txt'), 'content');
    // ...
  });
});
```

---

## Unit Testing Strategies

### Pure Functions

The easiest to test - same input always produces same output.

```typescript
// Function
function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

// Tests
describe('formatCurrency', () => {
  it('should format USD', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });

  it('should format EUR', () => {
    expect(formatCurrency(1234.56, 'EUR')).toBe('€1,234.56');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0, 'USD')).toBe('$0.00');
  });
});
```

### Functions with Dependencies

Use dependency injection for testability.

```typescript
// Function with injected dependencies
type Dependencies = {
  db: Database;
  logger: Logger;
};

function createUserService({ db, logger }: Dependencies) {
  return {
    async createUser(input: CreateUserInput): Promise<User> {
      logger.info('Creating user', { email: input.email });
      const user = await db.users.create(input);
      return user;
    },
  };
}

// Tests
describe('UserService', () => {
  it('should create user', async () => {
    const mockDb = {
      users: {
        create: vi.fn().mockResolvedValue({ id: '1', name: 'John' }),
      },
    };
    const mockLogger = { info: vi.fn() };

    const service = createUserService({
      db: mockDb as unknown as Database,
      logger: mockLogger as unknown as Logger,
    });

    const user = await service.createUser({ name: 'John' });

    expect(user.name).toBe('John');
    expect(mockDb.users.create).toHaveBeenCalled();
    expect(mockLogger.info).toHaveBeenCalled();
  });
});
```

---

## Integration Testing

### Database Integration

```typescript
import { beforeAll, afterAll, describe, it, expect } from 'vitest';

describe('UserRepository', () => {
  let db: Database;
  let repo: UserRepository;

  beforeAll(async () => {
    db = await createTestDatabase();
    repo = new UserRepository(db);
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.exec('DELETE FROM users');
  });

  it('should create and retrieve user', async () => {
    const created = await repo.create({ name: 'John', email: 'john@example.com' });

    const found = await repo.findById(created.id);

    expect(found).toEqual(created);
  });

  it('should update user', async () => {
    const user = await repo.create({ name: 'John', email: 'john@example.com' });

    await repo.update(user.id, { name: 'Jane' });
    const updated = await repo.findById(user.id);

    expect(updated?.name).toBe('Jane');
  });
});
```

### API Integration

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('Users API', () => {
  let app: Hono;

  beforeAll(() => {
    app = createApp();
  });

  it('GET /users/:id returns user', async () => {
    const res = await app.request('/users/123');

    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.id).toBe('123');
  });

  it('POST /users creates user', async () => {
    const res = await app.request('/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'John', email: 'john@example.com' }),
    });

    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body.id).toBeDefined();
  });

  it('POST /users returns 400 for invalid email', async () => {
    const res = await app.request('/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'John', email: 'invalid' }),
    });

    expect(res.status).toBe(400);
  });
});
```

---

## E2E Testing with Playwright

### Setup

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Page Object Pattern

```typescript
// e2e/pages/login-page.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(private page: Page) {
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// e2e/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';

test('successful login', async ({ page }) => {
  const loginPage = new LoginPage(page);

  await loginPage.goto();
  await loginPage.login('test@example.com', 'password');

  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Welcome')).toBeVisible();
});

test('invalid credentials show error', async ({ page }) => {
  const loginPage = new LoginPage(page);

  await loginPage.goto();
  await loginPage.login('wrong@example.com', 'wrong');

  await expect(page.getByText('Invalid credentials')).toBeVisible();
});
```

---

## Testing in CI

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'pnpm'

      - run: pnpm install
      - run: pnpm test:coverage

      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### Test Splitting for Speed

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: pnpm test --shard=${{ matrix.shard }}/4
```

---

## Anti-Patterns to Avoid

### Don't Test Implementation

```typescript
// ❌ Brittle: breaks when implementation changes
it('should use map and filter', () => {
  const spy = vi.spyOn(Array.prototype, 'map');
  processItems(items);
  expect(spy).toHaveBeenCalled();
});

// ✅ Test outcome instead
it('should return processed items', () => {
  const result = processItems(items);
  expect(result).toEqual(expectedOutput);
});
```

### Don't Over-Mock

```typescript
// ❌ Too many mocks = testing mocks, not code
it('should process order', async () => {
  mockDb.find.mockResolvedValue(order);
  mockValidator.validate.mockReturnValue(true);
  mockPayment.charge.mockResolvedValue({ success: true });
  mockEmail.send.mockResolvedValue(true);
  mockLogger.info.mockImplementation(() => {});

  await processOrder(orderId);

  expect(mockPayment.charge).toHaveBeenCalled();
});

// ✅ Test with real implementations where practical
// Only mock external services (HTTP, database, email)
```

### Don't Aim for 100% Coverage

```typescript
// ❌ Testing trivial code for coverage
it('should export constant', () => {
  expect(MAX_RETRIES).toBe(3);
});

// ✅ Focus on critical paths and edge cases
// 80% meaningful coverage > 100% meaningless coverage
```

---

## Testing Checklist

- [ ] Tests are independent (can run in any order)
- [ ] Tests are deterministic (same result every run)
- [ ] Tests are fast (< 100ms for unit tests)
- [ ] Tests have meaningful names
- [ ] Tests follow AAA pattern
- [ ] Tests cover edge cases
- [ ] Tests cover error paths
- [ ] Mocks are minimal
- [ ] No implementation details tested

---

*Companion to: vitest-patterns.md, jest-patterns.md, ai-testing-protocols.md*
*Last updated: 2026-01-15*
