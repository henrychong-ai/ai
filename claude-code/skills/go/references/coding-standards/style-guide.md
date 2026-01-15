# Go Style Guide

Concise conventions for consistent, maintainable Go code. Based on [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments).

---

## Core Principles

1. **Clarity over cleverness** - Code is read more than written
2. **Consistency is key** - Follow conventions uniformly
3. **Enforce with tooling** - golangci-lint, gofumpt
4. **Composition over inheritance** - Small interfaces, embedding

---

## Naming Conventions

### Variables

| Type | Convention | Example |
|------|------------|---------|
| Local variables | camelCase, short | `i`, `user`, `buf` |
| Loop variables | Single letter | `i`, `j`, `k` |
| Receiver | 1-2 letters | `u` for `*User`, `s` for `*Server` |
| Exported | CamelCase | `UserCount`, `MaxRetries` |
| Unexported | camelCase | `userCount`, `maxRetries` |

```go
// Short names for small scopes
for i := 0; i < len(users); i++ {
    u := users[i]
    // ...
}

// Descriptive names for larger scopes
func processUserRegistration(registrationData *RegistrationData) error {
    validationResult := validateRegistration(registrationData)
    // ...
}

// Receiver names
func (u *User) FullName() string {
    return u.FirstName + " " + u.LastName
}

func (s *Server) Start() error {
    return s.listener.Accept()
}
```

### Functions

| Context | Convention | Example |
|---------|------------|---------|
| Exported | CamelCase, verb-first | `GetUser`, `CreateOrder` |
| Unexported | camelCase, verb-first | `getUser`, `createOrder` |
| Constructors | `New*` | `NewServer`, `NewUserService` |
| Getters | No `Get` prefix | `Name()` not `GetName()` |
| Setters | `Set*` prefix | `SetName()` |
| Predicates | `Is*`, `Has*`, `Can*` | `IsValid`, `HasPermission` |

```go
// Constructors
func NewServer(addr string) *Server {
    return &Server{addr: addr}
}

// Getters (no Get prefix)
func (u *User) Name() string {
    return u.name
}

// Setters
func (u *User) SetName(name string) {
    u.name = name
}

// Predicates
func (u *User) IsActive() bool {
    return u.status == StatusActive
}
```

### Types

| Type | Convention | Example |
|------|------------|---------|
| Structs | CamelCase, noun | `User`, `OrderService` |
| Interfaces | CamelCase, `-er` suffix | `Reader`, `Validator` |
| Type aliases | CamelCase | `UserID`, `OrderStatus` |

```go
// Structs
type User struct {
    ID        string
    Name      string
    CreatedAt time.Time
}

// Interfaces (single method = -er suffix)
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Validator interface {
    Validate() error
}

// Interfaces (multiple methods = descriptive name)
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
}
```

### Packages

| Type | Convention | Example |
|------|------------|---------|
| Package names | lowercase, short | `http`, `user`, `db` |
| No underscores | | `userservice` not `user_service` |
| No plural | | `user` not `users` |
| No generic names | | Avoid `util`, `common`, `helper` |

```go
// Good package names
package user
package orderservice
package db

// Bad package names
package users          // No plural
package user_service   // No underscores
package util           // Too generic
```

### Files

| Type | Convention | Example |
|------|------------|---------|
| Source files | lowercase, snake_case | `user_service.go` |
| Test files | `*_test.go` | `user_service_test.go` |
| Platform-specific | `*_linux.go`, `*_darwin.go` | `fs_linux.go` |

### Acronyms

Keep acronyms in the style they appear (all caps or all lower):

```go
// ✅ Good
type HTTPClient struct{}
func ServeHTTP(w http.ResponseWriter, r *http.Request)
var userID string
type XMLParser struct{}
const maxURLLength = 2048

// ❌ Bad
type HttpClient struct{}
func ServeHttp(w http.ResponseWriter, r *http.Request)
var usrId string
type XmlParser struct{}
```

**Common acronyms:** HTTP, URL, ID, API, JSON, XML, SQL, HTML, CSS, RPC, TCP, UDP, IP, EOF, UUID

---

## Interface Design

### Accept Interfaces, Return Structs

```go
// ✅ Good: accept interface
func ProcessData(r io.Reader) error {
    data, err := io.ReadAll(r)
    // ...
}

// ✅ Good: return concrete type
func NewServer(addr string) *Server {
    return &Server{addr: addr}
}

// ❌ Bad: return interface (usually)
func NewServer(addr string) ServerInterface {
    return &Server{addr: addr}
}
```

### Small, Focused Interfaces

```go
// ✅ Good: single-method interface
type Validator interface {
    Validate() error
}

type Stringer interface {
    String() string
}

// ❌ Bad: kitchen sink interface
type UserService interface {
    Create(user *User) error
    Update(user *User) error
    Delete(id string) error
    Find(id string) (*User, error)
    List() ([]*User, error)
    Validate(user *User) error
    SendEmail(user *User, subject, body string) error
    // ... 20 more methods
}
```

