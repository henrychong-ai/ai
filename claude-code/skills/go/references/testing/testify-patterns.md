# Testify Patterns

Assertions, mocking, and test suites with stretchr/testify.

---

## Installation

```bash
go get github.com/stretchr/testify
```

---

## Assert Package

### Basic Assertions

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestUser(t *testing.T) {
    user := NewUser("Alice", "alice@example.com")

    // Equality
    assert.Equal(t, "Alice", user.Name)
    assert.NotEqual(t, "", user.ID)

    // Boolean
    assert.True(t, user.IsActive())
    assert.False(t, user.IsDeleted())

    // Nil checks
    assert.Nil(t, user.DeletedAt)
    assert.NotNil(t, user.CreatedAt)

    // Contains
    assert.Contains(t, user.Email, "@")
    assert.NotContains(t, user.Name, "Bob")

    // Length
    assert.Len(t, user.Roles, 1)
    assert.Empty(t, user.Permissions)
    assert.NotEmpty(t, user.ID)
}
```

### Error Assertions

```go
func TestValidation(t *testing.T) {
    // Error exists
    err := ValidateEmail("")
    assert.Error(t, err)

    // No error
    err = ValidateEmail("valid@example.com")
    assert.NoError(t, err)

    // Specific error
    err = GetUser("nonexistent")
    assert.ErrorIs(t, err, ErrNotFound)

    // Error type
    var validationErr *ValidationError
    assert.ErrorAs(t, err, &validationErr)
}
```

### Collection Assertions

```go
func TestCollections(t *testing.T) {
    users := []User{
        {Name: "Alice"},
        {Name: "Bob"},
    }

    // Length
    assert.Len(t, users, 2)

    // Contains element
    assert.Contains(t, users, User{Name: "Alice"})

    // Subset
    assert.Subset(t, []string{"a", "b", "c"}, []string{"a", "c"})

    // Element wise
    assert.ElementsMatch(t, []int{1, 2, 3}, []int{3, 2, 1})
}
```

### Type Assertions

```go
func TestTypes(t *testing.T) {
    var i interface{} = "hello"

    assert.IsType(t, "", i)
    assert.Implements(t, (*fmt.Stringer)(nil), time.Now())
}
```

---

## Require Package

`require` is like `assert` but fails immediately (calls `t.FailNow()`).

```go
import "github.com/stretchr/testify/require"

func TestWithRequire(t *testing.T) {
    user, err := CreateUser("Alice", "alice@example.com")

    // If error, stop test immediately
    require.NoError(t, err)
    require.NotNil(t, user)

    // Continue with assertions that depend on user existing
    assert.Equal(t, "Alice", user.Name)
    assert.NotEmpty(t, user.ID)
}
```

### When to Use require vs assert

| Use `require` | Use `assert` |
|---------------|--------------|
| Setup operations | Multiple independent checks |
| Preconditions | Non-fatal failures |
| Error that makes further tests meaningless | Want to see all failures |

```go
func TestUserWorkflow(t *testing.T) {
    // require for setup - can't continue without user
    user, err := CreateUser("Alice", "alice@example.com")
    require.NoError(t, err)
    require.NotNil(t, user)

    // assert for validations - want to see all failures
    assert.Equal(t, "Alice", user.Name)
    assert.Equal(t, "alice@example.com", user.Email)
    assert.False(t, user.IsDeleted())
}
```

---

## Test Suites

### Basic Suite

```go
import (
    "testing"
    "github.com/stretchr/testify/suite"
)

type UserServiceSuite struct {
    suite.Suite
    service *UserService
    db      *sql.DB
}

// SetupSuite runs once before all tests
func (s *UserServiceSuite) SetupSuite() {
    db, err := sql.Open("postgres", testDSN)
    s.Require().NoError(err)
    s.db = db
}

// TearDownSuite runs once after all tests
func (s *UserServiceSuite) TearDownSuite() {
    s.db.Close()
}

// SetupTest runs before each test
func (s *UserServiceSuite) SetupTest() {
    s.service = NewUserService(s.db)
    // Clean tables, seed data, etc.
}

// TearDownTest runs after each test
func (s *UserServiceSuite) TearDownTest() {
    // Cleanup
}

// Test methods must start with "Test"
func (s *UserServiceSuite) TestCreateUser() {
    user, err := s.service.Create(context.Background(), "Alice", "alice@example.com")

    s.NoError(err)
    s.NotNil(user)
    s.Equal("Alice", user.Name)
}

func (s *UserServiceSuite) TestGetUser() {
    // Create user first
    created, err := s.service.Create(context.Background(), "Bob", "bob@example.com")
    s.Require().NoError(err)

    // Get user
    user, err := s.service.GetByID(context.Background(), created.ID)

    s.NoError(err)
    s.Equal("Bob", user.Name)
}

func (s *UserServiceSuite) TestGetUser_NotFound() {
    user, err := s.service.GetByID(context.Background(), "nonexistent")

    s.ErrorIs(err, ErrNotFound)
    s.Nil(user)
}

// Run the suite
func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceSuite))
}
```

### Suite with Embedded Assertions

```go
type MySuite struct {
    suite.Suite
}

