# Go Type Patterns

Interface design, generics, composition, and type-safe patterns for Go.

---

## Interface Patterns

### Accept Interfaces, Return Structs

The most important Go pattern: functions should accept interfaces and return concrete types.

```go
// ✅ Good: accept interface parameter
func ProcessData(r io.Reader) ([]byte, error) {
    return io.ReadAll(r)
}

// ✅ Good: return concrete type
func NewUserService(db *sql.DB) *UserService {
    return &UserService{db: db}
}

// Usage: any io.Reader works
ProcessData(os.Stdin)              // *os.File
ProcessData(strings.NewReader("")) // *strings.Reader
ProcessData(bytes.NewReader(data)) // *bytes.Reader
```

**Why:**
- Callers can pass any implementation
- Return type has all methods available
- Allows evolution without breaking changes

### Small, Focused Interfaces

Go favors small interfaces (1-3 methods). Large interfaces are harder to implement and mock.

```go
// ✅ Good: single-method interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

type Validator interface {
    Validate() error
}

// ✅ Good: composed interfaces
type ReadWriter interface {
    Reader
    Writer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

### Interface Naming

| Pattern | Example |
|---------|---------|
| Single method | Verb + `-er`: `Reader`, `Writer`, `Closer` |
| Multiple methods | Descriptive noun: `UserRepository`, `EventHandler` |
| Behavior | What it does: `Validator`, `Marshaler` |

### Don't Export Interfaces for Implementation

```go
// ✅ Good: interface defined where it's USED
// In consumer package
type UserGetter interface {
    GetUser(ctx context.Context, id string) (*User, error)
}

func NewOrderService(users UserGetter) *OrderService {
    return &OrderService{users: users}
}

// ❌ Bad: interface defined where it's IMPLEMENTED
// In provider package (often unnecessary)
type UserServiceInterface interface {
    GetUser(ctx context.Context, id string) (*User, error)
    CreateUser(ctx context.Context, user *User) error
    // ... 20 more methods
}
```

---

## Generics

### Basic Generic Functions

```go
// Generic function
func Map[T, U any](items []T, fn func(T) U) []U {
    result := make([]U, len(items))
    for i, item := range items {
        result[i] = fn(item)
    }
    return result
}

// Usage
names := Map(users, func(u User) string { return u.Name })
ids := Map(orders, func(o Order) int { return o.ID })
```

### Generic Types

```go
// Generic container
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

// Usage
intStack := &Stack[int]{}
intStack.Push(1)
intStack.Push(2)

stringStack := &Stack[string]{}
stringStack.Push("hello")
```

### Type Constraints

```go
// Built-in constraints
import "golang.org/x/exp/constraints"

func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// Custom constraints
type Number interface {
    ~int | ~int32 | ~int64 | ~float32 | ~float64
}

func Sum[T Number](items []T) T {
    var total T
    for _, item := range items {
        total += item
    }
    return total
}
```

### When to Use Generics

| Use Generics | Avoid Generics |
|--------------|----------------|
| Container types (Stack, Queue, Set) | Domain-specific types |
| Utility functions (Map, Filter) | Simple functions |
| Type-safe collections | When `any` or interface works |
| Generic algorithms | When it adds complexity |

```go
// ✅ Good use: generic Set
type Set[T comparable] map[T]struct{}

func (s Set[T]) Add(item T) {
    s[item] = struct{}{}
}

func (s Set[T]) Contains(item T) bool {
    _, ok := s[item]
    return ok
}

