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

# Execute example notebooks and save output in-place
examples:
    @echo "Executing example notebooks..."
    uv run --with jupyter,pandas jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 examples/pandas/highlighting.ipynb
    uv run --with jupyter,polars jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 examples/polars/highlighting.ipynb
    @echo "✓ Notebooks executed with outputs saved"
    @echo "  - examples/pandas/highlighting.ipynb"
    @echo "  - examples/polars/highlighting.ipynb"

# Release a new version (launches GitHub Actions workflow)
release:
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "Current version: $(uv version --short)"
    echo ""
    echo "Select release type:"
    echo "  1) patch (0.1.0 -> 0.1.1)"
    echo "  2) minor (0.1.0 -> 0.2.0)"
    echo "  3) major (0.1.0 -> 1.0.0)"
    echo ""
    read -p "Enter choice (1/2/3): " choice
    
    case "$choice" in
        1) bump_type="patch" ;;
        2) bump_type="minor" ;;
        3) bump_type="major" ;;
        *) echo "Invalid choice. Aborting."; exit 1 ;;
    esac
    
    echo ""
    echo "Will bump $bump_type version..."
    uv version --bump "$bump_type" --dry-run
    echo ""
    read -p "Proceed with release? (y/N): " confirm
    
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Release cancelled."
        exit 0
    fi
    
    echo ""
    echo "Running CI checks..."
    just ci
    
    echo ""
    echo "Bumping version..."
    uv version --bump "$bump_type"
    
    new_version=$(uv version --short)
    echo ""
    echo "✓ Version bumped to $new_version"
    
    echo ""
    echo "Committing and tagging release..."
    git add pyproject.toml
    if [ -f uv.lock ]; then git add uv.lock; fi
    git commit -m "Release v$new_version"
    git tag -a "v$new_version" -m "Release v$new_version"
    
    echo ""
    echo "Pushing to remote to trigger GitHub Actions..."
    git push origin main && git push origin --tags
    
    echo ""
    echo "🚀 Release v$new_version pushed!"
    echo "GitHub Actions will now:"
    echo "  1. Run cross-platform tests"
    echo "  2. Publish to PyPI"
    echo "  3. Create a GitHub Release with signed artifacts"
    echo ""
    echo "Monitor progress at: https://github.com/erichutchins/nwgrep/actions"
