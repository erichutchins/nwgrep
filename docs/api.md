# API Reference

Complete reference for all nwgrep functions and methods.

## Core Function

### `nwgrep()`

Search and filter dataframes with grep-like functionality.

```python
nwgrep(
    df,
    pattern,
    *,
    columns=None,
    case_sensitive=True,
    regex=False,
    invert=False,
    whole_word=False
)
```

**Parameters:**

- **`df`** : DataFrame or LazyFrame (pandas, polars, pyarrow, daft, etc.)
    
    The dataframe to search. Can be a native dataframe or a Narwhals DataFrame.

- **`pattern`** : `str` or `list[str]`
    
    The search pattern(s). If a list is provided, matches any pattern (OR logic).

- **`columns`** : `list[str]`, optional
    
    Specific column names to search. If `None` (default), searches all columns.

- **`case_sensitive`** : `bool`, default `True`
    
    Whether the search should be case-sensitive.

- **`regex`** : `bool`, default `False`
    
    If `True`, treat `pattern` as a regular expression. If `False`, treat as literal string.

- **`invert`** : `bool`, default `False`
    
    If `True`, return rows that do NOT match the pattern (like `grep -v`).

- **`whole_word`** : `bool`, default `False`
    
    If `True`, only match complete words. Adds word boundaries (`\b`) around the pattern.

**Returns:**

Same type as input - DataFrame or LazyFrame matching the input backend.

**Examples:**

Basic search:

```python
import pandas as pd
from nwgrep import nwgrep

df = pd.DataFrame({"col": ["foo", "bar", "baz"]})
result = nwgrep(df, "ba")
# Returns rows with "bar" and "baz"
```

Case-insensitive:

```python
result = nwgrep(df, "FOO", case_sensitive=False)
# Matches "foo", "FOO", "Foo", etc.
```

Column-specific:

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "email": ["alice@test.com", "bob@test.com"]
})
result = nwgrep(df, "alice", columns=["name"])
# Only searches the name column
```

Regex:

```python
result = nwgrep(df, r"\.com$", regex=True, columns=["email"])
# Finds emails ending with .com
```

Multiple patterns:

```python
result = nwgrep(df, ["Alice", "Bob"])
# Finds rows containing "Alice" OR "Bob"
```

Invert match:

```python
result = nwgrep(df, "test", invert=True)
# Returns rows NOT containing "test"
```

Whole word:

```python
df = pd.DataFrame({"text": ["active", "activate", "actor"]})
result = nwgrep(df, "active", whole_word=True)
# Only matches "active", not "activate"
```

---

## Accessor Registration

### `register_grep_accessor()`

Register the `.grep()` accessor method on pandas and polars DataFrames.

```python
register_grep_accessor()
```

**Parameters:** None

**Returns:** None

**Side Effects:**

Registers `.grep()` method on:

- `pandas.DataFrame`
- `polars.DataFrame`
- `polars.LazyFrame`

**Examples:**

```python
from nwgrep import register_grep_accessor
import pandas as pd

# Register once at the start
register_grep_accessor()

df = pd.DataFrame({"col": ["foo", "bar"]})

# Now you can use .grep() directly
result = df.grep("foo")
result = df.grep("FOO", case_sensitive=False)
result = df.grep("pattern", columns=["col"])
```

Works with polars too:

```python
import polars as pl
from nwgrep import register_grep_accessor

register_grep_accessor()

df = pl.DataFrame({"col": ["foo", "bar"]})
result = df.grep("foo")
```

!!! warning
    Call `register_grep_accessor()` only once per session, typically at the start of your script or notebook.

---

## DataFrame Accessor Method

### `.grep()`

Available after calling `register_grep_accessor()`.

```python
df.grep(
    pattern,
    *,
    columns=None,
    case_sensitive=True,
    regex=False,
    invert=False,
    whole_word=False
)
```

**Parameters:**

Same as [`nwgrep()`](#nwgrep), except `df` is implicit (the dataframe you're calling `.grep()` on).

**Returns:**

Same type as the input dataframe.

**Examples:**

```python
from nwgrep import register_grep_accessor
import pandas as pd

register_grep_accessor()

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "status": ["active", "inactive", "active"]
})

# Find active users
active = df.grep("active")