// ❌ Bad use: unnecessary generic
func GetUserByID[T User](id string) T // Just use User type
```

---

## Composition Patterns

### Struct Embedding

```go
// Embed for code reuse
type Logger struct {
    prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

type UserService struct {
    Logger  // Embedded - UserService gains Log method
    db *sql.DB
}

// Usage
svc := &UserService{
    Logger: Logger{prefix: "user"},
    db:     db,
}
svc.Log("Creating user")  // Log promoted to UserService
```

### Interface Embedding

```go
type ReadWriter interface {
    io.Reader
    io.Writer
}

// Combine custom interfaces
type UserRepository interface {
    UserReader
    UserWriter
}

type UserReader interface {
    FindByID(ctx context.Context, id string) (*User, error)
    FindByEmail(ctx context.Context, email string) (*User, error)
}

type UserWriter interface {
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}
```

### Decorator Pattern

```go
// Base interface
type Handler interface {
    Handle(ctx context.Context, req Request) Response
}

// Decorator
type LoggingHandler struct {
    next   Handler
    logger *log.Logger
}

func (h *LoggingHandler) Handle(ctx context.Context, req Request) Response {
    h.logger.Printf("Handling request: %+v", req)
    resp := h.next.Handle(ctx, req)
    h.logger.Printf("Response: %+v", resp)
    return resp
}

// Chain decorators
handler := &LoggingHandler{
    next: &MetricsHandler{
        next: &AuthHandler{
            next: &RealHandler{},
        },
    },
    logger: logger,
}
```

---

## Functional Options

```go
type Server struct {
    host    string
    port    int
    timeout time.Duration
    tls     *tls.Config
}

type ServerOption func(*Server)

func WithPort(port int) ServerOption {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(d time.Duration) ServerOption {
    return func(s *Server) {
        s.timeout = d
    }
}

func WithTLS(config *tls.Config) ServerOption {
    return func(s *Server) {
        s.tls = config
    }
}

func NewServer(host string, opts ...ServerOption) *Server {
    s := &Server{
        host:    host,
        port:    8080,
        timeout: 30 * time.Second,
    }

    for _, opt := range opts {
        opt(s)
    }

    return s
}

// Usage
server := NewServer("localhost",
    WithPort(3000),
    WithTimeout(60*time.Second),
    WithTLS(tlsConfig),
)
```

---

## Type Assertions and Switches

### Type Assertions

```go
// Check if value implements interface
func process(v any) {
    // Type assertion with check
    if s, ok := v.(Stringer); ok {
        fmt.Println(s.String())
    }

    // Type assertion without check (panics if wrong)
    s := v.(Stringer)
    fmt.Println(s.String())
}
```

### Type Switches

```go
func describe(v any) string {
    switch x := v.(type) {
    case nil:
        return "nil"
    case int:
        return fmt.Sprintf("int: %d", x)
    case string:
        return fmt.Sprintf("string: %s", x)
    case bool:
        return fmt.Sprintf("bool: %t", x)
    case Stringer:
        return fmt.Sprintf("stringer: %s", x.String())
    default:
        return fmt.Sprintf("unknown: %T", x)
    }
}
```

---

## Value vs Pointer Receivers

### When to Use Pointer Receivers

```go
// ✅ Use pointer when:
// 1. Method modifies the receiver
func (u *User) SetName(name string) {
    u.name = name
}

// 2. Receiver is large struct (avoid copying)
func (d *LargeData) Process() {
    // ...
}

// 3. Consistency (if one method needs pointer, all should use pointer)
func (u *User) Name() string {
    return u.name
}
```

### When to Use Value Receivers

```go
// ✅ Use value when:
// 1. Method doesn't modify receiver
// 2. Receiver is small (primitive, small struct)
// 3. Receiver is a map, func, or chan (already reference types)

type Point struct {
    X, Y float64
}

func (p Point) Distance(q Point) float64 {
    return math.Sqrt((p.X-q.X)*(p.X-q.X) + (p.Y-q.Y)*(p.Y-q.Y))
}
```

### Consistency Rule

```go
// ✅ All methods use same receiver type
type User struct {
    id   string
    name string
}

func (u *User) ID() string   { return u.id }
func (u *User) Name() string { return u.name }
func (u *User) SetName(name string) { u.name = name }

// ❌ Mixed receivers (confusing)
func (u User) ID() string { return u.id }
func (u *User) SetName(name string) { u.name = name }
```

---

## Type Safety Patterns

### Wrapper Types for Safety

```go
// Wrapper types prevent mixing up values
type UserID string
type OrderID string

func GetUser(id UserID) (*User, error) { ... }
func GetOrder(id OrderID) (*Order, error) { ... }

// Compile-time safety
userID := UserID("user-123")
orderID := OrderID("order-456")

GetUser(userID)   // ✅ Works
GetUser(orderID)  // ❌ Compile error
```

### Enums with Constants

```go
type Status string

const (
    StatusPending  Status = "pending"
    StatusActive   Status = "active"
    StatusInactive Status = "inactive"
)

func (s Status) IsValid() bool {
    switch s {
    case StatusPending, StatusActive, StatusInactive:
        return true
    }
    return false
}

func UpdateStatus(s Status) error {
    if !s.IsValid() {
        return fmt.Errorf("invalid status: %s", s)
    }
    // ...
}
```

---

## Summary

| Pattern | Use When |
|---------|----------|
| Accept interfaces | Function needs specific behavior |
| Return structs | Caller needs concrete type |
| Small interfaces | Define minimal required behavior |
| Generics | Container types, utility functions |
| Embedding | Code reuse, composition |
| Functional options | Many optional parameters |
| Type assertions | Need to check/convert interface type |
| Pointer receivers | Mutation, large structs |
| Value receivers | Small, immutable types |
| Wrapper types | Type safety for IDs, values |

---

*Companion to: style-guide.md, clean-code.md*
*Last updated: 2026-01-15*
