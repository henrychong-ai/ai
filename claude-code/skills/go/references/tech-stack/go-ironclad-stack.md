# The Ironclad Stack: Universal Go for Claude Code

A single, production-ready Go stack optimized for AI-assisted development. Designed for compile-time safety, maximum Claude Code proficiency, and universal compatibility across all project types.

**Core Principle:** *One source of truth, compile-time validation, one set of tools.*

---

## Design Principles

### 1. Claude Code Optimization
Every technology choice prioritizes Claude's training data coverage. We use tools with the most documentation, examples, and community adoption to minimize hallucinations and maximize accurate code generation.

### 2. Compile-Time Safety
sqlc validates SQL at compile time. golangci-lint catches errors before runtime. Strong typing with interfaces prevents entire categories of bugs. Errors are caught by the compiler, not at 3am in production.

### 3. Universal Compatibility
The same core stack works for all project types: APIs, CLI tools, microservices, and background workers. Framework choices are minimal; tooling stays consistent.

### 4. Multi-Developer + Multi-CC Stability
Pre-commit hooks enforce standards automatically. golangci-lint catches errors before code review. Consistent tooling means any developer or CC instance can work on any project.

---

## The Universal Core Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Language** | Go 1.25+ | Compile-time safety + maximum CC training data |
| **Minimum Version** | Go 1.24+ | Security baseline |
| **Web Framework** | Gin | Maximum training data, battle-tested, fast |
| **Database** | sqlc | SQL-first, compile-time type generation |
| **Validation** | go-playground/validator | Struct tag validation, reflection-based |
| **CLI** | Cobra + Viper | Industry standard, composable |
| **Linting** | golangci-lint | Meta-linter, 50+ linters |
| **Formatting** | gofumpt | Stricter than gofmt |
| **Testing** | go test + testify | Standard runner + better assertions |
| **Microservices** | gRPC + protobuf | Type-safe RPC, code generation |
| **Migrations** | golang-migrate | SQL-based migrations |

---

## Go Version Policy

### Version Requirements

| Context | Version | Rationale |
|---------|---------|-----------|
| **New projects** | Go 1.25+ | Latest stable with all features |
| **Minimum supported** | Go 1.24+ | Security baseline, generics stable |

### Current Support Schedule

Go maintains support for the **two most recent major versions**. Unlike Node.js, Go has no formal LTS designation.

| Version | Released | Status |
|---------|----------|--------|
| **1.25** | Aug 2025 | Current (Recommended) |
| **1.24** | Feb 2025 | Supported |
| **1.23** | Aug 2024 | End of Life |

### Why Go 1.24+ Minimum

1. **Generics stability**: Generic types and functions are mature
2. **Range over functions**: Enables cleaner iterator patterns
3. **Security patches**: All critical fixes included
4. **toolchain directive**: Automatic version management in go.mod

### Version Pinning

**go.mod (recommended):**
```go
module github.com/username/project

go 1.25

toolchain go1.25.0
```

The `toolchain` directive ensures consistent Go versions across all developers.

---

## Component Breakdown

### Gin (Web Framework)

**Role:** HTTP framework for APIs

**Why:**
- Maximum Claude training data (most popular Go web framework)
- Fast performance (httprouter-based)
- Middleware support
- JSON binding and validation
- Battle-tested in production

```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"id": id})
    })

    r.Run(":8080")
}
```

**Why not alternatives?**
| Framework | Issue |
|-----------|-------|
| Echo | Less training data |
| Chi | Router-only, less batteries |
| Fiber | fasthttp-based, compatibility issues |
| net/http | Too low-level for most projects |

---

### sqlc (Database)

**Role:** SQL-first database access

**Why:**
- Write SQL, get type-safe Go
- Compile-time query validation
- No ORM magic or runtime reflection
- AI-generated SQL errors caught at build time
- You see exactly what SQL executes

```sql
-- queries.sql
-- name: GetUser :one
SELECT id, name, email FROM users WHERE id = $1;

-- name: CreateUser :one
INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *;
```

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "queries.sql"
    schema: "schema.sql"
    gen:
      go:
        package: "db"
        out: "db"
