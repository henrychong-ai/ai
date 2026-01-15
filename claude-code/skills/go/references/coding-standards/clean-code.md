# Clean Code Principles for Go

Writing readable, maintainable, and idiomatic Go code.

---

## Core Principles

1. **Simplicity** - The simplest solution that works
2. **Clarity** - Code intent is immediately obvious
3. **Consistency** - Same patterns throughout codebase
4. **Composition** - Small pieces combined effectively

---

## Function Design

### Single Responsibility

```go
// ❌ Bad: function does too much
func ProcessUserRegistration(data RegistrationData) error {
    // Validate
    if data.Email == "" {
        return errors.New("email required")
    }
    // Hash password
    hash, _ := bcrypt.GenerateFromPassword([]byte(data.Password), 10)
    // Save to database
    db.Exec("INSERT INTO users...")
    // Send email
    smtp.Send(data.Email, "Welcome!")
    // Log
    log.Printf("User registered: %s", data.Email)
    return nil
}

// ✅ Good: separate concerns
func (s *UserService) Register(ctx context.Context, data RegistrationData) error {
    if err := s.validator.Validate(data); err != nil {
        return fmt.Errorf("validation: %w", err)
    }

    user, err := s.createUser(ctx, data)
    if err != nil {
        return fmt.Errorf("create user: %w", err)
    }

    if err := s.notifier.SendWelcome(ctx, user); err != nil {
        s.logger.Error("failed to send welcome email", "error", err)
        // Non-fatal, don't return error
    }

    return nil
}
```

### Short Functions

```go
// ❌ Bad: 100+ line function
func processData(data []byte) error {
    // ... 100 lines of code ...
}

// ✅ Good: extract logical units
func processData(data []byte) error {
    parsed, err := parseData(data)
    if err != nil {
        return fmt.Errorf("parse: %w", err)
    }

    validated, err := validateData(parsed)
    if err != nil {
        return fmt.Errorf("validate: %w", err)
    }

    return storeData(validated)
}
```

### Early Returns

```go
// ❌ Bad: nested conditionals
func processUser(user *User) error {
    if user != nil {
        if user.IsActive {
            if user.HasPermission("admin") {
                // Finally do something
                return doAdminStuff(user)
            } else {
                return ErrNoPermission
            }
        } else {
            return ErrInactiveUser
        }
    } else {
        return ErrNilUser
    }
}

// ✅ Good: guard clauses with early returns
func processUser(user *User) error {
    if user == nil {
        return ErrNilUser
    }
    if !user.IsActive {
        return ErrInactiveUser
    }
    if !user.HasPermission("admin") {
        return ErrNoPermission
    }

    return doAdminStuff(user)
}
```

---

## Error Handling

### Handle Errors Immediately

```go
// ❌ Bad: error handling far from cause
func process() error {
    result1, err1 := step1()
    result2, err2 := step2()
    result3, err3 := step3()

    if err1 != nil {
        return err1
    }
    if err2 != nil {
        return err2
    }
    if err3 != nil {
        return err3
    }
    // ...
}

// ✅ Good: handle errors inline
func process() error {
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

    return nil
}
```

### Don't Ignore Errors

```go
// ❌ Bad: ignoring error
data, _ := json.Marshal(user)

// ✅ Good: handle or explicitly ignore with comment
data, err := json.Marshal(user)
if err != nil {
    return fmt.Errorf("marshal user: %w", err)
}

// If truly ignorable, document why
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
```

---

## Variable Scope

### Minimize Scope

```go
// ❌ Bad: variable declared far from use
func process(items []Item) error {
    var result []ProcessedItem // Declared at top
    var err error

    // ... 50 lines later ...

    for _, item := range items {
        processed, err := processItem(item)
        // ...
    }
    return nil
}

// ✅ Good: declare close to use
func process(items []Item) error {
    for _, item := range items {
        processed, err := processItem(item)
        if err != nil {
            return err
        }
        // Use processed immediately
    }
    return nil
}
```

### Use Short Variable Names for Short Scopes

```go
// ✅ Good: short name for small scope
for i, u := range users {
    fmt.Printf("%d: %s\n", i, u.Name)
}

// ✅ Good: descriptive name for larger scope
func processUsers(users []User) error {
    validatedUsers := make([]User, 0, len(users))
    for _, user := range users {
        if user.IsValid() {
            validatedUsers = append(validatedUsers, user)
        }
    }
    return saveUsers(validatedUsers)
}
```

---

## Avoiding Complexity

### No Cleverness

```go
// ❌ Bad: clever but unclear
func (u *User) Age() int {
    return int(time.Since(u.BirthDate).Hours() / 24 / 365.25)
}

// ✅ Good: clear and correct
func (u *User) Age() int {
    now := time.Now()
    years := now.Year() - u.BirthDate.Year()

    // Adjust if birthday hasn't occurred this year
    if now.YearDay() < u.BirthDate.YearDay() {
        years--
    }

    return years
}
```

### Avoid Deep Nesting

