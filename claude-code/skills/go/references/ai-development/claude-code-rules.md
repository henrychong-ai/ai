# Claude Code Rules for Go Development

Conventions and guidelines for Claude Code when working on Go projects.

---

## Code Generation Principles

### Default Behaviors

When generating Go code, Claude Code should:

1. **Follow Go idioms** - Use idiomatic Go patterns from this skill
2. **Prefer simplicity** - Avoid over-engineering; Go values simplicity
3. **Handle errors** - Always handle errors, wrap with context
4. **Use interfaces** - Accept interfaces, return concrete types
5. **Apply composition** - Favor composition over inheritance

### File Organization

```go
// Order within a file:
// 1. Package declaration
// 2. Imports (grouped: stdlib, third-party, internal)
// 3. Constants
// 4. Package-level variables (minimize)
// 5. Types (structs, interfaces)
// 6. Constructor functions (New*)
// 7. Methods (grouped by receiver)
// 8. Functions
```

---

## Ironclad Stack Enforcement

### Technology Selection

| Category | Required Tool | Alternatives |
|----------|---------------|--------------|
| Web Framework | Gin | None |
| Database | sqlc + PostgreSQL | None |
| Validation | go-playground/validator | None |
| CLI | Cobra + Viper | None |
| Linting | golangci-lint | None |
| Formatting | gofumpt | None |
| Testing | go test + testify | None |
| Microservices | gRPC | None |

### When User Asks for Alternatives

If user requests GORM, Echo, Chi, or other alternatives:

1. **Acknowledge request**
2. **Explain Ironclad Stack rationale** - Single source of truth, maximum training data coverage
3. **Offer to proceed with Ironclad choice** or respect explicit override

---

## Error Handling Rules

### Always Wrap Errors

```go
// ✅ Correct
if err != nil {
    return fmt.Errorf("get user %s: %w", userID, err)
}

// ❌ Incorrect
if err != nil {
    return err
}
```

### Use Sentinel Errors

```go
// Define at package level
var ErrNotFound = errors.New("not found")

// Check with errors.Is
if errors.Is(err, ErrNotFound) {
    // handle
}
```

---

## Linting Integration

### Reference /lint Skill

For detailed golangci-lint configuration, invoke the **`/lint` skill**.

The Go skill references `/lint` for:
- Complete `.golangci.yml` configuration
- IDE integration setup
- Pre-commit hook configuration

### Minimum Linters

Always enable these linters:
- `errcheck` - Unchecked errors
- `govet` - Suspicious constructs
- `staticcheck` - Static analysis
- `unused` - Unused code
- `gofumpt` - Formatting
- `goimports` - Import ordering

---

## Testing Conventions

### Default Test Structure

```go
func TestFunctionName(t *testing.T) {
    tests := []struct {
        name    string
        input   InputType
        want    OutputType
        wantErr bool
    }{
        // test cases
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Arrange, Act, Assert
        })
    }
}
```

### Coverage Requirements

- **Minimum**: 80%
- **Business logic**: 90%
- **Run with race detector**: `-race`

---

## Project Structure

### Standard Layout

```
project/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── api/
│   │   ├── handlers/
│   │   ├── middleware/
│   │   └── routes.go
│   ├── db/
│   │   ├── queries.sql
│   │   ├── schema.sql
│   │   └── db.go (generated)
│   ├── domain/
│   └── service/
├── go.mod
├── go.sum
├── sqlc.yaml
├── .golangci.yml
└── Makefile
```

### Package Guidelines

- `cmd/` - Entry points only, minimal code
- `internal/` - Private packages
- `pkg/` - Public packages (rare)
- Avoid `util/`, `common/`, `helper/`

---

## Concurrency Guidelines

### Context Propagation

```go
// Always accept and pass context
func (s *Service) Process(ctx context.Context, data Data) error {
    // Pass to downstream calls
    result, err := s.repo.Get(ctx, data.ID)
    if err != nil {
        return err
    }

    // Check cancellation before expensive work
    if ctx.Err() != nil {
        return ctx.Err()
    }

    return s.processResult(ctx, result)
}
```

### Goroutine Lifecycle

```go
// Always ensure goroutines can exit
go func() {
    for {
        select {
        case <-ctx.Done():
            return // REQUIRED exit path
        default:
            doWork()
        }
    }
}()
```

---

## Security Checklist

When generating API code:

- [ ] Use parameterized queries (sqlc handles this)
- [ ] Validate all input with binding tags
- [ ] Hash passwords with bcrypt (cost ≥ 12)
- [ ] Use short-lived JWTs
- [ ] Implement rate limiting
- [ ] Add security headers

---

## Code Review Checklist

Before presenting generated code:

### Correctness
- [ ] Compiles without errors
- [ ] Handles all error paths
- [ ] Uses context for cancellation
- [ ] Respects interface contracts

### Style
- [ ] Follows Go naming conventions
- [ ] Uses gofumpt formatting
- [ ] Imports properly grouped
- [ ] Comments explain "why" not "what"

### Testing
- [ ] Tests are table-driven
- [ ] Error cases covered
- [ ] Mocks use testify
- [ ] Coverage meets threshold

---

## Command Reference

### Development Commands

```bash
# Format code
gofumpt -w .

# Lint code
golangci-lint run

# Run tests
go test -race -cover ./...

# Generate sqlc
sqlc generate

# Generate mocks
mockery --name=InterfaceName
```

### Build Commands

```bash
# Build binary
go build -o bin/server ./cmd/server

# Build with optimizations
CGO_ENABLED=0 go build -ldflags="-w -s" -o bin/server ./cmd/server
```

---

## Makefile Template

```makefile
.PHONY: build test lint fmt generate

build:
	go build -o bin/server ./cmd/server

test:
	go test -race -cover ./...

lint:
	golangci-lint run

fmt:
	gofumpt -w .

generate:
	sqlc generate

all: fmt lint test build
```

---

## Cross-References

| Topic | Reference |
|-------|-----------|
| Tech stack details | `tech-stack/go-ironclad-stack.md` |
| Infrastructure | `tech-stack/go-ironclad-infra.md` |
| Style guide | `coding-standards/style-guide.md` |
| Type patterns | `coding-standards/type-patterns.md` |
| Error handling | `patterns/error-handling.md` |
| Concurrency | `patterns/concurrency-patterns.md` |
| API patterns | `patterns/api-patterns.md` |
| Security | `patterns/security-patterns.md` |
| Testing | `testing/` directory |
| Linting | `/lint` skill |

---

*Last updated: 2026-01-15*
