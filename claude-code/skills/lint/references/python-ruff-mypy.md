# Python Linting with Ruff + mypy

Modern Python linting stack: Ruff (linting + formatting) + mypy (type checking).

## Why Ruff?

- **Speed**: 10-100x faster than Flake8, Black, isort combined
- **All-in-one**: Replaces Flake8, Black, isort, pydocstyle, pyupgrade, autoflake
- **Rust-based**: Written in Rust for maximum performance
- **Compatible**: Drop-in replacement for existing tools

## Installation

### With uv (Recommended)
```bash
uv add --dev ruff mypy
```

### With pip
```bash
pip install ruff mypy
```

### With pipx (Global)
```bash
pipx install ruff
pipx install mypy
```

## Configuration (pyproject.toml)

### Standard Strict Config
```toml
[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "RUF",   # Ruff-specific rules
    "ARG",   # flake8-unused-arguments
    "PTH",   # flake8-use-pathlib
    "ERA",   # eradicate (commented code)
    "PL",    # pylint
    "PERF",  # perflint
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "PLR0913",  # too many arguments
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests
"__init__.py" = ["F401"]    # Allow unused imports in __init__

[tool.ruff.lint.isort]
known-first-party = ["myproject"]
force-single-line = true

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

### mypy Strict Config
```toml
[tool.mypy]
python_version = "3.11"
strict = true

# Additional strictness beyond strict=true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
no_implicit_reexport = true
strict_equality = true
extra_checks = true

# Per-module overrides
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party.*"
ignore_missing_imports = true
```

## Commands

### Ruff
```bash
# Linting
ruff check .                    # Check for errors
ruff check . --fix              # Auto-fix errors
ruff check . --watch            # Watch mode
ruff check . --select=ALL       # Enable all rules

# Formatting
ruff format .                   # Format all files
ruff format --check .           # Check formatting
ruff format --diff .            # Show formatting diff
```

### mypy
```bash
mypy .                          # Type check
mypy src/                       # Check specific directory
mypy --strict .                 # Maximum strictness
mypy --show-error-codes .       # Show error codes
mypy --install-types .          # Install missing stubs
```

## Package.json Scripts (for monorepos)

If using package.json in a monorepo:
```json
{
  "scripts": {
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check . --fix",
    "format:py": "ruff format .",
    "typecheck:py": "mypy .",
    "check:py": "ruff check . && ruff format --check . && mypy ."
  }
}
```

## Pre-commit Integration

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-PyYAML
```

## Rule Categories

### Essential Rules (Always Enable)
| Code | Name | Purpose |
|------|------|---------|
| `E` | pycodestyle | PEP 8 style errors |
| `F` | pyflakes | Logical errors, undefined names |
| `I` | isort | Import sorting |
| `B` | bugbear | Common bugs and design issues |
| `UP` | pyupgrade | Modernize syntax |

### Recommended Additions
| Code | Name | Purpose |
|------|------|---------|
| `N` | pep8-naming | Naming conventions |
| `C4` | comprehensions | List/dict comprehension improvements |
| `SIM` | simplify | Code simplification |
| `TCH` | type-checking | TYPE_CHECKING imports |
| `RUF` | ruff | Ruff-specific rules |

### Strict Additions
| Code | Name | Purpose |
|------|------|---------|
| `ARG` | unused-arguments | Unused function arguments |
| `PTH` | use-pathlib | Prefer pathlib over os.path |
| `ERA` | eradicate | Remove commented-out code |
| `PL` | pylint | Pylint rules |
| `PERF` | perflint | Performance anti-patterns |

## Gradual Adoption

### For Existing Codebases

Start with minimal rules, expand gradually:

```toml
# Phase 1: Basic
[tool.ruff.lint]
select = ["E", "F", "I"]

# Phase 2: Add quality rules
select = ["E", "F", "I", "B", "UP", "N"]

# Phase 3: Full strictness
select = ["E", "F", "I", "B", "UP", "N", "C4", "SIM", "TCH", "RUF", "ARG", "PTH"]
```

### mypy Gradual Strictness

```toml
# Phase 1: Basic type checking
[tool.mypy]
python_version = "3.11"
check_untyped_defs = true

# Phase 2: Stricter
strict = false
disallow_untyped_defs = true
warn_return_any = true

# Phase 3: Maximum strictness
strict = true
```

## Editor Integration

### VSCode settings.json
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  "ruff.lint.args": ["--config=pyproject.toml"],
  "mypy.runUsingActiveInterpreter": true
}
```

## Troubleshooting

### Ruff vs Black Conflicts
Ruff formatter is 99.9% compatible with Black. If migrating:
```bash
# Verify no differences
ruff format --diff . | head -100
```

### mypy Missing Stubs
```bash
mypy --install-types .
# Or add to pyproject.toml
[[tool.mypy.overrides]]
module = "library_without_stubs.*"
ignore_missing_imports = true
```

### Import Sorting Conflicts
If using other import sorters, disable Ruff's:
```toml
[tool.ruff.lint]
select = ["E", "F", "B"]  # No "I"
```

### SQLAlchemy/SQLModel RUF012 Errors
SQLAlchemy's `__table_args__` and similar class attributes trigger RUF012 (mutable class attribute).

**Solution:** Add `# noqa: RUF012` to these specific lines:
```python
class MyModel(SQLModel, table=True):
    __tablename__ = "my_table"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
```

**Why:** These are framework-specific patterns where mutable class attributes are intentional and managed by SQLAlchemy's metaclass.

**Common patterns requiring noqa:**
- `__table_args__` (SQLAlchemy/SQLModel)
- `__mapper_args__` (SQLAlchemy)
- `Config` class with `table_args` list (SQLModel)