```go
// ❌ Bad: deeply nested
func process(data Data) error {
    if data.Valid {
        for _, item := range data.Items {
            if item.Active {
                for _, sub := range item.SubItems {
                    if sub.Ready {
                        // Finally do something
                    }
                }
            }
        }
    }
    return nil
}

// ✅ Good: extract and flatten
func process(data Data) error {
    if !data.Valid {
        return nil
    }

    for _, item := range data.Items {
        if err := processItem(item); err != nil {
            return err
        }
    }
    return nil
}

func processItem(item Item) error {
    if !item.Active {
        return nil
    }

    for _, sub := range item.SubItems {
        if err := processSubItem(sub); err != nil {
            return err
        }
    }
    return nil
}
```

---

## Dependency Injection

### Constructor Injection

```go
// ✅ Good: dependencies passed to constructor
type UserService struct {
    db     *sql.DB
    cache  Cache
    logger *slog.Logger
}

func NewUserService(db *sql.DB, cache Cache, logger *slog.Logger) *UserService {
    return &UserService{
        db:     db,
        cache:  cache,
        logger: logger,
    }
}

// ❌ Bad: global dependencies
var globalDB *sql.DB

type UserService struct{}

func (s *UserService) GetUser(id string) (*User, error) {
    return queryUser(globalDB, id) // Hidden dependency
}
```

### Interface for Testing

```go
// Define interface for what you need
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
}

type UserService struct {
    repo UserRepository
}

// In tests, provide mock implementation
type mockRepo struct {
    users map[string]*User
}

func (m *mockRepo) FindByID(ctx context.Context, id string) (*User, error) {
    if user, ok := m.users[id]; ok {
        return user, nil
    }
    return nil, ErrNotFound
}
```

---

## Comments

### Self-Documenting Code

```go
// ❌ Bad: comment explains unclear code
// Check if user can edit
if u.r == 1 && u.s == "a" && !u.d {
    // ...
}

// ✅ Good: code is self-explanatory
if user.IsAdmin() && user.IsActive() && !user.IsDeleted() {
    // ...
}
```

### Document Why, Not What

```go
// ❌ Bad: explains what (obvious from code)
// Increment counter by 1
counter++

// ✅ Good: explains why (not obvious)
// Retry count starts at 1 because the initial attempt counts
retryCount := 1

// ✅ Good: explains business logic
// Users created before 2020 have legacy pricing that doesn't expire
if user.CreatedAt.Before(legacyPricingCutoff) {
    return nil // No expiration check needed
}
```

### Document Public APIs

```go
// GetUser retrieves a user by their unique identifier.
//
// It returns ErrNotFound if no user exists with the given ID.
// The returned User is safe to modify; it's a copy of the stored data.
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    // ...
}
```

---

## Testing Considerations

### Design for Testability

```go
// ✅ Good: easy to test with dependency injection
type OrderService struct {
    users      UserGetter
    inventory  InventoryChecker
    payments   PaymentProcessor
    time       func() time.Time // For testing time-dependent logic
}

func NewOrderService(users UserGetter, inv InventoryChecker, pay PaymentProcessor) *OrderService {
    return &OrderService{
        users:     users,
        inventory: inv,
        payments:  pay,
        time:      time.Now,
    }
}

// ❌ Bad: hard to test with direct dependencies
type OrderService struct{}

func (s *OrderService) Process(orderID string) error {
    user := db.GetUser(orderID)      // Direct DB call
    stock := inventory.Check(orderID) // Direct service call
    time.Now()                        // Can't control time
    // ...
}
```

### Avoid Side Effects in Constructors

```go
// ❌ Bad: constructor has side effects
func NewServer() *Server {
    db, _ := sql.Open("postgres", os.Getenv("DB_URL")) // Side effect
    go startBackgroundJob()                            // Side effect
    return &Server{db: db}
}

// ✅ Good: constructor only creates object
func NewServer(db *sql.DB) *Server {
    return &Server{db: db}
}

// Caller controls lifecycle
func main() {
    db, err := sql.Open("postgres", os.Getenv("DB_URL"))
    if err != nil {
        log.Fatal(err)
    }

    server := NewServer(db)
    go server.StartBackgroundJobs()
    server.Run()
}
```

---

## Concurrency

### Don't Leak Goroutines

```go
// ❌ Bad: goroutine can leak
func process(ctx context.Context) {
    go func() {
        for {
            // Never exits
            doWork()
        }
    }()
}

// ✅ Good: goroutine respects context
func process(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return
            default:
                doWork()
            }
        }
    }()
}
```

### Close Channels From Sender

```go
// ✅ Good: sender closes channel
func produce(ctx context.Context) <-chan int {
    ch := make(chan int)
    go func() {
        defer close(ch) // Sender closes
        for i := 0; ; i++ {
            select {
            case <-ctx.Done():
                return
            case ch <- i:
            }
        }
    }()
    return ch
}
```

---

## Summary

| Principle | Practice |
|-----------|----------|
| Single Responsibility | One function, one job |
| Short Functions | Extract logical units |
| Early Returns | Guard clauses first |
| Handle Errors | Immediately, with context |
| Minimize Scope | Declare close to use |
| No Cleverness | Clear over clever |
| Shallow Nesting | Extract and flatten |
| Dependency Injection | Pass dependencies explicitly |
| Self-Documenting | Clear names over comments |
| Document Why | Not what (obvious from code) |
| Design for Testability | Interfaces, injection |
| Respect Context | Goroutines must exit |

---

*Companion to: style-guide.md, type-patterns.md*
*Last updated: 2026-01-15*
