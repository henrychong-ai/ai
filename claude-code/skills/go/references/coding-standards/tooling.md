# Go Tooling Configuration

golangci-lint, gofumpt, editor integration, and development setup.

---

## golangci-lint

### Installation

```bash
# Binary installation (recommended)
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

# Or via go install
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Verify installation
golangci-lint --version
```

### Basic Configuration

**For comprehensive configuration, invoke the `/lint` skill.**

Minimal `.golangci.yml`:

```yaml
run:
  timeout: 5m
  modules-download-mode: readonly

linters:
  disable-all: true
  enable:
    # Default linters
    - errcheck      # Check for unchecked errors
    - gosimple      # Simplify code
    - govet         # Suspicious constructs
    - ineffassign   # Useless assignments
    - staticcheck   # Static analysis
    - unused        # Unused code
    # Recommended additions
    - gofumpt       # Stricter formatting
    - goimports     # Import ordering
    - misspell      # Spelling mistakes
    - unconvert     # Unnecessary type conversions
    - unparam       # Unused function parameters

linters-settings:
  gofumpt:
    extra-rules: true

issues:
  exclude-use-default: false
  max-issues-per-linter: 0
  max-same-issues: 0
```

### Strict Configuration

For stricter projects:

```yaml
run:
  timeout: 5m
  modules-download-mode: readonly

linters:
  disable-all: true
  enable:
    # Error handling
    - errcheck
    - errorlint      # Error wrapping
    - wrapcheck      # Wrap errors from external packages

    # Code quality
    - govet
    - staticcheck
    - gosimple
    - ineffassign
    - unused
    - unconvert
    - unparam

    # Style
    - gofumpt
    - goimports
    - misspell
    - whitespace

    # Complexity
    - gocyclo        # Cyclomatic complexity
    - gocognit       # Cognitive complexity
    - nestif         # Nested if depth

    # Security
    - gosec          # Security issues

    # Performance
    - prealloc       # Slice preallocation

linters-settings:
  gofumpt:
    extra-rules: true

  gocyclo:
    min-complexity: 15

  gocognit:
    min-complexity: 20

  nestif:
    min-complexity: 5

  gosec:
    excludes:
      - G104  # Audit errors not handled

issues:
  exclude-use-default: false
  exclude-rules:
    # Allow long lines in tests
    - path: _test\.go
      linters:
        - lll

    # Allow unused parameters in interface implementations
    - linters:
        - unparam
      text: "always receives"
```

### Running golangci-lint

```bash
# Run all linters
golangci-lint run

# Run on specific paths
golangci-lint run ./internal/...

# Auto-fix issues (where supported)
golangci-lint run --fix

# Show all available linters
golangci-lint linters

# Verbose output
golangci-lint run -v

# Output in specific format
golangci-lint run --out-format=json
golangci-lint run --out-format=github-actions
```

---

## gofumpt

### Installation

```bash
go install mvdan.cc/gofumpt@latest
```

### Usage

```bash
# Format single file
gofumpt -w file.go

# Format all files recursively
gofumpt -w .

# Check without modifying (for CI)
gofumpt -d . | grep -q . && echo "formatting needed" && exit 1
```

### Extra Rules (over gofmt)

gofumpt enforces:
- Consistent grouping of imports (stdlib, third-party, internal)
- No empty lines at start/end of function bodies
- No empty lines around single-statement blocks
- Consistent composite literal formatting

```go
// Before gofumpt
func example() {

    x := map[string]int{
        "a": 1, "b": 2,
    }

}

// After gofumpt
func example() {
    x := map[string]int{
        "a": 1,
        "b": 2,
    }
}
```

---

## Editor Integration

### VS Code

Install the official Go extension, then configure settings:

```json
// .vscode/settings.json
{
  "go.formatTool": "gofumpt",
  "go.lintTool": "golangci-lint",
  "go.lintFlags": ["--fast"],
  "editor.formatOnSave": true,
  "[go]": {
    "editor.defaultFormatter": "golang.go",
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "gopls": {
    "formatting.gofumpt": true
  }
}
```

### JetBrains GoLand

1. **Preferences > Tools > File Watchers**
   - Add gofumpt watcher for formatting on save

