# Go Error Handling Patterns

Idiomatic error handling, wrapping, sentinel errors, and custom error types.

---

## Core Principles

1. **Errors are values** - Handle them, don't ignore them
2. **Wrap with context** - Add information at each level
3. **Check immediately** - Handle errors where they occur
4. **Fail fast** - Return early on errors

---

## Basic Patterns

### Always Check Errors

```go
// ❌ Bad: ignoring error
data, _ := json.Marshal(user)

// ✅ Good: handle error
data, err := json.Marshal(user)
if err != nil {
    return fmt.Errorf("marshal user: %w", err)
}

// ✅ Good: explicitly ignore with comment
_ = file.Close() // Error ignored: best effort cleanup
```

### Wrap with Context

```go
// ❌ Bad: no context
if err != nil {
    return err
}

// ✅ Good: add context
if err != nil {
    return fmt.Errorf("get user %s: %w", userID, err)
}

// ✅ Good: operation + identifier
if err != nil {
    return fmt.Errorf("create order for customer %s: %w", customerID, err)
}
```

### Handle Immediately

```go
// ❌ Bad: delayed error handling
result1, err1 := step1()
result2, err2 := step2()
result3, err3 := step3()

if err1 != nil { return err1 }
if err2 != nil { return err2 }
if err3 != nil { return err3 }

// ✅ Good: handle inline
result1, err := step1()
if err != nil {
    return fmt.Errorf("step1: %w", err)
}

result2, err := step2(result1)
if err != nil {
    return fmt.Errorf("step2: %w", err)
}

result3, err := step3(result2)
if err != nil {
    return fmt.Errorf("step3: %w", err)
}
```

---

## Sentinel Errors

### Definition

```go
package user

import "errors"

// Package-level sentinel errors
var (
    ErrNotFound     = errors.New("user not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
    ErrDuplicate    = errors.New("user already exists")
)
```

### Usage

```go
func (r *Repository) GetByID(ctx context.Context, id string) (*User, error) {
    user, err := r.db.GetUser(ctx, id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrNotFound
        }
        return nil, fmt.Errorf("query user: %w", err)
    }
    return user, nil
}
```

### Checking Sentinel Errors

```go
user, err := repo.GetByID(ctx, userID)
if err != nil {
    if errors.Is(err, user.ErrNotFound) {
        return c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
    }
    return c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
}
```

---

## Custom Error Types

### Simple Custom Error

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on %s: %s", e.Field, e.Message)
}

// Usage
func ValidateUser(u *User) error {
    if u.Email == "" {
        return &ValidationError{Field: "email", Message: "required"}
    }
    if len(u.Name) < 2 {
        return &ValidationError{Field: "name", Message: "too short"}
    }
    return nil
}
```

### Error with Code

```go
type AppError struct {
    Code    string
    Message string
    Err     error
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Err)
    }
    return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

func (e *AppError) Unwrap() error {
    return e.Err
}

// Constructors
func NewAppError(code, message string) *AppError {
    return &AppError{Code: code, Message: message}
}

func WrapAppError(err error, code, message string) *AppError {
    return &AppError{Code: code, Message: message, Err: err}
}

// Usage
const (
    ErrCodeNotFound = "NOT_FOUND"
    ErrCodeInvalid  = "INVALID_INPUT"
    ErrCodeInternal = "INTERNAL"
)

func GetUser(id string) (*User, error) {
    user, err := db.Query(id)
    if err != nil {
        return nil, WrapAppError(err, ErrCodeInternal, "database query failed")
    }
    if user == nil {
        return nil, NewAppError(ErrCodeNotFound, "user not found")
    }
    return user, nil
}
```

### Checking Custom Errors

```go
// Using errors.As
var appErr *AppError
if errors.As(err, &appErr) {
    switch appErr.Code {
    case ErrCodeNotFound:
        return c.JSON(http.StatusNotFound, gin.H{"error": appErr.Message})
    case ErrCodeInvalid:
        return c.JSON(http.StatusBadRequest, gin.H{"error": appErr.Message})
    default:
        return c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
    }
}

// Using errors.Is for sentinel comparison
if errors.Is(err, ErrNotFound) {
    // Handle not found
}
```

---

## Multi-Error Handling

### Collecting Multiple Errors

```go
type MultiError struct {
    Errors []error
}

func (m *MultiError) Error() string {
    if len(m.Errors) == 0 {
        return "no errors"
    }
    if len(m.Errors) == 1 {
        return m.Errors[0].Error()
    }

    var b strings.Builder
    fmt.Fprintf(&b, "%d errors occurred:\n", len(m.Errors))
    for i, err := range m.Errors {
        fmt.Fprintf(&b, "  %d: %v\n", i+1, err)
    }
    return b.String()
}

func (m *MultiError) Add(err error) {
    if err != nil {
        m.Errors = append(m.Errors, err)
    }
}

func (m *MultiError) HasErrors() bool {
    return len(m.Errors) > 0
}

