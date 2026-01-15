# AI-Assisted Go Testing Protocols

Guidelines for Claude Code when generating and executing Go tests.

---

## Test Generation Principles

### Default Behavior

When generating Go tests:

1. **Always use testify** - Use `assert` and `require` packages
2. **Table-driven by default** - Prefer table-driven tests for multiple cases
3. **Descriptive names** - Use clear, behavior-describing test names
4. **AAA pattern** - Arrange, Act, Assert structure

### Test File Placement

```
// For source file: internal/user/service.go
// Test file goes: internal/user/service_test.go

// Same package for internal access
package user

// Or separate package for black-box testing
package user_test
```

---

## Code Generation Templates

### Unit Test Template

```go
func Test{FunctionName}(t *testing.T) {
    tests := []struct {
        name    string
        // input fields
        want    // expected output type
        wantErr bool
    }{
        {
            name: "description of test case",
            // input values
            want: // expected value
            wantErr: false,
        },
        // more test cases...
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Arrange
            // setup code

            // Act
            got, err := FunctionName(/* args */)

            // Assert
            if tt.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### Service Test Template

```go
func TestUserService_Create(t *testing.T) {
    tests := []struct {
        name      string
        setupMock func(*mocks.UserRepository)
        input     CreateUserInput
        want      *User
        wantErr   error
    }{
        {
            name: "success",
            setupMock: func(m *mocks.UserRepository) {
                m.On("Create", mock.Anything, mock.AnythingOfType("*User")).
                    Return(nil)
            },
            input: CreateUserInput{Name: "Alice", Email: "alice@example.com"},
            want:  &User{Name: "Alice", Email: "alice@example.com"},
        },
        {
            name: "validation error",
            setupMock: func(m *mocks.UserRepository) {
                // No mock setup needed - validation fails first
            },
            input:   CreateUserInput{Name: "", Email: ""},
            wantErr: ErrValidation,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mockRepo := new(mocks.UserRepository)
            tt.setupMock(mockRepo)

            svc := NewUserService(mockRepo)
            got, err := svc.Create(context.Background(), tt.input)

            if tt.wantErr != nil {
                require.ErrorIs(t, err, tt.wantErr)
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tt.want.Name, got.Name)
            mockRepo.AssertExpectations(t)
        })
    }
}
```

### Handler Test Template

```go
func TestHandler_GetUser(t *testing.T) {
    gin.SetMode(gin.TestMode)

    tests := []struct {
        name       string
        userID     string
        setupMock  func(*mocks.UserService)
        wantStatus int
        wantBody   map[string]any
    }{
        {
            name:   "success",
            userID: "123",
            setupMock: func(m *mocks.UserService) {
                m.On("GetByID", mock.Anything, "123").
                    Return(&User{ID: "123", Name: "Alice"}, nil)
            },
            wantStatus: http.StatusOK,
            wantBody:   map[string]any{"id": "123", "name": "Alice"},
        },
        {
            name:   "not found",
            userID: "999",
            setupMock: func(m *mocks.UserService) {
                m.On("GetByID", mock.Anything, "999").
                    Return(nil, ErrNotFound)
            },
            wantStatus: http.StatusNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mockSvc := new(mocks.UserService)
            tt.setupMock(mockSvc)

            h := NewHandler(mockSvc)
            r := gin.New()
            r.GET("/users/:id", h.GetUser)

            req := httptest.NewRequest("GET", "/users/"+tt.userID, nil)
            w := httptest.NewRecorder()
            r.ServeHTTP(w, req)

            assert.Equal(t, tt.wantStatus, w.Code)
            mockSvc.AssertExpectations(t)
        })
    }
}
```

---

## Test Execution Protocol

### Before Running Tests

1. **Check for existing tests** - Read existing test files first
2. **Understand patterns** - Follow existing project conventions
3. **Check dependencies** - Ensure testify is in go.mod

### Running Tests

```bash
# Run all tests
go test ./...

# Run specific package
go test ./internal/user/...