2. **Preferences > Tools > External Tools**
   - Add golangci-lint for linting

3. **Preferences > Editor > Code Style > Go**
   - Enable "Use goimports"

### Neovim (with nvim-lspconfig)

```lua
-- init.lua
require('lspconfig').gopls.setup{
  settings = {
    gopls = {
      gofumpt = true,
    },
  },
}

-- Use null-ls for golangci-lint
local null_ls = require("null-ls")
null_ls.setup({
  sources = {
    null_ls.builtins.diagnostics.golangci_lint,
  },
})
```

---

## Pre-commit Hooks

### Using pre-commit framework

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.62.0
    hooks:
      - id: golangci-lint

  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-fmt-goimports
```

### Using Git hooks directly

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Format check
if ! gofumpt -d . | diff -q /dev/null - > /dev/null 2>&1; then
    echo "Error: Code is not formatted. Run 'gofumpt -w .'"
    exit 1
fi

# Lint check
if ! golangci-lint run --timeout 5m; then
    echo "Error: Linting failed"
    exit 1
fi

# Test check
if ! go test -race ./...; then
    echo "Error: Tests failed"
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## CI Configuration

### GitHub Actions

```yaml
# .github/workflows/go.yml
name: Go

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.25'

      - name: Format check
        run: |
          go install mvdan.cc/gofumpt@latest
          if [ -n "$(gofumpt -d .)" ]; then
            echo "Code is not formatted"
            gofumpt -d .
            exit 1
          fi

      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest
          args: --timeout=5m

      - name: Test
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Coverage check
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "Coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage below 80%"
            exit 1
          fi
```

### Bitbucket Pipelines

```yaml
# bitbucket-pipelines.yml
image: golang:1.25

definitions:
  steps:
    - step: &lint
        name: Lint & Format
        caches:
          - go
        script:
          - go install mvdan.cc/gofumpt@latest
          - go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
          - gofumpt -d . | diff -q /dev/null - || (echo "Format check failed" && exit 1)
          - golangci-lint run --timeout 5m

    - step: &test
        name: Test & Coverage
        caches:
          - go
        script:
          - go test -race -coverprofile=coverage.out ./...
          - go tool cover -func=coverage.out

pipelines:
  default:
    - step: *lint
    - step: *test

  pull-requests:
    '**':
      - step: *lint
      - step: *test
```

---

## Makefile Integration

```makefile
.PHONY: fmt lint test coverage build

# Format code
fmt:
	gofumpt -w .

# Run linter
lint:
	golangci-lint run --timeout 5m

# Run tests
test:
	go test -race -v ./...

# Run tests with coverage
coverage:
	go test -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# Check coverage threshold
coverage-check:
	@go test -coverprofile=coverage.out ./... > /dev/null
	@COVERAGE=$$(go tool cover -func=coverage.out | grep total | awk '{print $$3}' | sed 's/%//'); \
	echo "Coverage: $$COVERAGE%"; \
	if [ $$(echo "$$COVERAGE < 80" | bc) -eq 1 ]; then \
		echo "Coverage below 80% threshold"; \
		exit 1; \
	fi

# Build binary
build:
	go build -o bin/app ./cmd/app

# Run all checks
check: fmt lint test coverage-check

# Install dev tools
tools:
	go install mvdan.cc/gofumpt@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
```

---

## Module Configuration

### go.mod

```go
module github.com/username/project

go 1.25

toolchain go1.25.0
```

### .gitignore

```gitignore
# Binaries
/bin/
*.exe
*.dll
*.so
*.dylib

# Test coverage
coverage.out
coverage.html

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Build cache
/vendor/
```

---

## Tool Versions Summary

| Tool | Installation | Version Command |
|------|--------------|-----------------|
| Go | go.dev/dl | `go version` |
| golangci-lint | `go install` | `golangci-lint --version` |
| gofumpt | `go install` | `gofumpt --version` |
| sqlc | `go install` | `sqlc version` |

---

*For detailed linting configuration, invoke the `/lint` skill.*
*Companion to: style-guide.md, go-ironclad-stack.md*
*Last updated: 2026-01-15*