func (m *MultiError) ErrorOrNil() error {
    if m.HasErrors() {
        return m
    }
    return nil
}

// Usage
func ValidateOrder(o *Order) error {
    var errs MultiError

    if o.CustomerID == "" {
        errs.Add(errors.New("customer_id required"))
    }
    if len(o.Items) == 0 {
        errs.Add(errors.New("at least one item required"))
    }
    for i, item := range o.Items {
        if item.Quantity <= 0 {
            errs.Add(fmt.Errorf("item %d: quantity must be positive", i))
        }
    }

    return errs.ErrorOrNil()
}
```

### Using errors.Join (Go 1.20+)

```go
func ValidateUser(u *User) error {
    var errs []error

    if u.Email == "" {
        errs = append(errs, errors.New("email required"))
    }
    if u.Name == "" {
        errs = append(errs, errors.New("name required"))
    }

    return errors.Join(errs...)
}
```

---

## Error Wrapping Chain

### Building Context Through Layers

```go
// Repository layer
func (r *UserRepo) GetByID(ctx context.Context, id string) (*User, error) {
    user, err := r.queries.GetUser(ctx, id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrNotFound
        }
        return nil, fmt.Errorf("query user %s: %w", id, err)
    }
    return user, nil
}

// Service layer
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    return user, nil
}

// Handler layer
func (h *UserHandler) GetUser(c *gin.Context) {
    id := c.Param("id")

    user, err := h.service.GetUser(c.Request.Context(), id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
            return
        }
        h.logger.Error("get user failed", "error", err)
        c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
        return
    }

    c.JSON(http.StatusOK, user)
}
```

---

## HTTP Error Responses

### Gin Error Handler

```go
type HTTPError struct {
    Code    int    `json:"-"`
    Message string `json:"error"`
    Details any    `json:"details,omitempty"`
}

func (e *HTTPError) Error() string {
    return e.Message
}

func NewHTTPError(code int, message string) *HTTPError {
    return &HTTPError{Code: code, Message: message}
}

// Error handler middleware
func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        if len(c.Errors) == 0 {
            return
        }

        err := c.Errors.Last().Err

        // Check for custom HTTP error
        var httpErr *HTTPError
        if errors.As(err, &httpErr) {
            c.JSON(httpErr.Code, httpErr)
            return
        }

        // Check for validation error
        var valErr *ValidationError
        if errors.As(err, &valErr) {
            c.JSON(http.StatusBadRequest, gin.H{
                "error":   "validation failed",
                "field":   valErr.Field,
                "message": valErr.Message,
            })
            return
        }

        // Check for not found
        if errors.Is(err, ErrNotFound) {
            c.JSON(http.StatusNotFound, gin.H{"error": "resource not found"})
            return
        }

        // Default to 500
        c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
    }
}

// Usage in handlers
func (h *Handler) CreateUser(c *gin.Context) {
    var input CreateUserInput
    if err := c.ShouldBindJSON(&input); err != nil {
        c.Error(NewHTTPError(http.StatusBadRequest, "invalid request body"))
        return
    }

    user, err := h.service.Create(c.Request.Context(), input)
    if err != nil {
        c.Error(err) // Let middleware handle
        return
    }

    c.JSON(http.StatusCreated, user)
}
```

---

## Panic Recovery

### Recovery Middleware

```go
func RecoveryMiddleware(logger *slog.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if r := recover(); r != nil {
                // Log with stack trace
                logger.Error("panic recovered",
                    slog.Any("panic", r),
                    slog.String("stack", string(debug.Stack())),
                )

                c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
                    "error": "internal server error",
                })
            }
        }()

        c.Next()
    }
}
```

### When to Panic

```go
// ✅ Panic: Programmer error, unrecoverable
func MustParseTemplate(name string) *template.Template {
    t, err := template.ParseFiles(name)
    if err != nil {
        panic(fmt.Sprintf("failed to parse template %s: %v", name, err))
    }
    return t
}

// ❌ Don't panic: User input, recoverable
func ParseUserInput(input string) (*Data, error) {
    // Return error, don't panic
    return nil, fmt.Errorf("invalid input: %s", input)
}
```

---

## Best Practices Summary

| Practice | Do | Don't |
|----------|-----|-------|
| **Check errors** | Always handle or explicitly ignore | Use `_` without comment |
| **Add context** | `fmt.Errorf("op: %w", err)` | Return bare `err` |
| **Sentinel errors** | Package-level `var ErrX = errors.New()` | String comparison |
| **Check errors** | `errors.Is()`, `errors.As()` | Type assertion directly |
| **Custom types** | Implement `Error()` and `Unwrap()` | Forget `Unwrap()` |
| **Panic** | Programmer errors only | User input errors |
| **Log errors** | At handler/boundary level | At every level |

---

*Companion to: style-guide.md, clean-code.md*
*Last updated: 2026-01-15*
