# Contributing to nwgrep

Thank you for your interest in contributing to nwgrep! This document provides guidelines and instructions for development.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- [just](https://github.com/casey/just) - Command runner (optional but recommended)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/erichutchins/nwgrep.git
   cd nwgrep
   ```

2. Sync development dependencies:

   ```bash
   # Using just (recommended)
   just sync

   # Or using uv directly
   uv sync --group dev
   ```

This installs:

- Core test backends: pandas, polars, pyarrow
- Test tools: pytest, pytest-cov
- Linting tools: ruff, pre-commit

## Development Workflow

### Using just (Recommended)

Run `just` to see all available commands:

```bash
just --list
```

Common commands:

| Command                    | Description                              |
| -------------------------- | ---------------------------------------- |
| `just sync`                | Sync development dependencies            |
| `just test`                | Run all tests with core backends         |
| `just test-backend pandas` | Run tests with a specific backend        |
| `just lint`                | Run linter                               |
| `just lint-fix`            | Run linter and auto-fix issues           |
| `just format`              | Format code                              |
| `just check`               | Run all checks (lint, format, typecheck) |
| `just ci`                  | Full CI check (checks + tests)           |
| `just smoke`               | Run smoke test                           |
| `just coverage`            | Generate HTML coverage report            |

### Using uv Directly

If you prefer not to use just:

```bash
# Run tests
uv run pytest --backend=pandas --backend=polars --backend=pyarrow

# Run linter
uv run ruff check src/ tests/

# Run formatter
uv run ruff format src/ tests/

# Run type checker
uvx ty check src/

# Run smoke test
uv run python tests/smoke_test.py
```

## Testing

### Running Tests

Tests support multiple backends via the `--backend` flag:

```bash
# Run with all core backends
just test

# Run with specific backend(s)
uv run pytest --backend=pandas
uv run pytest --backend=polars --backend=pyarrow

# Run specific test file
just test tests/test_cli.py

# Run with verbose output
just test -v
```

### Test Structure

- `tests/test_nwgrep.py` - Core nwgrep function tests
- `tests/test_cli.py` - CLI integration tests
- `tests/test_accessor.py` - Pandas/Polars accessor tests
- `tests/smoke_test.py` - Basic import and functionality check

## Code Quality

### Linting and Formatting

We use [ruff](https://docs.astral.sh/ruff/) for both linting and formatting:

```bash
# Check for issues
just lint
just format-check

# Auto-fix issues
just lint-fix
just format
```

### Type Checking

We use [ty](https://github.com/astral-sh/ty) for type checking:

```bash
just typecheck
```

### Pre-commit Hooks

Install pre-commit hooks to run checks automatically before each commit:

```bash
uv run pre-commit install
```

Run hooks manually on all files:

```bash
just pre-commit
```

## Project Structure

```
nwgrep/
├── src/nwgrep/
│   ├── __init__.py      # Package exports
│   ├── core.py          # Main nwgrep() function
│   ├── accessor.py      # Pandas/Polars .grep() accessor
│   └── cli.py           # Command-line interface
├── tests/
│   ├── conftest.py      # Pytest fixtures
│   ├── test_nwgrep.py   # Core function tests
│   ├── test_cli.py      # CLI tests
│   ├── test_accessor.py # Accessor tests
│   └── smoke_test.py    # Smoke test
├── pyproject.toml       # Project configuration
├── justfile             # Development commands
└── CONTRIBUTING.md      # This file
```

## Dependency Groups

The project uses uv dependency groups for organization:

| Group   | Contents                | Usage                        |
| ------- | ----------------------- | ---------------------------- |
| `core`  | pandas, polars, pyarrow | Core test backends           |
| `tests` | pytest, pytest-cov      | Test runner                  |
| `lint`  | ruff, pre-commit        | Code quality tools           |
| `dev`   | All of the above        | Full development environment |

Install specific groups:

```bash
uv sync --group tests        # Just test tools
uv sync --group dev          # Full dev environment
```

## Making Changes

1. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all checks pass:

   ```bash
   just ci
   ```

3. Commit your changes with a descriptive message following [conventional commits](https://www.conventionalcommits.org/):

   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in cli"
   git commit -m "docs: update contributing guide"
   ```

4. Push and open a pull request.

## CLI Development

The CLI requires polars for efficient lazy scanning of binary formats. Users install it with:

```bash
pip install 'nwgrep[cli]'
```

When developing CLI features, ensure polars is available:

```bash
uv sync --group dev  # Already includes polars via core group
```

## Questions?

Feel free to open an issue for questions or discussions about contributing.
