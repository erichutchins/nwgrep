# Installation

## Basic Installation

Install nwgrep using uv (recommended) or pip:

=== "uv"

    ```bash
    uv add nwgrep
    ```

=== "pip"

    ```bash
    pip install nwgrep
    ```

!!! note
    The basic installation includes only the core nwgrep library and Narwhals. You'll need to install at least one dataframe backend separately.

## With Dataframe Backends

Install nwgrep with your preferred dataframe backend(s):

=== "pandas"

    ```bash
    uv add nwgrep[pandas]
    # or
    pip install nwgrep[pandas]
    ```

=== "polars"

    ```bash
    uv add nwgrep[polars]
    # or
    pip install nwgrep[polars]
    ```

=== "pyarrow"

    ```bash
    uv add nwgrep[pyarrow]
    # or
    pip install nwgrep[pyarrow]
    ```

=== "dask"

    ```bash
    uv add nwgrep[dask]
    # or
    pip install nwgrep[dask]
    ```

=== "daft"

    ```bash
    uv add nwgrep[daft]
    # or
    pip install nwgrep[daft]
    ```

=== "cuDF (GPU)"

    ```bash
    uv add nwgrep[cudf]
    # or
    pip install nwgrep[cudf]
    ```
    
    !!! warning
        cuDF is only available on Linux with Python 3.10-3.13 and requires CUDA-capable GPUs.

=== "All Backends"

    ```bash
    uv add nwgrep[all]
    # or
    pip install nwgrep[all]
    ```
    
    This installs pandas, polars, pyarrow, daft, dask, and duckdb.

## Command Line Interface

To use nwgrep from the command line for searching parquet/feather files:

```bash
uv add nwgrep[cli]
# or
pip install nwgrep[cli]
```

This includes polars for efficient lazy scanning of binary formats.

Then you can use:

```bash
nwgrep "pattern" datafile.parquet
```

## Development Installation

If you want to contribute or modify nwgrep:

```bash
# Clone the repository
git clone https://github.com/erichutchins/nwgrep.git
cd nwgrep

# Install with development dependencies
uv sync --group dev
```

This installs:

- Core testing backends (pandas, polars, pyarrow)
- Testing tools (pytest, pytest-cov)
- Linting and formatting tools (ruff, pre-commit)

See [Contributing](contributing.md) for more details on development setup.

## Backend Compatibility

nwgrep works with any backend supported by Narwhals:

| Backend | Status | Notes |
|---------|--------|-------|
| pandas | ✅ Full support | Tested with pandas >= 1.1.3 |
| polars | ✅ Full support | Supports both DataFrame and LazyFrame |
| pyarrow | ✅ Full support | - |
| daft | ✅ Full support | Supports lazy evaluation |
| dask | ✅ Full support | Distributed dataframes |
| modin | ✅ Full support | Parallel pandas |
| cuDF | ✅ Full support | GPU-accelerated (Linux only) |
| pyspark | ✅ Full support | - |
| duckdb | ✅ Full support | - |
| ibis | ✅ Full support | - |

## Verifying Installation

Test your installation:

```python
import nwgrep
import pandas as pd

df = pd.DataFrame({"col": ["hello", "world"]})
result = nwgrep.nwgrep(df, "hello")
print(result)
```

Expected output:

```
     col
0  hello
```

## Troubleshooting

### Import Errors

If you get an import error for a specific backend:

```python
ImportError: pandas is not installed
```

Install the missing backend:

```bash
uv add pandas  # or pip install pandas
```

### Type Checking

nwgrep includes full type hints. For the best type checking experience, use [ty (Red Knot)](https://docs.astral.sh/red-knot/):

```bash
uvx ty check your_script.py
```

## Next Steps

- [Usage Guide](usage.md) - Learn how to use nwgrep
- [API Reference](api.md) - Complete function reference
- [CLI Reference](cli.md) - Command-line usage
