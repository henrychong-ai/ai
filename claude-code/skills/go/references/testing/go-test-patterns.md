# Go Test Patterns

Standard library testing patterns, table-driven tests, benchmarks, and coverage.

---

## Test File Organization

### Naming Conventions

| File | Purpose |
|------|---------|
| `user_test.go` | Tests for `user.go` |
| `user_internal_test.go` | Internal tests (same package) |
| `export_test.go` | Export internal symbols for testing |

### Package Naming

```go
// Same package (internal tests) - access unexported
package user

// Separate package (black-box tests) - test public API
package user_test
```

---

## Basic Test Structure

### Simple Test

```go
func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}
```

### Test with Subtests

```go
func TestMath(t *testing.T) {
    t.Run("Add", func(t *testing.T) {
        if Add(2, 3) != 5 {
            t.Error("Add failed")
        }
    })

    t.Run("Subtract", func(t *testing.T) {
        if Subtract(5, 3) != 2 {
            t.Error("Subtract failed")
        }
    })
}
```

---

## Table-Driven Tests

### Standard Pattern

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {
            name:    "valid email",
            email:   "user@example.com",
            wantErr: false,
        },
        {
            name:    "empty email",
            email:   "",
            wantErr: true,
        },
        {
            name:    "no at symbol",
            email:   "userexample.com",
            wantErr: true,
        },
        {
            name:    "no domain",
            email:   "user@",
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidateEmail(%q) error = %v, wantErr %v", tt.email, err, tt.wantErr)
            }
        })
    }
}
```

### With Expected Output

```go
func TestCalculate(t *testing.T) {
    tests := []struct {
        name     string
        input    int
        expected int
    }{
        {"zero", 0, 0},
        {"positive", 5, 25},
        {"negative", -3, 9},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Calculate(tt.input)
            if result != tt.expected {
                t.Errorf("Calculate(%d) = %d; want %d", tt.input, result, tt.expected)
            }
        })
    }
}
```

### With Setup Function

```go
func TestUserService(t *testing.T) {
    tests := []struct {
        name      string
        setupMock func(*mockDB)
        userID    string
        wantUser  *User
        wantErr   error
    }{
        {
            name: "user found",
            setupMock: func(m *mockDB) {
                m.users["123"] = &User{ID: "123", Name: "Alice"}
            },
            userID:   "123",
            wantUser: &User{ID: "123", Name: "Alice"},
            wantErr:  nil,
        },
        {
            name: "user not found",
            setupMock: func(m *mockDB) {
                // Empty
            },
            userID:   "999",
            wantUser: nil,
            wantErr:  ErrNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mock := newMockDB()
            tt.setupMock(mock)

            svc := NewUserService(mock)
            user, err := svc.GetByID(context.Background(), tt.userID)

            if !errors.Is(err, tt.wantErr) {
                t.Errorf("error = %v, want %v", err, tt.wantErr)
            }
            if !reflect.DeepEqual(user, tt.wantUser) {
                t.Errorf("user = %v, want %v", user, tt.wantUser)
            }
        })
    }
}
```

---

## Test Helpers

### Helper Functions

```go
// Helper marked with t.Helper() for better error messages
func assertEqual(t *testing.T, got, want interface{}) {
    t.Helper()
    if !reflect.DeepEqual(got, want) {
        t.Errorf("got %v, want %v", got, want)
    }
}

func assertError(t *testing.T, err error, wantErr bool) {
    t.Helper()
    if (err != nil) != wantErr {
        t.Errorf("error = %v, wantErr %v", err, wantErr)
    }
}

func assertNil(t *testing.T, got interface{}) {
    t.Helper()
    if got != nil {
        t.Errorf("got %v, want nil", got)
    }
}
```

### Test Setup/Teardown

```go
func TestWithSetup(t *testing.T) {
    // Setup
    db := setupTestDB(t)

    // Cleanup runs even if test fails
    t.Cleanup(func() {
        db.Close()
    })

    // Test code...
}

