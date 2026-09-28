# Go Linting + Formatting with golangci-lint v2

golangci-lint runs Go linters and formatters (gofmt, goimports, gofumpt) from one binary and one `.golangci.yml`. All configuration here targets **golangci-lint v2** (validated against v2.14.0); a v1 binary cannot read it.

## Baseline vs Strict

| Profile | Template | Linters | Formatters | Use |
|---------|----------|---------|------------|-----|
| **Baseline** (default) | `templates/.golangci.yml` | v2 `standard` set: errcheck, govet, ineffassign, staticcheck, unused | gofmt, goimports | Every Go repo. Low-friction default that most codebases pass with few changes. |
| **Strict** (opt-in) | `templates/.golangci.strict.yml` | `default: all` minus a documented disable list | gofumpt, goimports | Deliberate adoption on a new or clean codebase. Expect many findings on existing code; fix them before making CI blocking. |

Copy the chosen template to the module root as `.golangci.yml`, then run `golangci-lint config verify`.

## Installation

Pin an exact v2 release in every install (local, CI, pre-commit) so all environments report the same issues. Releases: <https://github.com/golangci/golangci-lint/releases>.

```bash
# Binary (upstream-recommended): installs the pinned version into $(go env GOPATH)/bin
curl -sSfL https://golangci-lint.run/install.sh | sh -s -- -b $(go env GOPATH)/bin v2.14.0

# macOS
brew install golangci-lint

# Verify
golangci-lint version
```

Source installs use the **v2 module path**: `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.14.0`. The old path without `/v2` installs v1. Upstream does not guarantee `go install`, `go get -tool` / `go tool`, or the "tools pattern" (results depend on the local Go version and untested dependency versions) and recommends the binary install.

## Configuration

### Setup Check

```bash
golangci-lint config verify          # validates .golangci.yml against the v2 schema
golangci-lint linters                # shows which linters and formatters are enabled
```

### Baseline (`templates/.golangci.yml`)

```yaml
version: "2"

linters:
  default: standard            # errcheck, govet, ineffassign, staticcheck, unused
  settings:
    errcheck:
      exclude-functions: []    # add repo-specific closers only if the preset misses them
  exclusions:
    generated: lax
    warn-unused: true
    presets:
      - comments
      - std-error-handling     # .Close, .Flush, os.Remove(All), fmt.Print*, os.(Un)Setenv, ...
      - common-false-positives

formatters:
  enable:
    - gofmt
    - goimports
  exclusions:
    generated: lax

issues:
  max-issues-per-linter: 0
  max-same-issues: 0

output:
  formats:
    text:
      path: stdout
  sort-order:
    - linter
    - file
```

### Strict (`templates/.golangci.strict.yml`)

Starts from `linters.default: all` and disables linters that are too noisy or opinionated for general use (including `wsl`, its successor `wsl_v5`, and the deprecated `gomodguard`). It configures errcheck, govet (all analysers except fieldalignment, strict shadow), revive, gosec, gocritic, nakedret, staticcheck and nolintlint, and uses gofumpt (`extra.group-params`, which replaces the deprecated `extra-rules`). The pattern follows `default: all` configs from google/osv-scanner, google/go-github, prometheus and etcd. Read the template for the full list with a reason per entry.

### v2 Layout (common mistakes)

| v1 / wrong | v2 |
|------------|-----|
| top-level `linters-settings:` | `linters.settings:` |
| top-level `exclusions:` or `issues.exclude-rules` | `linters.exclusions:` (`rules`, `paths`, `presets`, `generated`) |
| `enable-all` / `disable-all` | `linters.default: all \| standard \| fast \| none` |
| gofmt/goimports/gofumpt under `linters.enable` | `formatters.enable` (settings under `formatters.settings`) |
| `output.formats: - format: colored-line-number` | `output.formats: { text: { path: stdout } }` (map form) |
| `output.sort-results` | removed; `output.sort-order` only |
| `run.skip-dirs` | `linters.exclusions.paths` |
| `gosimple`, `stylecheck` linters | merged into `staticcheck` |

### Migrating a v1 Config

Some repos still pin golangci-lint v1 (for example as a Go `tool` dependency). To move them to v2:

