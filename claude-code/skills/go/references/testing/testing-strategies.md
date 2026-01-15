# Go Testing Strategies

Testing pyramid, integration testing, and test organization.

---

## Testing Pyramid

```
        /\
       /  \     E2E Tests (few)
      /----\
     /      \   Integration Tests (some)
    /--------\
   /          \ Unit Tests (many)
  /------------\
```

| Level | Focus | Speed | Coverage Target |
|-------|-------|-------|-----------------|
| Unit | Functions, methods | Fast | 80%+ |
| Integration | Components together | Medium | Key paths |
| E2E | Full system | Slow | Critical flows |

---

## Unit Testing

### Characteristics

- Test single function or method
- No external dependencies (database, network)
- Fast execution (<100ms per test)
- High coverage target (80%+)

### Example

```go
func TestCalculateTotal(t *testing.T) {
    items := []Item{
        {Price: 10.00, Quantity: 2},
        {Price: 5.50, Quantity: 3},
    }

    total := CalculateTotal(items)

    assert.Equal(t, 36.50, total)
}
```

### What to Unit Test

- Pure functions
- Business logic
- Validation rules
- Error handling
- Edge cases

---

## Integration Testing

### Characteristics

- Test multiple components together
- May use real or test databases
- Slower than unit tests
- Focus on component boundaries

### Database Integration Test

```go
func TestUserRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    // Setup test database
    db := setupTestDB(t)
    t.Cleanup(func() { db.Close() })

    repo := NewUserRepository(db)

    // Test create
    user := &User{Name: "Alice", Email: "alice@example.com"}
    err := repo.Create(context.Background(), user)
    require.NoError(t, err)
    assert.NotEmpty(t, user.ID)

    // Test read
    found, err := repo.GetByID(context.Background(), user.ID)
    require.NoError(t, err)
    assert.Equal(t, "Alice", found.Name)
}
```

### API Integration Test

```go
func TestAPIIntegration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    // Setup server with real dependencies
    server := setupTestServer(t)
    t.Cleanup(func() { server.Close() })

    // Test endpoint
    resp, err := http.Get(server.URL + "/api/v1/health")
    require.NoError(t, err)
    defer resp.Body.Close()

    assert.Equal(t, http.StatusOK, resp.StatusCode)
}
```

### Test Database Setup

```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()

    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        t.Skip("TEST_DATABASE_URL not set")
    }

    db, err := sql.Open("postgres", dsn)
    require.NoError(t, err)

    // Run migrations
    err = runMigrations(db)
    require.NoError(t, err)

    // Clean tables
    _, err = db.Exec("TRUNCATE users, orders CASCADE")
    require.NoError(t, err)

    return db
}
```

---

## Test Organization

### Directory Structure

```
project/
├── internal/
│   ├── user/
│   │   ├── user.go
│   │   ├── user_test.go           # Unit tests
│   │   ├── repository.go
│   │   └── repository_test.go
│   └── order/
│       ├── order.go
│       └── order_test.go
├── tests/
│   ├── integration/
│   │   ├── user_test.go           # Integration tests
│   │   └── order_test.go
│   └── e2e/
│       └── api_test.go            # E2E tests
└── testutil/
    ├── fixtures.go                # Test data
    └── helpers.go                 # Shared utilities
```

### Test Fixtures

```go
// testutil/fixtures.go
package testutil

func NewTestUser() *User {
    return &User{
        ID:    uuid.New().String(),
        Name:  "Test User",
        Email: "test@example.com",
    }
}

func NewTestOrder(userID string) *Order {
    return &Order{
        ID:     uuid.New().String(),
        UserID: userID,
        Total:  99.99,
        Status: "pending",
    }
}
```

### Test Helpers

```go
// testutil/helpers.go
package testutil

func SetupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    // ...
}

func CleanTables(t *testing.T, db *sql.DB, tables ...string) {
    t.Helper()
    for _, table := range tables {
        _, err := db.Exec("TRUNCATE " + table + " CASCADE")
        require.NoError(t, err)
    }
}
```

---

## Test Isolation

### Database Isolation

```go
func TestWithTransaction(t *testing.T) {
    db := setupTestDB(t)

    // Start transaction
    tx, err := db.Begin()
    require.NoError(t, err)

    // Rollback after test (isolation)
    t.Cleanup(func() { tx.Rollback() })

    // Run test with transaction
    repo := NewUserRepository(tx)
    // ...
}
```

