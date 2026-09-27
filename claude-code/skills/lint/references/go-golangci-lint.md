# Go Linting + Formatting with golangci-lint

golangci-lint is the standard Go linter, aggregating 100+ linters into a single fast tool. It also handles formatting via built-in gofumpt — no standalone gofumpt binary needed.

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

Based on patterns from Google Go projects and community standards:
- [google/osv-scanner](https://github.com/google/osv-scanner) — uses `default: all` approach
- [google/go-github](https://github.com/google/go-github) — most comprehensive Google config
- [prometheus/prometheus](https://github.com/prometheus/prometheus), [etcd-io/etcd](https://github.com/etcd-io/etcd), [open-telemetry/opentelemetry-go](https://github.com/open-telemetry/opentelemetry-go)
- [maratori/golangci-lint-config](https://github.com/maratori/golangci-lint-config)

```yaml
version: "2"

linters:
  # Enable all linters, disable specific ones
  # Same approach as google/osv-scanner
  default: all
  disable:
    - depguard          # Dependency guard — enable per-project with custom deny rules
    - exhaustruct       # Require all struct fields initialized (too strict)
    - ireturn           # Accept interfaces, return concrete (too opinionated)
    - varnamelen        # Variable name length (too strict for idiomatic Go)
    - wrapcheck         # Error wrapping enforcement (handled manually)
    - nlreturn          # Newline before return (style opinion)
    - wsl               # Whitespace linter (style opinion)
    - godox             # TODO/FIXME/BUG comments (noisy during development)
    - err113            # Dynamic errors (too strict, conflicts with fmt.Errorf)
    - testpackage       # Require _test package (blocks white-box testing)
    - paralleltest      # Require t.Parallel (not always appropriate)
    - thelper           # Require t.Helper (too strict)
    - cyclop            # Redundant with gocyclo/gocognit
    - forcetypeassert   # Allow unchecked type assertions (checked by errcheck)
    - tagliatelle       # Struct tag naming convention (too opinionated)
    - nonamedreturns    # Named returns useful for documentation
    - mnd               # Magic number detection (too noisy)
    - funlen            # Function length — use gocognit for complexity instead
    - lll               # Line length — gofumpt handles formatting

formatters:
  enable:
    - gofumpt       # Stricter than gofmt — no standalone install needed
    - goimports

linters-settings:
  gofumpt:
    extra-rules: true

  errcheck:
    check-type-assertions: true
    check-blank: true
    # No exclude-functions needed — the std-error-handling preset already covers:
    # .*Close, .*Flush, os.Remove(All), fmt.Print*, os.(Un)Setenv, stdout/stderr

  gocyclo:
    min-complexity: 15

  gocognit:
    min-complexity: 20

  govet:
    enable-all: true
    disable:
      - fieldalignment  # Disabled in every Google project that customizes govet
    settings:
      shadow:
        strict: true

  revive:
    severity: warning
    rules:
      - name: blank-imports
      - name: context-as-argument
      - name: context-keys-type
      - name: dot-imports
      - name: early-return
      - name: empty-block
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: errorf
      - name: exported
      - name: if-return
      - name: increment-decrement
      - name: indent-error-flow
      - name: package-comments
      - name: range
      - name: receiver-naming
      - name: redefines-builtin-id
      - name: superfluous-else
      - name: time-naming
      - name: unexported-return
      - name: unreachable-code
      - name: unused-parameter
      - name: var-declaration
      - name: var-naming

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

  nakedret:
    max-func-lines: 0   # Disallow naked returns entirely

  staticcheck:
    checks:
      - all
      - -ST1000         # Package comments (handled by revive)
      - -ST1020         # Comment on exported method (too noisy for existing codebases)
      - -ST1021         # Comment on exported type (too noisy for existing codebases)
      - -ST1022         # Comment on exported const (too noisy for existing codebases)
      - -QF1008         # Embedded field selector (style preference)

  nolintlint:
    require-explanation: true
    require-specific: true

exclusions:
  generated: lax
  warn-unused: true
  presets:
    - comments
    - std-error-handling
    - common-false-positives

  rules:
    # Relax checks in test files
    - path: _test\.go
      linters:
        - errcheck
        - gosec
        - goconst
        - dupl
        - noctx

    # Exclude generated files
    - path: \.pb\.go$
      linters:
        - all

    - path: _mock\.go$
      linters:
        - all

    - path: \.gen\.go$
      linters:
        - all

issues:
  max-issues-per-linter: 0
  max-same-issues: 0

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

formatters:
  enable:
    - gofumpt
    - goimports

linters-settings:
  gofumpt:
    extra-rules: true
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
          go-version: '1.26'
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
