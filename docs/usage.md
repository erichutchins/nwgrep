# Usage Guide

This guide covers all the ways to use nwgrep for searching and filtering dataframes.

## Basic Search

Search for a pattern across all columns:

```python
import pandas as pd
from nwgrep import nwgrep

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Eve"],
    "email": ["alice@example.com", "bob@test.org", "eve@example.com"],
    "status": ["active", "locked", "active"],
})

# Find all rows containing "active"
result = nwgrep(df, "active")
print(result)
```

Output:

```
    name               email  status
0  Alice  alice@example.com  active
2    Eve    eve@example.com  active
```

## Search Options

### Case-Insensitive Search

```python
# Match "ACTIVE", "active", "Active", etc.
result = nwgrep(df, "ACTIVE", case_sensitive=False)
```

### Invert Match

Return rows that **don't** match the pattern (like `grep -v`):

```python
# Find all rows NOT containing "active"
result = nwgrep(df, "active", invert=True)
print(result)
```

Output:

```
  name           email  status
1  Bob  bob@test.org  locked
```

### Column-Specific Search

Search only in specific columns:

```python
# Only search in the email column
result = nwgrep(df, "example.com", columns=["email"])
print(result)
```

Output:

```
    name               email  status
0  Alice  alice@example.com  active
2    Eve    eve@example.com  active
```

### Regex Search

Use regular expressions for complex patterns:

```python
# Find emails with .com domain
result = nwgrep(df, r"\.com$", regex=True, columns=["email"])

# Find names starting with A or E
result = nwgrep(df, r"^(A|E)", regex=True, columns=["name"])
```

### Multiple Patterns

Search for any of multiple patterns (OR logic):

```python
# Find rows containing "Alice" OR "Bob"
result = nwgrep(df, ["Alice", "Bob"])
```

### Whole Word Matching

Match complete words only:

```python
df = pd.DataFrame({
    "text": ["activate", "active", "actor"]
})

# Only matches "active", not "activate" or "actor"
result = nwgrep(df, "active", whole_word=True)
```

## Usage Patterns

### Method 1: Direct Function Call

The simplest approach - call `nwgrep()` directly:

```python
from nwgrep import nwgrep

result = nwgrep(df, "pattern")
```

**Best for:** Simple scripts, one-off searches, maximum compatibility.

### Method 2: Pipe Method

Use with pandas/polars `.pipe()` for functional-style data pipelines:

```python
result = df.pipe(nwgrep, "pattern")

# Beautiful chaining
result = (
    df
    .pipe(nwgrep, "active")
    .pipe(nwgrep, "example.com", columns=["email"])
    .pipe(lambda x: x.sort_values('name'))
)
```

**Best for:** Data pipelines, functional programming style, method chaining.

### Method 3: Accessor Method

Register `.grep()` as a dataframe method for the cleanest syntax:

```python
from nwgrep import register_grep_accessor

# Register once at the start of your script/notebook
register_grep_accessor()

# Now use .grep() directly
result = df.grep("active")
result = df.grep("ACTIVE", case_sensitive=False)
result = df.grep("pattern", columns=["email"])
```

**Best for:** Interactive use (notebooks), frequent searching, cleanest syntax.

!!! note
    The accessor method works with both pandas and polars DataFrames.

### Method 4: Narwhals Native

Work directly with Narwhals objects in backend-agnostic code:

```python
import narwhals as nw
from nwgrep import nwgrep

# Accept any backend
def process_data(df_native):
    df = nw.from_native(df_native)
    result = nwgrep(df, "pattern")
    return nw.to_native(result)

# Works with pandas
import pandas as pd
df_pandas = pd.DataFrame({"col": ["a", "b"]})
result = process_data(df_pandas)

# Works with polars
import polars as pl
df_polars = pl.DataFrame({"col": ["a", "b"]})
result = process_data(df_polars)
```

**Best for:** Library code, backend-agnostic functions, writing reusable components.

## Working with Different Backends

nwgrep works seamlessly across all backends:

=== "pandas"

    ```python
    import pandas as pd
    from nwgrep import nwgrep
    
    df = pd.DataFrame({"col": ["foo", "bar", "baz"]})
    result = nwgrep(df, "ba")
    # Returns pandas DataFrame
    ```

=== "polars (eager)"

    ```python
    import polars as pl
    from nwgrep import nwgrep
    
    df = pl.DataFrame({"col": ["foo", "bar", "baz"]})
    result = nwgrep(df, "ba")
    # Returns polars DataFrame
    ```