### Parallel Test Safety

```go
func TestParallel(t *testing.T) {
    tests := []struct {
        name   string
        userID string
    }{
        {"user1", "id1"},
        {"user2", "id2"},
    }

    for _, tt := range tests {
        tt := tt // Capture
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            // Each test gets isolated data
            user := createTestUser(t, tt.userID)
            // ...
        })
    }
}
```

---

## Test Modes

### Short Mode

```go
func TestLongRunning(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping in short mode")
    }

    // Long running test...
}
```

```bash
# Run quick tests only
go test -short ./...

# Run all tests including long ones
go test ./...
```

### Build Tags

```go
//go:build integration

package tests

func TestIntegration(t *testing.T) {
    // Only runs with: go test -tags integration
}
```

```bash
# Run integration tests
go test -tags integration ./...
```

---

## Testing Patterns

### Arrange-Act-Assert (AAA)

```go
func TestUserService_Create(t *testing.T) {
    // Arrange
    repo := new(mocks.UserRepository)
    repo.On("Create", mock.Anything, mock.Anything).Return(nil)
    svc := NewUserService(repo)

    // Act
    user, err := svc.Create(context.Background(), "Alice", "alice@example.com")

    // Assert
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    repo.AssertExpectations(t)
}
```

### Given-When-Then

```go
func TestOrder_CanBeCancelled(t *testing.T) {
    // Given an order in pending status
    order := &Order{Status: "pending"}

    // When we attempt to cancel
    err := order.Cancel()

    // Then it should succeed
    require.NoError(t, err)
    assert.Equal(t, "cancelled", order.Status)
}
```

### Test Doubles

| Type | Purpose | Example |
|------|---------|---------|
| Stub | Return canned answers | `mockRepo.On("Get").Return(user, nil)` |
| Mock | Verify interactions | `mockRepo.AssertCalled(t, "Create")` |
| Fake | Working implementation | In-memory database |
| Spy | Record calls | Log all method calls |

---

## Coverage Strategies

### Coverage Goals

| Component | Target | Rationale |
|-----------|--------|-----------|
| Business logic | 90%+ | Critical code |
| Handlers | 80%+ | Entry points |
| Utilities | 80%+ | Reused code |
| Generated code | 0% | Don't test generated |

### Measuring Coverage

```bash
# Generate coverage profile
go test -coverprofile=coverage.out ./...

# View by function
go tool cover -func=coverage.out

# View in browser
go tool cover -html=coverage.out -o coverage.html

# Coverage summary
go test -cover ./...
```

### CI Coverage Check

```yaml
# In CI pipeline
- name: Test with coverage
  run: |
    go test -coverprofile=coverage.out ./...
    COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "Coverage $COVERAGE% is below 80%"
      exit 1
    fi
```

---

## Testing Anti-Patterns

### What NOT to Do

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Testing implementation | Brittle tests | Test behavior |
| No test isolation | Flaky tests | Use transactions/cleanup |
| Testing private methods | Over-specification | Test public API |
| Ignoring errors in tests | Hidden failures | Use require/assert |
| Magic numbers | Unclear intent | Use named constants |
| Too many mocks | Complex setup | Simplify or use fakes |

### Example: Testing Behavior, Not Implementation

```go
// ❌ Bad: testing implementation
func TestUserService_UsesCache(t *testing.T) {
    mockCache.AssertCalled(t, "Get", "user:123")
}

// ✅ Good: testing behavior
func TestUserService_ReturnsUser(t *testing.T) {
    user, err := svc.GetByID(ctx, "123")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.25'

      - name: Unit tests
        run: go test -short -race -cover ./...

      - name: Integration tests
        run: go test -race ./tests/integration/...
        env:
          TEST_DATABASE_URL: postgres://test:test@localhost:5432/test?sslmode=disable
```

---

## Summary

| Strategy | When to Use |
|----------|-------------|
| Unit tests | Business logic, pure functions |
| Integration tests | Database, external services |
| E2E tests | Critical user flows |
| Table-driven | Multiple input/output combinations |
| Test suites | Shared setup/teardown |
| Mocks | Isolate dependencies |
| Fakes | Simpler than mocks for complex deps |

---

*Companion to: go-test-patterns.md, testify-patterns.md*
*Last updated: 2026-01-15*
