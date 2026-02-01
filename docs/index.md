# nwgrep

> **Grep your dataframes**

Search and filter dataframes with grep-like patterns. Works with pandas, polars, and any backend supported by [Narwhals](https://narwhals-dev.github.io/narwhals/).

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/refs/heads/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/erichutchins/nwgrep/blob/main/LICENSE)
[![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](https://claude.ai)
[![Gemini](https://img.shields.io/badge/Gemini-8E75FF?logo=googlegemini&logoColor=fff)](https://antigravity.google)

```python
# Find what you're looking for
df.grep("active")              # Simple search
df.grep("@gmail.com")          # Find patterns
df.grep(r"^\d{3}-\d{4}$")      # Regex support
```

## What is nwgrep?

nwgrep brings the familiar power of `grep` to dataframes. Search across columns, filter by patterns, use regex - all with a simple, intuitive interface that works seamlessly with any dataframe library thanks to [Narwhals](https://narwhals-dev.github.io/narwhals/).

## Why nwgrep?

:material-magnify: **Familiar Interface**
: If you know `grep`, you know nwgrep. Same flags (`-i`, `-v`, `-E`), same intuition.

:material-rocket-launch: **Backend Agnostic**
: Write once, run anywhere. Switch from pandas to polars without changing your code.

:material-target: **Simple to Use**
: Three ways to use: function call, pipe method, or accessor. Choose what feels natural.

:material-flash: **Lightning Fast**
: Lazy evaluation with polars/daft. Process multi-GB files efficiently.

:material-shield-check: **Type Safe**
: Full type hints. Catch errors before runtime with ty.

## Quick Start

Install with your preferred backend:

```bash
uv add nwgrep[polars]  # or pandas, dask, pyarrow, cudf
```

Search your data:

```python
import pandas as pd
from nwgrep import nwgrep

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "locked", "active"],
})

# Find all rows containing "active"
result = nwgrep(df, "active")
```

That's it. No complex queries, no backend-specific syntax.

## Three Ways to Use

Choose the style that fits your workflow:

=== "Direct Function"

    Simple and explicit.

    ```python
    from nwgrep import nwgrep
    result = nwgrep(df, "active")
    ```

    Best for: Simple scripts, one-off searches, maximum clarity.

=== "Pipe Method"

    Functional style for data pipelines.

    ```python
    result = (
        df
        .pipe(nwgrep, "active")
        .pipe(nwgrep, "@example.com", columns=["email"])
        .pipe(lambda x: x.sort_values('name'))
    )
    ```

    Best for: Data pipelines, method chaining, functional programming.

=== "Accessor Method"

    Cleanest syntax for interactive use.

    ```python
    from nwgrep import register_grep_accessor
    register_grep_accessor()  # Once at startup

    df.grep("active")
    df.grep("ALICE", case_sensitive=False)
    df.grep("example.com", columns=["email"])
    ```

    Best for: Notebooks, interactive analysis, frequent searching.

=== "Command Line"

    Search binary formats directly.

    ```bash
    nwgrep "error" logfile.parquet
    nwgrep -i "warning" data.feather
    nwgrep --format ndjson "pattern" data.parquet | jq .
    ```

    Best for: Shell scripts, one-liners, exploring data files.

## Powerful Search Options

All the grep features you know and love:

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
```

## Backend Support

Works seamlessly with any dataframe library:

| Backend     | Status                              | Notes                   |
| ----------- | ----------------------------------- | ----------------------- |
| **pandas**  | :material-check-circle:{ .success } | Full support            |
| **polars**  | :material-check-circle:{ .success } | DataFrame and LazyFrame |
| **pyarrow** | :material-check-circle:{ .success } | Table support           |
| **dask**    | :material-check-circle:{ .success } | Distributed dataframes  |
| **daft**    | :material-check-circle:{ .success } | Lazy evaluation         |
| **cuDF**    | :material-check-circle:{ .success } | GPU acceleration        |
| **modin**   | :material-check-circle:{ .success } | Parallel pandas         |

Same code, any backend. Switch freely without rewriting your filters.

## Real-World Examples

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
    .grep("active", columns=["status"])      # Active users
    .grep("@company.com", columns=["email"]) # Company emails
    .grep("admin", invert=True)              # Exclude admins
)
```

## Why Narwhals?

[Narwhals](https://narwhals-dev.github.io/narwhals/) provides a unified API across dataframe libraries. This means:

- **Write once, run anywhere** - Same code for pandas, polars, or any backend
- **No vendor lock-in** - Switch backends without rewriting code
- **Automatic optimization** - Each backend uses its strengths
- **Future-proof** - Support for new backends as they emerge

nwgrep is a certified Narwhals plugin, enabling truly backend-agnostic filtering.

## Next Steps

<div class="grid cards" markdown>

- :material-download:{ .lg .middle } **Installation**

  ***

  Get nwgrep installed with your preferred backends

  [:octicons-arrow-right-24: Installation Guide](installation.md)

- :material-book-open-variant:{ .lg .middle } **Usage**

  ***

  Learn all the ways to search and filter your data

  [:octicons-arrow-right-24: Usage Examples](usage.md)

- :material-api:{ .lg .middle } **API Reference**

  ***

  Complete function and parameter documentation

  [:octicons-arrow-right-24: API Reference](api.md)

- :material-console:{ .lg .middle } **CLI Reference**

  ***

  Command-line interface for binary formats

  [:octicons-arrow-right-24: CLI Reference](cli.md)

</div>

## Credit

Built with :material-heart:{ .pulse } using [Narwhals](https://narwhals-dev.github.io/narwhals/) for dataframe abstraction.

Special thanks to Claude and Gemini for their assistance in developing this project.