func (s *MySuite) TestExample() {
    // Suite embeds assert methods
    s.Equal(1, 1)
    s.NoError(nil)
    s.True(true)

    // Require methods also available
    s.Require().NotNil(someValue)
}
```

---

## Mock Package

### Generating Mocks

```bash
# Install mockery
go install github.com/vektra/mockery/v2@latest

# Generate mock for interface
mockery --name=UserRepository --output=mocks
```

### Using Generated Mocks

```go
import (
    "testing"
    "github.com/stretchr/testify/mock"
    "myapp/mocks"
)

func TestUserService_GetByID(t *testing.T) {
    // Create mock
    mockRepo := new(mocks.UserRepository)

    // Setup expectation
    mockRepo.On("GetByID", mock.Anything, "123").
        Return(&User{ID: "123", Name: "Alice"}, nil)

    // Create service with mock
    svc := NewUserService(mockRepo)

    // Execute
    user, err := svc.GetByID(context.Background(), "123")

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)

    // Verify expectations were met
    mockRepo.AssertExpectations(t)
}
```

### Mock Patterns

```go
func TestMockPatterns(t *testing.T) {
    mockRepo := new(mocks.UserRepository)

    // Exact match
    mockRepo.On("GetByID", mock.Anything, "123").
        Return(&User{ID: "123"}, nil)

    // Any argument
    mockRepo.On("Create", mock.Anything, mock.Anything).
        Return(nil)

    // Matching function
    mockRepo.On("Search", mock.Anything, mock.MatchedBy(func(q string) bool {
        return len(q) > 0
    })).Return([]User{}, nil)

    // Return error
    mockRepo.On("Delete", mock.Anything, "protected").
        Return(errors.New("cannot delete"))

    // Run function (side effects)
    mockRepo.On("Create", mock.Anything, mock.AnythingOfType("*User")).
        Run(func(args mock.Arguments) {
            user := args.Get(1).(*User)
            user.ID = "generated-id"
        }).
        Return(nil)

    // Call count
    mockRepo.On("GetByID", mock.Anything, "456").
        Return(&User{}, nil).
        Once() // Expect exactly one call

    mockRepo.On("List", mock.Anything).
        Return([]User{}, nil).
        Times(2) // Expect exactly two calls
}
```

### Manual Mock

```go
type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) GetByID(ctx context.Context, id string) (*User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) Create(ctx context.Context, user *User) error {
    args := m.Called(ctx, user)
    return args.Error(0)
}
```

---

## Table-Driven Tests with Testify

```go
func TestCalculate(t *testing.T) {
    tests := []struct {
        name     string
        input    int
        expected int
        wantErr  bool
    }{
        {"positive", 5, 25, false},
        {"zero", 0, 0, false},
        {"negative", -1, 0, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Calculate(tt.input)

            if tt.wantErr {
                assert.Error(t, err)
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

---

## HTTP Testing

```go
func TestHandler(t *testing.T) {
    mockSvc := new(mocks.UserService)
    mockSvc.On("GetByID", mock.Anything, "123").
        Return(&User{ID: "123", Name: "Alice"}, nil)

    handler := NewHandler(mockSvc)

    req := httptest.NewRequest("GET", "/users/123", nil)
    w := httptest.NewRecorder()

    handler.GetUser(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    var response User
    err := json.Unmarshal(w.Body.Bytes(), &response)
    require.NoError(t, err)
    assert.Equal(t, "Alice", response.Name)

    mockSvc.AssertExpectations(t)
}
```

---

## Common Assertion Patterns

### Comparing Structs

```go
func TestStructEquality(t *testing.T) {
    expected := User{ID: "1", Name: "Alice"}
    actual := GetUser("1")

    // Full equality
    assert.Equal(t, expected, actual)

    // Partial equality (ignore some fields)
    assert.Equal(t, expected.Name, actual.Name)
    assert.NotEmpty(t, actual.CreatedAt) // Just check it's set
}
```

### Testing Time

```go
func TestWithTime(t *testing.T) {
    user := CreateUser("Alice")

    // Within duration
    assert.WithinDuration(t, time.Now(), user.CreatedAt, time.Second)

    // Not zero
    assert.False(t, user.CreatedAt.IsZero())
}
```

### Testing Panics

```go
func TestPanic(t *testing.T) {
    assert.Panics(t, func() {
        MustParse("invalid")
    })

    assert.NotPanics(t, func() {
        MustParse("valid")
    })

    assert.PanicsWithValue(t, "invalid input", func() {
        MustParse("invalid")
    })
}
```

---

## Best Practices

| Practice | Do | Don't |
|----------|-----|-------|
| **Require vs Assert** | Use require for setup, assert for validation | Use only one |
| **Mock verification** | Call `AssertExpectations(t)` | Forget to verify |
| **Table tests** | Use descriptive test names | Generic "test1", "test2" |
| **Suites** | Use for shared setup/teardown | Overuse for simple tests |
| **Error messages** | Let testify generate messages | Add redundant messages |

---

*Companion to: go-test-patterns.md, testing-strategies.md*
*Last updated: 2026-01-15*
