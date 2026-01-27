# nwgrep

**Grep-like tool for dataframes using Narwhals** - works with pandas, polars, pyarrow, daft, dask, modin, cuDF, and more.

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/erichutchins/nwgrep/blob/main/LICENSE)

## What is nwgrep?

nwgrep brings the familiar power of `grep` to dataframes. Search across all columns, filter by patterns, use regex, and work seamlessly with any dataframe library thanks to [Narwhals](https://narwhals-dev.github.io/narwhals/).

## Quick Start

```bash
uv add nwgrep
# or
pip install nwgrep
```

```python
import pandas as pd
from nwgrep import nwgrep

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "locked", "active"],
})

# Search for "active" across all columns
result = nwgrep(df, "active")
```

## Key Features

:octicons-zap-24: **Backend Agnostic**
:   Works with pandas, polars, pyarrow, daft, dask, modin, cuDF - any backend supported by Narwhals

:octicons-search-24: **Powerful Search**
:   Literal text, regex patterns, case-sensitive or insensitive, whole word matching

:octicons-filter-24: **Column Filtering**
:   Search all columns or specify exactly which ones to search

:octicons-rocket-24: **Lazy Evaluation**
:   Efficient with large datasets when using polars or daft LazyFrames

:octicons-terminal-24: **Command Line Interface**
:   grep-like CLI for searching parquet, feather, and other binary formats

:octicons-code-24: **Flexible API**
:   Use as a function, with `.pipe()`, or as a `.grep()` accessor method

:octicons-shield-check-24: **Type Safe**
:   Full type hints with ty (Red Knot) type checking

## Multiple Ways to Use

Choose the style that fits your workflow:

=== "Direct Function"

    ```python
    from nwgrep import nwgrep
    result = nwgrep(df, "active")
    ```

=== "Pipe Method"

    ```python
    result = df.pipe(nwgrep, "active")
    
    # Beautiful chaining
    result = (
        df
        .pipe(nwgrep, "active")
        .pipe(lambda x: x.sort_values('name'))
    )
    ```

=== "Accessor Method"

    ```python
    from nwgrep import register_grep_accessor
    register_grep_accessor()
    
    # Now use .grep() directly
    result = df.grep("active")
    ```

=== "Command Line"

    ```bash
    nwgrep "error" logfile.parquet
    nwgrep -i "warning" data.feather
    nwgrep --format ndjson "pattern" data.parquet
    ```

## Why Narwhals?

[Narwhals](https://narwhals-dev.github.io/narwhals/) provides a unified API across dataframe libraries. This means:

- Write code once, run on any backend
- No vendor lock-in - switch backends freely
- Automatic optimization based on backend capabilities
- Future-proof as new backends emerge

## Next Steps

- [Installation Guide](installation.md) - Get nwgrep installed with your preferred backends
- [Usage Examples](usage.md) - Learn all the ways to search and filter
- [API Reference](api.md) - Complete function reference
- [CLI Reference](cli.md) - Command-line usage

## Credit

Built with love using [Narwhals](https://narwhals-dev.github.io/narwhals/) for dataframe abstraction.