```

```bash
sqlc generate
```

**Generated Go (db/queries.sql.go):**
```go
func (q *Queries) GetUser(ctx context.Context, id int32) (User, error) {
    row := q.db.QueryRowContext(ctx, getUserSQL, id)
    var i User
    err := row.Scan(&i.ID, &i.Name, &i.Email)
    return i, err
}
```

**Why not GORM?**
| Aspect | sqlc | GORM |
|--------|------|------|
| Error detection | Compile-time | Runtime |
| SQL visibility | Full (you write it) | Hidden |
| AI hallucination | Caught at build | Caught at runtime |
| Performance | Optimal (no reflection) | Slower (reflection) |
| Learning curve | SQL knowledge required | Easier initially |

---

### golangci-lint (Linting)

**Role:** Meta-linter aggregating 50+ linters

**Why:**
- One tool, all linters
- Consistent configuration
- Fast parallel execution
- IDE integration

**For complete configuration, use the `/lint` skill.**

Basic `.golangci.yml`:
```yaml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - typecheck
    - gofumpt
    - goimports
    - misspell
    - unconvert
    - unparam

linters-settings:
  gofumpt:
    extra-rules: true

run:
  timeout: 5m
```

```bash
golangci-lint run
golangci-lint run --fix  # Auto-fix issues
```

---

### gofumpt (Formatting)

**Role:** Stricter gofmt

**Why:**
- All gofmt rules plus additional consistency
- No configuration needed
- Deterministic output
- Editor integration

```bash
gofumpt -w .  # Format all files
```

**Additional rules over gofmt:**
- Consistent grouping of imports
- No empty lines at start/end of blocks
- Consistent spacing in composite literals

---

### go test + testify (Testing)

**Role:** Testing framework

**Why go test:**
- Built into Go toolchain
- Parallel execution
- Benchmarking support
- Coverage reporting

**Why testify:**
- Better assertions than standard library
- Suite support for setup/teardown
- Mock generation

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestCreateUser(t *testing.T) {
    // Arrange
    input := CreateUserInput{Name: "Alice", Email: "alice@example.com"}

    // Act
    user, err := CreateUser(input)

    // Assert
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    assert.NotEmpty(t, user.ID)
}
```

**Coverage requirements:** 80% minimum (enforced in CI)

---

### Cobra + Viper (CLI)

**Role:** CLI framework and configuration

**Why Cobra:**
- Industry standard (used by Docker, Kubernetes, Hugo)
- Subcommand support
- Flag parsing
- Help generation
- Shell completion

**Why Viper:**
- Configuration from files, env vars, flags
- Multiple format support (YAML, JSON, TOML)
- Live watching

```go
var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "My application",
    Run: func(cmd *cobra.Command, args []string) {
        // Main logic
    },
}

func init() {
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file")
    viper.BindPFlag("config", rootCmd.PersistentFlags().Lookup("config"))
}
```

---

### go-playground/validator (Validation)

**Role:** Struct validation

**Why:**
- Struct tag based
- Extensive built-in validators
- Custom validators support
- Gin integration

```go
type CreateUserInput struct {
    Name  string `json:"name" validate:"required,min=1,max=100"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age" validate:"gte=0,lte=150"`
}

var validate = validator.New()

func validateInput(input *CreateUserInput) error {
    return validate.Struct(input)
}
```

---

### gRPC (Microservices)

**Role:** Type-safe RPC framework

**Why:**
- Protocol Buffers for schema
- Code generation for client/server
- Streaming support
- High performance

```protobuf
// user.proto
syntax = "proto3";
package user;
option go_package = "github.com/username/project/pb";

service UserService {
    rpc GetUser(GetUserRequest) returns (User);
    rpc CreateUser(CreateUserRequest) returns (User);
}

