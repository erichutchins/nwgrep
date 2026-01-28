# nwgrep development tasks
# Run `just --list` to see available recipes

# Default recipe - show help
default:
    @just --list

# Sync development dependencies
sync:
    uv sync --group dev

# Run all tests with core backends (pandas, polars, pyarrow)
test *ARGS:
    uv run pytest --backend=pandas --backend=polars --backend=pyarrow {{ ARGS }}

# Run tests with a specific backend
test-backend BACKEND *ARGS:
    uv run pytest --backend={{ BACKEND }} {{ ARGS }}

# Run linter
lint:
    uv run ruff check src/ tests/ examples/

# Run linter and fix issues
lint-fix:
    uv run ruff check --fix src/ tests/ examples/

# Run formatter check
format-check:
    uv run ruff format --check src/ tests/ examples/

# Run formatter
format:
    uv run ruff format src/ tests/ examples/

# Run type checker
typecheck:
    uvx ty check src/

# Run all checks (lint, format, typecheck)
check: lint format-check typecheck

# Run smoke test
smoke:
    uv run python tests/smoke_test.py

# Build the package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info src/*.egg-info .pytest_cache .coverage htmlcov/

# Run pre-commit hooks on all files
pre-commit:
    prek run --all-files

# Full CI check: lint, format, typecheck, and tests
ci: check test

# Show coverage report
coverage:
    uv run pytest --backend=pandas --backend=polars --backend=pyarrow --cov=nwgrep --cov-report=html
    @echo "Coverage report generated in htmlcov/"

# Serve documentation locally
docs-serve:
    uv run --group docs mkdocs serve

# Build documentation
docs-build:
    uv run --group docs mkdocs build

# Deploy documentation to GitHub Pages
docs-deploy:
    uv run --group docs mkdocs gh-deploy --force

# Clean documentation build artifacts
docs-clean:
    rm -rf site/