# Run specific test
go test -run TestUserService_Create ./internal/user/...

# With race detector (always use for CI)
go test -race ./...

# With coverage
go test -coverprofile=coverage.out ./...

# Verbose output
go test -v ./...
```

### After Test Failures

1. **Read error output carefully** - Understand what failed
2. **Check test isolation** - Ensure tests don't depend on order
3. **Verify mocks** - Check mock expectations match implementation
4. **Run single test** - Isolate failing test

---

## Coverage Requirements

### Minimum Standards

| Component | Coverage Target |
|-----------|-----------------|
| Overall | 80% |
| Business logic | 90% |
| Handlers | 80% |
| Utilities | 80% |

### Checking Coverage

```bash
# Generate and check coverage
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total
```

---

## Mock Generation

### Using mockery

```bash
# Install mockery
go install github.com/vektra/mockery/v2@latest

# Generate mock for interface
mockery --name=UserRepository --output=mocks --outpkg=mocks

# Generate all mocks (if configured in .mockery.yaml)
mockery
```

### .mockery.yaml Configuration

```yaml
with-expecter: true
packages:
  github.com/username/project/internal/user:
    interfaces:
      UserRepository:
      UserService:
```

---

## Test Data Strategies

### Fixtures

```go
// testutil/fixtures.go
func NewTestUser(opts ...func(*User)) *User {
    u := &User{
        ID:    uuid.New().String(),
        Name:  "Test User",
        Email: "test@example.com",
    }
    for _, opt := range opts {
        opt(u)
    }
    return u
}

func WithName(name string) func(*User) {
    return func(u *User) {
        u.Name = name
    }
}

// Usage
user := NewTestUser(WithName("Alice"))
```

### Test Database

```go
func SetupTestDB(t *testing.T) *sql.DB {
    t.Helper()

    dsn := os.Getenv("TEST_DATABASE_URL")
    if dsn == "" {
        t.Skip("TEST_DATABASE_URL not set")
    }

    db, err := sql.Open("postgres", dsn)
    require.NoError(t, err)

    t.Cleanup(func() {
        db.Close()
    })

    return db
}
```

---

## Integration with /lint

For golangci-lint configuration specific to tests, invoke the **`/lint` skill** which provides:

- Test-specific linter configurations
- Coverage thresholds
- Test file exclusion patterns

Example `.golangci.yml` test configuration:

```yaml
issues:
  exclude-rules:
    # Allow long lines in tests
    - path: _test\.go
      linters:
        - lll

    # Allow unused parameters in test mocks
    - path: _test\.go
      linters:
        - unparam

    # Allow dot imports in tests (for testify)
    - path: _test\.go
      linters:
        - revive
      text: "dot-imports"
```

---

## Common Issues and Solutions

### Issue: Flaky Tests

**Symptoms**: Tests pass/fail inconsistently

**Solutions**:
1. Check for shared state between tests
2. Use `t.Parallel()` carefully
3. Ensure proper test isolation with transactions
4. Use deterministic test data

### Issue: Slow Tests

**Symptoms**: Test suite takes too long

**Solutions**:
1. Use `-short` flag for quick tests
2. Run integration tests separately
3. Parallelize independent tests
4. Mock external dependencies

### Issue: Coverage Gaps

**Symptoms**: Coverage below target

**Solutions**:
1. Add edge case tests
2. Test error paths
3. Use table-driven tests for variations
4. Don't test generated code

---

## Best Practices Summary

| Practice | Implementation |
|----------|----------------|
| Use testify | `assert` for non-fatal, `require` for fatal |
| Table-driven | Default for multiple test cases |
| Mock interfaces | Use mockery for generation |
| Test naming | `Test{Function}_{Scenario}` |
| Coverage | Minimum 80%, target 90% for business logic |
| Isolation | Use `t.Cleanup()` and transactions |
| CI | Always run with `-race` flag |

---

*Companion to: go-test-patterns.md, testify-patterns.md*
*For linting: invoke /lint skill*
*Last updated: 2026-01-15*