message User {
    string id = 1;
    string name = 2;
    string email = 3;
}
```

```bash
protoc --go_out=. --go-grpc_out=. user.proto
```

---

## Project-Type Configurations

### API / Microservice

| Layer | Technology |
|-------|------------|
| Framework | Gin |
| Database | sqlc + PostgreSQL |
| Validation | go-playground/validator |
| Config | Viper |

**Quick start:**
```bash
mkdir my-api && cd my-api
go mod init github.com/username/my-api
go get github.com/gin-gonic/gin
go get github.com/lib/pq
go get github.com/spf13/viper
go get github.com/stretchr/testify
# Install sqlc: go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
```

---

### CLI Tool

| Layer | Technology |
|-------|------------|
| Framework | Cobra + Viper |
| Build | go build |

**Quick start:**
```bash
mkdir my-cli && cd my-cli
go mod init github.com/username/my-cli
go get github.com/spf13/cobra
go get github.com/spf13/viper
go get github.com/stretchr/testify
```

---

### gRPC Microservice

| Layer | Technology |
|-------|------------|
| Framework | gRPC |
| Database | sqlc |
| Validation | Protocol Buffers |

**Quick start:**
```bash
mkdir my-service && cd my-service
go mod init github.com/username/my-service
go get google.golang.org/grpc
go get google.golang.org/protobuf
go get github.com/stretchr/testify
```

---

### Background Worker

| Layer | Technology |
|-------|------------|
| Queue | Redis / NATS |
| Config | Viper |
| Graceful shutdown | context + signal handling |

---

## Decision Tree

```
What are you building?
│
├─► HTTP API?
│   └─► Gin + sqlc + PostgreSQL
│
├─► gRPC Microservice?
│   └─► gRPC + protobuf + sqlc
│
├─► CLI Tool?
│   └─► Cobra + Viper
│
├─► Background Worker?
│   └─► Viper + context + signal handling
│
└─► Library/Package?
    └─► Pure Go, minimal dependencies
```

---

## Standard Project Structure

```
project/
├── cmd/
│   └── server/
│       └── main.go          # Entry point
├── internal/
│   ├── api/
│   │   ├── handlers/        # HTTP handlers
│   │   ├── middleware/      # Middleware
│   │   └── routes.go        # Route definitions
│   ├── db/
│   │   ├── queries.sql      # SQL queries (sqlc)
│   │   ├── schema.sql       # Database schema
│   │   └── db.go            # Generated by sqlc
│   ├── domain/
│   │   └── user.go          # Domain types
│   └── service/
│       └── user.go          # Business logic
├── pkg/                     # Public packages (if any)
├── go.mod
├── go.sum
├── sqlc.yaml
├── .golangci.yml
└── Makefile
```

---

## Makefile Template

```makefile
.PHONY: build test lint fmt run generate

build:
	go build -o bin/server ./cmd/server

test:
	go test -v -race -cover ./...

test-coverage:
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

lint:
	golangci-lint run

fmt:
	gofumpt -w .

run:
	go run ./cmd/server

generate:
	sqlc generate

all: fmt lint test build
```

---

## Dependencies Summary

**New Project Dependencies:**

```bash
# Core
go get github.com/gin-gonic/gin
go get github.com/go-playground/validator/v10

# Database
go get github.com/lib/pq                    # PostgreSQL driver
# sqlc installed separately: go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest

# CLI (if needed)
go get github.com/spf13/cobra
go get github.com/spf13/viper

# gRPC (if needed)
go get google.golang.org/grpc
go get google.golang.org/protobuf

# Testing
go get github.com/stretchr/testify

# Linting (install globally)
# go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
# go install mvdan.cc/gofumpt@latest
```

---

## Summary

### The Ironclad Stack

```
Language:           Go 1.25+ (minimum 1.24+)
Web Framework:      Gin
Database:           sqlc + PostgreSQL
Validation:         go-playground/validator
CLI:                Cobra + Viper
Microservices:      gRPC + protobuf
Linting:            golangci-lint
Formatting:         gofumpt
Testing:            go test + testify
Coverage:           80% minimum
```

### Key Properties

- **Claude Code optimized:** Maximum training data coverage
- **Compile-time safe:** sqlc catches SQL errors, golangci-lint catches code issues
- **Universal:** Works for APIs, CLIs, microservices, workers
- **Enforced:** Pre-commit hooks prevent violations
- **Single tool per category:** No alternatives, no decisions to make

### Companion Documents

| Document | Purpose |
|----------|---------|
| `go-ironclad-infra.md` | Deployment and infrastructure guide |
| `../coding-standards/tooling.md` | golangci-lint configuration |

---

*Last updated: 2026-01-15*
