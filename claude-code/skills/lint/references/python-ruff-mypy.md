# Python: Ruff + mypy

**Status: recommended standard for new work.** Use it for new Python projects, and when adding lint to an existing one.

Ruff lints and formats (replacing Flake8, Black, isort, pyupgrade, autoflake and most plugins); mypy type-checks. Project layout, pytest and coverage configuration belong to the project's Python standards (a `/python` skill where installed).

## Installation

```bash
uv add --dev ruff mypy        # project dev dependencies (recommended)
uvx ruff check .              # one-off run without installing
```

Check current versions before pinning: `uvx ruff --version`, `curl -s https://pypi.org/pypi/mypy/json | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['version'])"`.

## Configuration

Template: `templates/pyproject.toml` (merge its tables into the project's `pyproject.toml`).

```toml
[tool.ruff]
target-version = "py312"   # the project's minimum supported Python
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM", "TC", "S", "RUF"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]   # assert in tests
"__init__.py" = ["F401"]     # re-exports

[tool.ruff.lint.isort]
known-first-party = ["myproject"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.12"      # match target-version
strict = true
warn_unreachable = true
```

`strict = true` already turns on `disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, `warn_unused_ignores`, `no_implicit_reexport`, `strict_equality` and the other strict flags; list extra flags only when they go beyond it.

Per-module relaxations:

```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "library_without_stubs.*"
ignore_missing_imports = true
```

## Rule Sets

| Code | Source | Purpose |
|------|--------|---------|
| `E`, `W` | pycodestyle | Style errors and warnings |
| `F` | pyflakes | Undefined names, unused imports |
| `I` | isort | Import sorting |
| `N` | pep8-naming | Naming |
| `UP` | pyupgrade | Modern syntax for the target version |
| `B` | flake8-bugbear | Likely bugs |
| `C4` | flake8-comprehensions | Comprehension clean-ups |
| `SIM` | flake8-simplify | Simplifications |
| `TC` | flake8-type-checking | Imports only needed for typing go under `TYPE_CHECKING` (formerly `TCH`) |
| `S` | flake8-bandit | Security checks (shell=True, hard-coded secrets, unsafe deserialisation) |
| `RUF` | Ruff | Ruff-specific rules |

Stricter additions for mature codebases: `ARG` (unused arguments), `PTH` (pathlib), `ERA` (commented-out code), `PL` (pylint), `PERF` (performance). Look up any code with `ruff rule <CODE>`.

### Adopting on an Existing Codebase

1. `select = ["E", "F", "I"]`, fix, commit.
2. Add `B`, `UP`, `N`, then `C4`, `SIM`, `TC`, `S`, `RUF`.
3. mypy: start with `check_untyped_defs = true`, then `disallow_untyped_defs = true`, then `strict = true`.

`ruff check --add-noqa .` records existing violations as `# noqa` so new code is held to the full set immediately.

## Commands

```bash
ruff check .            # lint
ruff check . --fix      # lint + auto-fix
ruff format .           # format
ruff format --check .   # format check (CI)
mypy src/               # type check
```

## Pre-commit

With lint-staged (JS tooling present): `"*.py": ["ruff check --fix", "ruff format"]`.

With the pre-commit framework (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.9
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.3.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

Bump the `rev` values with `pre-commit autoupdate`.

## CI Step

```bash
uv sync --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src/
```

## Editor (VS Code)

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  }
}
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Formatting differs from Black | Ruff's formatter is Black-compatible; review `ruff format --diff .` once when migrating |
| Missing stubs in mypy | Install `types-<package>`, or add an override with `ignore_missing_imports = true` |
| Another import sorter in use | Remove it; Ruff's `I` rules replace isort |
| `RUF012` on SQLAlchemy/SQLModel `__table_args__` / `__mapper_args__` | Framework-managed mutable class attributes; add `# noqa: RUF012` on those lines |
