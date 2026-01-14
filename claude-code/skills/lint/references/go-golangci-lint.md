# Go Linting with golangci-lint

golangci-lint is the standard Go linter, aggregating 100+ linters into a single fast tool.

## Installation

### macOS
```bash
brew install golangci-lint
```

### Go Install
```bash
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

### Binary Download
```bash
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin
```

## Configuration

### golangci-lint v2 (2025+)

**Note:** v2 introduced breaking changes. Use `golangci-lint migrate` to convert v1 configs.

### Strict Configuration (.golangci.yml)
```yaml
version: "2"

linters:
  # Enable all linters, disable specific ones
  default: all
  disable:
    - depguard          # Dependency guard (project-specific)
    - exhaustruct       # Require all struct fields (too strict)
    - ireturn           # Accept interfaces, return concrete (opinion)
    - varnamelen        # Variable name length (too strict)
    - wrapcheck         # Wrap errors (handled manually)
    - nlreturn          # Newline before return (style opinion)
    - wsl               # Whitespace linter (style opinion)

formatters:
  enable:
    - gofmt
    - goimports

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true
    exclude-functions:
      - io.Copy
      - io.WriterTo.WriteTo

  gocyclo:
    min-complexity: 15

  gocognit:
    min-complexity: 20

  govet:
    enable-all: true
    disable:
      - fieldalignment  # Too strict for most projects

  revive:
    severity: warning
    rules:
      - name: blank-imports
      - name: context-as-argument
      - name: context-keys-type
      - name: dot-imports
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: exported
      - name: if-return
      - name: increment-decrement
      - name: var-naming
      - name: var-declaration
      - name: package-comments
      - name: range
      - name: receiver-naming
      - name: time-naming
      - name: unexported-return
      - name: indent-error-flow
      - name: errorf

  gosec:
    severity: medium
    confidence: medium

  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
      - experimental
      - opinionated

  staticcheck:
    checks: ["all"]

exclusions:
  warn-unused: true
  presets:
    - comments
    - std-error-handling
    - common-false-positives

  rules:
    # Exclude test files from certain checks
    - path: _test\.go
      linters:
        - errcheck
        - gosec
        - goconst

    # Exclude generated files
    - path: \.pb\.go$
      linters:
        - all

    - path: _mock\.go$
      linters:
        - all

output:
  formats:
    - format: colored-line-number
  sort-results: true
  sort-order:
    - linter
    - file
```

### Minimal Configuration (Quick Start)
```yaml
version: "2"

linters:
  default: standard
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports

formatters:
  enable:
    - gofmt
    - goimports
```

## Commands

```bash
# Basic lint
golangci-lint run

# Lint with auto-fix
golangci-lint run --fix

# Lint specific packages
golangci-lint run ./pkg/...

# Fast mode (subset of linters)
golangci-lint run --fast

# Show all enabled linters
golangci-lint linters

# Verbose output
golangci-lint run -v

# Generate config
golangci-lint config

# Migrate v1 to v2
golangci-lint migrate
```

## Key Linters

### Must-Have
| Linter | Purpose |
|--------|---------|
| `staticcheck` | Advanced static analysis |
| `govet` | Go vet checks |
| `errcheck` | Unchecked errors |
| `gosimple` | Code simplification |
| `ineffassign` | Ineffective assignments |
| `unused` | Unused code |

### Recommended
| Linter | Purpose |
|--------|---------|
| `gosec` | Security issues |
| `gocyclo` | Cyclomatic complexity |
| `gocritic` | Opinionated checks |
| `revive` | Fast, configurable linter |
| `misspell` | Spelling mistakes |
| `prealloc` | Slice preallocation |

### Strict Additions
| Linter | Purpose |
|--------|---------|
| `gocognit` | Cognitive complexity |
| `dupl` | Code duplication |
| `goconst` | Repeated strings |
| `noctx` | HTTP requests without context |
| `bodyclose` | HTTP response body close |

## Makefile Integration

```makefile
.PHONY: lint lint-fix

lint:
	golangci-lint run

lint-fix:
	golangci-lint run --fix

lint-verbose:
	golangci-lint run -v --timeout=5m
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Lint
on: [push, pull_request]

jobs:
  golangci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - name: golangci-lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest
          args: --timeout=5m
```

### GitLab CI
```yaml
lint:
  image: golangci/golangci-lint:latest
  script:
    - golangci-lint run --timeout=5m
```

## Pre-commit Hook

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.62.0
    hooks:
      - id: golangci-lint
```

### Manual Hook (.git/hooks/pre-commit)
```bash
#!/bin/sh
golangci-lint run --fix
```

## Troubleshooting

### Slow Performance
```yaml
# Reduce timeout
run:
  timeout: 5m

# Use fast preset
linters:
  default: fast
```

### Too Many False Positives
```yaml
exclusions:
  presets:
    - comments
    - std-error-handling
    - common-false-positives
```

### Memory Issues
```bash
# Increase memory limit
GOGC=100 golangci-lint run
```

### Specific File Exclusions
```yaml
exclusions:
  rules:
    - path: ".*_test\\.go"
      linters:
        - errcheck
    - path: "generated/"
      linters:
        - all
```

## Editor Integration

### VSCode settings.json
```json
{
  "go.lintTool": "golangci-lint",
  "go.lintFlags": ["--fast"],
  "go.lintOnSave": "package"
}
```

### GoLand
Settings → Tools → Go Linter → golangci-lint

## Migration from v1 to v2

```bash
# Automatic migration
golangci-lint migrate

# Key changes:
# - enable-all/disable-all → linters.default: all/none/standard/fast
# - run.skip-dirs → exclusions.paths
# - issues.exclude-rules → exclusions.rules
```
