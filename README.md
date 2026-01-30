# nwgrep

> **Grep your dataframes**

Search and filter dataframes with grep-like patterns. Works with pandas, polars, and any backend supported by [Narwhals](https://narwhals-dev.github.io/narwhals/).

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://erichutchins.github.io/nwgrep/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/refs/heads/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](https://claude.ai)
[![Gemini](https://img.shields.io/badge/Gemini-8E75FF?logo=googlegemini&logoColor=fff)](https://antigravity.google)

## At a Glance

```python
# Find what you're looking for
df.grep("active")              # Simple search
df.grep("@gmail.com")          # Find patterns
df.grep(r"^\d{3}-\d{4}$")      # Regex support
```

## Why nwgrep?

- **🔍 Familiar** - grep-like interface for row-based dataframe filtering
- **🚀 Fast** - Backend-agnostic, works with your preferred library
- **🎯 Simple** - Three ways to use: function, pipe, or accessor
- **⚡ Efficient** - Lazy evaluation with polars/daft for large datasets

## Quick Start

```bash
uv add nwgrep
```

```python
from nwgrep import nwgrep
import polars as pl

df = pl.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "locked", "active"],
})

# Find all rows containing "active"
result = nwgrep(df, "active")

# ┌───────┬────────┐
# │ name  ┆ status │
# │ ---   ┆ ---    │
# │ str   ┆ str    │
# ╞═══════╪════════╡
# │ Alice ┆ active │
# │ Eve   ┆ active │
# └───────┴────────┘
```

## Three Ways to Use

Choose the style that fits your workflow:

### 1. Direct Function

```python
from nwgrep import nwgrep
result = nwgrep(df, "active")
```

### 2. Pipe Method

```python
result = (
    df
    .pipe(nwgrep, "active")
    .pipe(nwgrep, "@example.com", columns=["email"])
)
```

### 3. Accessor Method

For Polars and Pandas backends, you can use the accessor method to add `.grep` function directly to the DataFrame:

```python
from nwgrep import register_grep_accessor
register_grep_accessor()

df.grep("active")                    # Search all columns
df.grep("ALICE", case_sensitive=False)  # Case-insensitive
df.grep("example.com", columns=["email"])  # Specific columns
```

## Powerful Search Options

```python
# Case-insensitive search
df.grep("ACTIVE", case_sensitive=False)

# Invert match (like grep -v)
df.grep("test", invert=True)

# Regex patterns
df.grep(r".*@example\.com", regex=True)

# Multiple patterns (OR logic)
df.grep(["Alice", "Bob"])

# Whole word matching
df.grep("active", whole_word=True)

# Column-specific search
df.grep("pattern", columns=["name", "email"])

# Highlight matching cells in notebooks (pandas/polars)
df.grep("error", highlight=True)  # Returns styled output with highlighted cells
```

## Command Line Interface

Search parquet, feather, and other binary formats directly:

```bash
# Install cli
uv tool install "nwgrep[cli]"

# Basic search
nwgrep "error" logfile.parquet

# Case insensitive + regex
nwgrep -i -E "warn(ing)?" data.feather

# Column-specific search
nwgrep --columns email "@gmail.com" users.parquet

# Count matching rows
nwgrep --count "pattern" data.parquet

# List files with matches (like grep -l)
nwgrep -l "error" *.parquet

# Show only matching values (like grep -o)
nwgrep -o "error" data.parquet

# Stream as NDJSON (lazy evaluation)
nwgrep --format ndjson "pattern" huge_file.parquet
```

## Backend Support

Works seamlessly with any dataframe library thanks to Narwhals:

| Backend     | Support | Notes                   |
| ----------- | ------- | ----------------------- |
| **pandas**  | ✅      | Full support            |
| **polars**  | ✅      | DataFrame and LazyFrame |
| **pyarrow** | ✅      | Table support           |
| **dask**    | ✅      | Distributed dataframes  |
| **daft**    | ✅      | Lazy evaluation         |
| **cuDF**    | ✅      | GPU acceleration        |
| **modin**   | ✅      | Parallel pandas         |

Same code, any backend. Switch freely without rewriting your filters.

## Installation

Basic installation:

```bash
uv add nwgrep
# or
pip install nwgrep
```

With specific backends:

```bash
uv add nwgrep             # core library
uv add nwgrep[cli]        # CLI for searching parquet/feather filesn using polars
uv add nwgrep[notebook]   # highlighting in notebooks (pandas/polars)
uv add nwgrep[all]        # include all features (cli + notebook)
```

Note: `nwgrep` is designed to be added to an existing environment with a dataframe library (pandas, polars, etc.) already installed. It does not install these backends by default, except for `polars` when installing the `[cli]` extra.

## Features

- 🚀 **Backend agnostic**: Write once, run on any dataframe library
- 🔍 **Multiple search modes**: Literal, regex, case-sensitive/insensitive
- 📊 **Column filtering**: Search all columns or specific ones
- ⚡ **Lazy evaluation**: Efficient with large datasets (polars/daft)
- 🎯 **Familiar interface**: grep-like flags and behavior (`-i`, `-v`, `-E`)
- 🔧 **Type safe**: Full type hints with ty type checking
- 🎨 **Flexible API**: Function, pipe, or accessor - your choice
- 🖥️ **CLI included**: Search binary formats from the command line

## Documentation

Full documentation available at **[erichutchins.github.io/nwgrep](https://erichutchins.github.io/nwgrep/)**

- [Installation Guide](https://erichutchins.github.io/nwgrep/installation/) - Setup for all backends
- [Usage Examples](https://erichutchins.github.io/nwgrep/usage/) - Comprehensive examples
- [API Reference](https://erichutchins.github.io/nwgrep/api/) - Complete function reference
- [CLI Reference](https://erichutchins.github.io/nwgrep/cli/) - Command-line usage

## Quick Examples

### Find Active Users

```python
users = df.grep("active", columns=["status"])
```

### Email Domain Search

```python
gmail_users = df.grep("@gmail.com", columns=["email"])
```

### Log Analysis

```python
errors = df.grep(["ERROR", "CRITICAL"], columns=["level"])
```

### Data Quality Checks

```python
# Find rows without email addresses
missing_email = df.grep(r"\w+@\w+\.\w+", regex=True, invert=True)
```

### Pipeline Filtering

```python
result = (
    df
    .grep("active", columns=["status"])     # Active users
    .grep("@company.com", columns=["email"]) # Company emails
    .grep("admin", invert=True)              # Exclude admins
)
```

## Narwhals Integration

nwgrep is a certified Narwhals plugin, enabling truly backend-agnostic code:

```python
import narwhals as nw
from nwgrep import nwgrep

def process_any_dataframe(df_native):
    """Works with pandas, polars, pyarrow, or any Narwhals-supported backend"""
    df = nw.from_native(df_native)
    result = nwgrep(df, "pattern")
    return nw.to_native(result)
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

Built with [Narwhals](https://narwhals-dev.github.io/narwhals/)
