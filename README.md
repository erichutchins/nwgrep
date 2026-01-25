# nwgrep

Grep-like tool for dataframes that works with pandas, polars, and any other backend supported by [Narwhals](https://narwhals-dev.github.io/narwhals/).

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=fff)](https://claude.ai)
[![Gemini](https://img.shields.io/badge/Gemini-8E75FF?logo=googlegemini&logoColor=fff)](https://antigravity.google)


## Installation

```bash
uv add nwgrep
```

With specific backends:
```bash
uv add nwgrep[pandas]  # pandas support
uv add nwgrep[polars]  # polars support
uv add nwgrep[dask]    # dask support
uv add nwgrep[cudf]    # cuDF (GPU) support
uv add nwgrep[all]     # all major backends
```

Or using `pip`:
```bash
pip install nwgrep
```

## Usage

### Method 1: Direct Function Call

```python
from nwgrep import nwgrep
import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "locked", "active"],
})

result = nwgrep(df, "active")

print(result)
    name  status
0  Alice  active
2    Eve  active
```

### Method 2: Using .pipe() (Pandas/Polars Style)

```python
# Works with any backend!
result = df.pipe(nwgrep, "active")

# Beautiful chaining
result = (
    df
    .pipe(nwgrep, "active")
    .pipe(lambda x: x.sort_values('name', ascending=False))
)

print(result)
    name  status
2    Eve  active
0  Alice  active
```

### Method 3: Accessor Pattern (df.grep)

```python
from nwgrep import register_grep_accessor
import pandas as pd

# Register once at start of your script/notebook
register_grep_accessor()

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "locked", "active"],
})

# Now you can use .grep() directly!
result = df.grep("active")
result = df.grep("ACTIVE", case_sensitive=False)
result = df.grep("active", columns=["status"])
```

**Works with both pandas and polars:**

```python
import polars as pl
from nwgrep import register_grep_accessor

register_grep_accessor()

df = pl.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "locked", "active"],
})

# Same syntax!
result = df.grep("active")
```

### Method 4: Narwhals Plugin Integration

`nwgrep` is fully Narwhals-compliant. This means you can use it directly with Narwhals objects, and it will be auto-discovered as a plugin by other Narwhals-based tools.

```python
import narwhals as nw
import pandas as pd
from nwgrep import nwgrep

# nwgrep handles Narwhals objects natively and returns Narwhals objects
df = nw.from_native(pd.DataFrame({"col": ["foo", "bar"]}))
result = nwgrep(df, "foo")

print(type(result)) # <class 'narwhals.dataframe.DataFrame'>
```

## All Search Options

```python
# Case-insensitive search
df.grep("ACTIVE", case_sensitive=False)

# Invert match (like grep -v)
df.grep("active", invert=True)

# Search specific columns only
df.grep("example.com", columns=["email"])

# Regex search
df.grep(r".*@example\.com", regex=True)

# Multiple patterns (OR logic)
df.grep(["Alice", "Bob"])

# Whole word matching
df.grep("active", whole_word=True)
```

### Command Line

```bash
# Basic search
uv run nwgrep "error" logfile.parquet

# Case insensitive
uv run nwgrep -i "warning" data.feather

# Invert match
uv run nwgrep -v "success" data.parquet

# Regex search
uv run nwgrep -E "err(or|!)?" data.parquet

# Search specific columns
uv run nwgrep --columns name,email "alice" users.feather

# Limit output rows
uv run nwgrep -n 10 "pattern" large_file.parquet

# Output as NDJSON (Streams lazily if polars is installed!)
uv run nwgrep "pattern" data.parquet --format ndjson

# Output as CSV
uv run nwgrep --format csv "pattern" data.parquet > results.csv
```

## Which Method Should I Use?

| Method | When to Use |
|--------|-------------|
| **`nwgrep(df, ...)`** | Simple scripts, maximum compatibility |
| **`df.pipe(nwgrep, ...)`** | Data pipelines, functional style |
| **`df.grep(...)`** | Interactive use (notebooks), cleanest syntax |
| **Narwhals native** | When working within a Narwhals data-agnostic pipeline |

## Features

- 🚀 **Backend agnostic**: Works with pandas, polars, daft, pyarrow
- 🔍 **Multiple search modes**: Literal, regex, case-sensitive/insensitive
- 📊 **Column filtering**: Search all columns or specific ones
- ⚡ **Lazy evaluation**: Efficient with large datasets when using polars/daft
- 🎯 **Familiar interface**: grep-like flags and behavior
- 🔧 **Type safe**: Full type hints and mypy support
- 🎨 **Flexible API**: Function, pipe, or method - your choice!

## API Reference

### `nwgrep(df, pattern, **kwargs)`

**Parameters:**
- `df`: DataFrame or LazyFrame (Native or Narwhals)
- `pattern`: str or list of str - Search pattern(s)
- `columns`: list of str, optional - Specific columns to search
- `case_sensitive`: bool, default True
- `regex`: bool, default False - Treat pattern as regex
- `invert`: bool, default False - Return non-matching rows
- `whole_word`: bool, default False - Match whole words only

**Returns:** Same type as input (Native or Narwhals DataFrame/LazyFrame)

### `register_grep_accessor()`

Registers `.grep()` method on pandas and polars DataFrames. Call once at the start of your script or notebook.

## Examples

Check the [examples](./examples) directory for complete scripts using both Pandas and Polars.

## License

MIT License - see LICENSE file for details