### Interface Segregation

```go
// ✅ Good: composed interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

---

## Error Handling

### Always Check Errors

```go
// ✅ Good
f, err := os.Open(filename)
if err != nil {
    return fmt.Errorf("open %s: %w", filename, err)
}
defer f.Close()

// ❌ Bad: ignoring error
f, _ := os.Open(filename)
```

### Error Wrapping

```go
// ✅ Good: add context with %w
func readConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("readConfig(%s): %w", path, err)
    }
    // ...
}

// Check wrapped errors
if errors.Is(err, os.ErrNotExist) {
    // Handle file not found
}
```

### Sentinel Errors

```go
// Define at package level
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
)

// Use in functions
func GetUser(id string) (*User, error) {
    user := db.Find(id)
    if user == nil {
        return nil, ErrNotFound
    }
    return user, nil
}

// Check with errors.Is
if errors.Is(err, ErrNotFound) {
    // Handle not found
}
```

---

## Code Organization

### Package Structure

```
project/
├── cmd/                    # Entry points
│   └── server/
│       └── main.go
├── internal/               # Private packages
│   ├── api/
│   ├── db/
│   └── service/
├── pkg/                    # Public packages (rare)
└── go.mod
```

### Import Grouping

```go
import (
    // Standard library
    "context"
    "fmt"
    "net/http"

    // Third-party
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"

    // Internal
    "github.com/username/project/internal/db"
    "github.com/username/project/internal/service"
)
```

gofumpt/goimports will auto-organize imports.

### File Organization

```go
// 1. Package declaration
package user

// 2. Imports
import (
    "context"
)

// 3. Constants
const (
    MaxNameLength = 100
)

// 4. Variables (package-level, avoid if possible)
var (
    ErrNotFound = errors.New("user not found")
)

// 5. Types
type User struct {
    ID   string
    Name string
}

// 6. Constructor functions
func NewUser(name string) *User {
    return &User{Name: name}
}

// 7. Methods (grouped by receiver)
func (u *User) Validate() error {
    // ...
}

// 8. Functions (non-methods)
func ValidateName(name string) error {
    // ...
}
```

---

## Functions

### Parameters

```go
// ✅ Good: options pattern for many parameters
type ServerOptions struct {
    Port    int
    Timeout time.Duration
    TLS     *tls.Config
}

func NewServer(opts ServerOptions) *Server {
    // ...
}

// ✅ Good: functional options
type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func NewServer(opts ...Option) *Server {
    s := &Server{port: 8080}
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// ❌ Bad: many positional parameters
func NewServer(port int, timeout time.Duration, tls *tls.Config, maxConns int) *Server
```

### Return Values

```go
// Named returns for documentation (don't use bare return)
func divide(a, b float64) (result float64, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return 0, err  // Explicit return, not bare
    }
    return a / b, nil
}
```

---

## Comments

### Package Comments

```go
// Package user provides user management functionality including
// creation, authentication, and authorization.
package user
```

### Function Comments

```go
// GetUser retrieves a user by ID from the database.
// It returns ErrNotFound if the user doesn't exist.
func GetUser(ctx context.Context, id string) (*User, error) {
    // ...
}
```

### Explain Why, Not What

```go
// ❌ Bad: explains what (obvious)
// Increment counter
counter++

// ✅ Good: explains why (not obvious)
// Start at 1 because initial request counts as first attempt
retryCount = 1
```

---

## Constants and Variables

### Const Groups

```go
// Related constants grouped
const (
    StatusPending  = "pending"
    StatusActive   = "active"
    StatusInactive = "inactive"
)

// iota for sequential values
const (
    Sunday = iota
    Monday
    Tuesday
    // ...
)
```

### Avoid Package-Level Variables

```go
// ❌ Bad: mutable package state
var globalDB *sql.DB

// ✅ Good: pass dependencies explicitly
type UserService struct {
    db *sql.DB
}
```

---

## Summary

| Category | Convention |
|----------|------------|
| Variables | camelCase (short for small scope) |
| Exported | CamelCase |
| Unexported | camelCase |
| Constructors | `New*` |
| Getters | No `Get` prefix |
| Predicates | `Is*`, `Has*`, `Can*` |
| Interfaces | `-er` suffix for single method |
| Packages | lowercase, short, no plural |
| Files | snake_case.go |
| Tests | `*_test.go` |
| Acronyms | Preserve case (HTTP, URL, ID) |
| Errors | Always check, wrap with `%w` |
| Imports | Group by: stdlib, third-party, internal |

---

*Based on: [Effective Go](https://go.dev/doc/effective_go), [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)*
*Companion to: type-patterns.md, clean-code.md*
*Last updated: 2026-01-15*