func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("postgres", testDSN)
    if err != nil {
        t.Fatalf("failed to open db: %v", err)
    }
    return db
}
```

---

## Testing HTTP Handlers

### Basic Handler Test

```go
func TestHealthHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/health", nil)
    w := httptest.NewRecorder()

    handler := http.HandlerFunc(healthHandler)
    handler.ServeHTTP(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("status = %d; want %d", w.Code, http.StatusOK)
    }

    var response map[string]string
    json.Unmarshal(w.Body.Bytes(), &response)

    if response["status"] != "healthy" {
        t.Errorf("status = %s; want healthy", response["status"])
    }
}
```

### Gin Handler Test

```go
func TestGetUser(t *testing.T) {
    gin.SetMode(gin.TestMode)

    r := gin.New()
    r.GET("/users/:id", handlers.GetUser)

    req := httptest.NewRequest("GET", "/users/123", nil)
    w := httptest.NewRecorder()

    r.ServeHTTP(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("status = %d; want %d", w.Code, http.StatusOK)
    }
}
```

### Testing with Request Body

```go
func TestCreateUser(t *testing.T) {
    gin.SetMode(gin.TestMode)

    body := `{"name": "Alice", "email": "alice@example.com"}`
    req := httptest.NewRequest("POST", "/users", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")

    w := httptest.NewRecorder()

    r := gin.New()
    r.POST("/users", handlers.CreateUser)
    r.ServeHTTP(w, req)

    if w.Code != http.StatusCreated {
        t.Errorf("status = %d; want %d", w.Code, http.StatusCreated)
    }
}
```

---

## Mocking

### Interface-Based Mocking

```go
// Define interface
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

// Mock implementation
type mockUserRepo struct {
    users map[string]*User
    err   error
}

func (m *mockUserRepo) GetByID(ctx context.Context, id string) (*User, error) {
    if m.err != nil {
        return nil, m.err
    }
    user, ok := m.users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return user, nil
}

func (m *mockUserRepo) Create(ctx context.Context, user *User) error {
    if m.err != nil {
        return m.err
    }
    m.users[user.ID] = user
    return nil
}

// Use in tests
func TestUserService_GetByID(t *testing.T) {
    mock := &mockUserRepo{
        users: map[string]*User{
            "123": {ID: "123", Name: "Alice"},
        },
    }

    svc := NewUserService(mock)
    user, err := svc.GetByID(context.Background(), "123")

    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }
    if user.Name != "Alice" {
        t.Errorf("name = %s; want Alice", user.Name)
    }
}
```

---

## Benchmarks

### Basic Benchmark

```go
func BenchmarkCalculate(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Calculate(100)
    }
}
```

### Benchmark with Setup

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData(1000)

    b.ResetTimer() // Exclude setup from timing

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

### Parallel Benchmark

```go
func BenchmarkConcurrent(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            DoWork()
        }
    })
}
```

### Sub-Benchmarks

```go
func BenchmarkSort(b *testing.B) {
    sizes := []int{100, 1000, 10000}

    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            data := generateData(size)
            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                sort.Ints(data)
            }
        })
    }
}
```

---

## Test Coverage

### Running with Coverage

```bash
# Generate coverage profile
go test -coverprofile=coverage.out ./...

# View coverage in terminal
go tool cover -func=coverage.out

# View coverage in browser
go tool cover -html=coverage.out

# Check coverage percentage
go test -cover ./...
```

### Coverage Targets

| Level | Coverage | Notes |
|-------|----------|-------|
| Minimum | 80% | Required for CI pass |
| Good | 85-90% | Most projects target |
| Excellent | 90%+ | Critical paths |

### Excluding Files from Coverage

```go
//go:build !test
// +build !test

package main

// This file excluded from test builds
```

---

## Testing Best Practices

### Test Naming

```go
// Function: TestFunctionName
func TestValidateEmail(t *testing.T) {}

// Method: TestType_Method
func TestUser_IsActive(t *testing.T) {}

// Scenario: TestFunction_Scenario
func TestValidateEmail_EmptyString(t *testing.T) {}
```

### Parallel Tests

```go
func TestParallel(t *testing.T) {
    tests := []struct {
        name string
        // ...
    }{
        // ...
    }

    for _, tt := range tests {
        tt := tt // Capture range variable
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // Run in parallel
            // Test code...
        })
    }
}
```

### Test Isolation

```go
func TestIsolated(t *testing.T) {
    // Each test gets its own instance
    db := setupTestDB(t)
    t.Cleanup(func() { db.Close() })

    // Test with isolated database
}
```

---

## Common Commands

```bash
# Run all tests
go test ./...

# Run specific package
go test ./internal/user

# Run specific test
go test -run TestValidateEmail ./...

# Verbose output
go test -v ./...

# Run with race detector
go test -race ./...

# Short mode (skip long tests)
go test -short ./...

# Run benchmarks
go test -bench=. ./...

# Run benchmarks with memory allocation stats
go test -bench=. -benchmem ./...
```

---

*Companion to: testify-patterns.md, testing-strategies.md*
*Last updated: 2026-01-15*