```bash
golangci-lint migrate                # rewrites .golangci.yml to the v2 layout (keeps a backup)
golangci-lint config verify
```

Then install a pinned v2 binary, and drop the v1 `tool` directive from `go.mod` (`go get -tool github.com/golangci/golangci-lint/cmd/golangci-lint@none`) if the repo used one.

## Commands

```bash
golangci-lint run ./...              # lint + formatter checks
golangci-lint run --fix ./...        # apply linter fixes and formatting
golangci-lint fmt ./...              # format only (enabled formatters)
golangci-lint run --fast-only ./...  # only linters marked fast (v2 flag; v1's --fast is gone)
golangci-lint run -v ./...           # verbose
golangci-lint linters                # enabled/disabled linters
golangci-lint config verify          # validate config
golangci-lint migrate                # convert a v1 config to v2
```

## Key Linters

### Baseline (`standard`)
| Linter | Purpose |
|--------|---------|
| `errcheck` | Unchecked errors |
| `govet` | Suspicious constructs (`go vet`) |
| `ineffassign` | Ineffective assignments |
| `staticcheck` | Static analysis, including the former gosimple and stylecheck checks |
| `unused` | Unused code |

### Common Additions (enabled by the strict profile)
| Linter | Purpose |
|--------|---------|
| `gosec` | Security issues |
| `gocritic` | Opinionated checks |
| `revive` | Configurable style rules |
| `gocognit` / `gocyclo` | Complexity |
| `bodyclose` / `noctx` | HTTP response body close, requests without context |
| `misspell` | Spelling mistakes |

To add a few linters to the baseline instead of switching profile, keep `default: standard` and list them under `linters.enable`.

## Makefile Integration

```makefile
.PHONY: lint lint-fix

lint:
	golangci-lint run ./...

lint-fix:
	golangci-lint run --fix ./...
```

## CI/CD Integration

Pin the golangci-lint version and take the Go version from `go.mod`.

### GitHub Actions
```yaml
name: Lint
on: [push, pull_request]

jobs:
  golangci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-go@v7
        with:
          go-version-file: go.mod
      - uses: golangci/golangci-lint-action@v9   # v7+ supports golangci-lint v2 only
        with:
          version: v2.14
```

### Bitbucket Pipelines
```yaml
- step:
    name: Lint Go
    image: golang:1.27   # match the go directive in go.mod (1.25 and older are end of life)
    script:
      - curl -sSfL https://golangci-lint.run/install.sh | sh -s -- -b $(go env GOPATH)/bin v2.14.0
      - golangci-lint run ./...
```

A runner that already provides a pinned golangci-lint binary on `PATH` can skip the install line.

## Pre-commit Hook

golangci-lint lints **packages, not file lists**, so hooks run it on `./...` rather than on the staged file names.

### lint-staged
```js
'*.go': () => 'golangci-lint run --fix ./...',
```

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/golangci/golangci-lint
    rev: v2.14.0
    hooks:
      - id: golangci-lint-full        # golangci-lint run --fix
      - id: golangci-lint-config-verify
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `can't load config` / "additional properties … not allowed" | v1 layout: run `golangci-lint migrate`, then `config verify` |
| `unknown flag: --fast` | v2 renamed it to `--fast-only` |
| Formatter findings after `gofmt -w` | Formatting is owned by golangci-lint's formatters (gofumpt in strict); run `golangci-lint fmt` or `run --fix`, not a separate gofmt |
| Warnings about unmatched exclusion rules | `linters.exclusions.warn-unused: true` reports stale rules; remove them or set it to `false` for generic rules |
| Slow first run | Normal (cold cache); set `run.timeout` only if CI needs a hard cap |
| Generated files flagged | Keep `exclusions.generated: lax`; add `linters.exclusions.paths` / `formatters.exclusions.paths` for generated files without a "Code generated" header |

## Editor Integration

### VS Code (Go extension)
```json
{
  "go.lintTool": "golangci-lint-v2",
  "go.lintOnSave": "package"
}
```

Use `"go.lintFlags": ["--fast-only"]` for faster on-save feedback.

### GoLand
Settings → Tools → Go Linter → golangci-lint