# Case-insensitive search
users = df.grep("ALICE", case_sensitive=False)

# Column-specific
name_search = df.grep("Alice", columns=["name"])

# Regex
email_pattern = df.grep(r".*@example\.com", regex=True)

# Exclude pattern
not_active = df.grep("active", invert=True)
```

---

## Type Signatures

nwgrep includes complete type annotations. The simplified signatures are:

```python
from typing import TypeVar, overload
import narwhals as nw

FrameT = TypeVar("FrameT")

@overload
def nwgrep(
    df: FrameT,
    pattern: str | list[str],
    *,
    columns: list[str] | None = None,
    case_sensitive: bool = True,
    regex: bool = False,
    invert: bool = False,
    whole_word: bool = False,
) -> FrameT: ...

# Narwhals-specific overload
@overload
def nwgrep(
    df: nw.DataFrame[Any],
    pattern: str | list[str],
    *,
    columns: list[str] | None = None,
    case_sensitive: bool = True,
    regex: bool = False,
    invert: bool = False,
    whole_word: bool = False,
) -> nw.DataFrame[Any]: ...
```

The function preserves the exact type of the input dataframe.

---

## Narwhals Integration

nwgrep is a Narwhals plugin, meaning:

- It can be auto-discovered by Narwhals-aware tools
- It handles Narwhals DataFrames natively
- It returns Narwhals DataFrames when given Narwhals input

```python
import narwhals as nw
from nwgrep import nwgrep

# Native pandas
import pandas as pd
df_native = pd.DataFrame({"col": ["a", "b"]})

# Convert to Narwhals
df_nw = nw.from_native(df_native)

# nwgrep handles both
result_nw = nwgrep(df_nw, "a")  # Returns Narwhals DataFrame
result_native = nwgrep(df_native, "a")  # Returns pandas DataFrame

# Convert back if needed
result_pandas = nw.to_native(result_nw)
```

---

## Parameter Combinations

Here are common parameter combinations:

| Use Case | Parameters |
|----------|------------|
| Literal search | `pattern="text"` |
| Case-insensitive | `case_sensitive=False` |
| Regex search | `regex=True` |
| Specific columns | `columns=["col1", "col2"]` |
| Exclude pattern | `invert=True` |
| Whole words only | `whole_word=True` |
| Multiple patterns | `pattern=["text1", "text2"]` |
| Complex regex | `pattern=r"^\w+@\w+\.\w+$", regex=True` |

---

## Supported Backends

nwgrep works with any backend supported by Narwhals:

| Backend | Type Preserved | Notes |
|---------|----------------|-------|
| pandas | ✅ | Returns `pandas.DataFrame` |
| polars (eager) | ✅ | Returns `polars.DataFrame` |
| polars (lazy) | ✅ | Returns `polars.LazyFrame` |
| pyarrow | ✅ | Returns `pyarrow.Table` |
| daft | ✅ | Returns `daft.DataFrame` (lazy) |
| dask | ✅ | Returns `dask.dataframe.DataFrame` |
| modin | ✅ | Returns `modin.pandas.DataFrame` |
| cuDF | ✅ | Returns `cudf.DataFrame` |

The return type always matches the input type.

---

## Error Handling

nwgrep raises clear errors for common issues:

**Invalid column names:**

```python
nwgrep(df, "pattern", columns=["nonexistent"])
# Raises: ValueError: Column 'nonexistent' not found
```

**Invalid regex:**

```python
nwgrep(df, r"[invalid(regex", regex=True)
# Raises: re.error with details
```

**Empty pattern:**

```python
nwgrep(df, "")
# Returns empty dataframe (no matches)
```

---

## Performance Characteristics

- **O(n × m)** where n = rows, m = columns searched
- Column filtering reduces m significantly
- Lazy backends (polars, daft) defer execution
- String operations are optimized per backend

**Best Practices:**

1. Use `columns` parameter when possible
2. Use lazy frames for large data
3. Compile complex regex patterns outside if reusing
4. Consider backend strengths (polars for large data, pandas for small)

---

## See Also

- [Usage Guide](usage.md) - Examples and patterns
- [CLI Reference](cli.md) - Command-line interface
- [Narwhals Documentation](https://narwhals-dev.github.io/narwhals/) - Backend abstraction