=== "polars (lazy)"

    ```python
    import polars as pl
    from nwgrep import nwgrep
    
    # LazyFrame - no computation until .collect()
    df = pl.scan_parquet("data.parquet")
    result = nwgrep(df, "ba")
    # Returns polars LazyFrame
    
    # Collect when ready
    final = result.collect()
    ```

=== "daft (lazy)"

    ```python
    import daft
    from nwgrep import nwgrep
    
    df = daft.read_parquet("data.parquet")
    result = nwgrep(df, "ba")
    # Returns daft DataFrame (lazy)
    
    result.show()  # Trigger computation
    ```

=== "pyarrow"

    ```python
    import pyarrow as pa
    from nwgrep import nwgrep
    
    df = pa.table({"col": ["foo", "bar", "baz"]})
    result = nwgrep(df, "ba")
    # Returns pyarrow Table
    ```

## Advanced Examples

### Email Domain Search

```python
df = pd.DataFrame({
    "user": ["alice", "bob", "charlie"],
    "email": ["alice@gmail.com", "bob@company.com", "charlie@gmail.com"]
})

# Find all Gmail users
gmail_users = nwgrep(df, "gmail.com", columns=["email"])
```

### Log File Analysis

```python
df = pd.DataFrame({
    "timestamp": ["2024-01-01", "2024-01-01", "2024-01-02"],
    "level": ["INFO", "ERROR", "WARN"],
    "message": ["Started", "Connection failed", "Slow query"]
})

# Find all errors and warnings
issues = nwgrep(df, ["ERROR", "WARN"], columns=["level"])

# Find connection-related messages
conn_logs = nwgrep(df, "connection", case_sensitive=False)
```

### Data Quality Checks

```python
# Find rows with email addresses (regex)
has_email = nwgrep(df, r"\w+@\w+\.\w+", regex=True)

# Find rows without phone numbers (invert)
no_phone = nwgrep(df, r"\d{3}-\d{3}-\d{4}", regex=True, invert=True)
```

### Complex Pipeline

```python
from nwgrep import register_grep_accessor
register_grep_accessor()

# Chain multiple operations
result = (
    df
    .grep("active", columns=["status"])      # Only active users
    .grep("@company.com", columns=["email"]) # Company emails
    .grep("admin", invert=True)              # Exclude admins
    .sort_values("name")                     # Sort by name
    .reset_index(drop=True)
)
```

## Performance Tips

### Use Column Filtering

When you know which columns contain your data, specify them:

```python
# Faster - only searches email column
result = nwgrep(df, "example.com", columns=["email"])

# Slower - searches all columns
result = nwgrep(df, "example.com")
```

### Leverage Lazy Evaluation

With polars or daft, use lazy frames for better performance:

```python
import polars as pl

# Lazy - builds query plan, executes once
df = (
    pl.scan_parquet("huge_file.parquet")
    .pipe(nwgrep, "pattern")
    .collect()
)
```

### Choose the Right Backend

Different backends excel at different tasks:

- **pandas**: Best for small-medium data, interactive work
- **polars**: Best for large data, complex transformations
- **dask**: Best for data larger than memory, distributed computing
- **cuDF**: Best when you have GPU acceleration available

## Common Patterns

### Quick Data Exploration

```python
from nwgrep import register_grep_accessor
register_grep_accessor()

# Quick searches in notebooks
df.grep("TODO")         # Find TODO items
df.grep("@")            # Find rows with email addresses
df.grep("error", case_sensitive=False)  # Find errors
```

### Data Cleaning

```python
# Remove test/dummy data
clean_df = df.pipe(nwgrep, "test", invert=True)

# Keep only valid email addresses
valid_emails = df.pipe(
    nwgrep,
    r"^[\w\.-]+@[\w\.-]+\.\w+$",
    regex=True,
    columns=["email"]
)
```

### Filtering Pipelines

```python
def filter_active_users(df):
    return df.pipe(nwgrep, "active", columns=["status"])

def filter_premium(df):
    return df.pipe(nwgrep, "premium", columns=["tier"])

# Compose filters
result = (
    raw_data
    .pipe(filter_active_users)
    .pipe(filter_premium)
)
```

## Next Steps

- [API Reference](api.md) - Complete parameter documentation
- [CLI Reference](cli.md) - Command-line usage
- [Contributing](contributing.md) - Help improve nwgrep
