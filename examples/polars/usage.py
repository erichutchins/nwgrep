from __future__ import annotations

import narwhals as nw
import polars as pl

from nwgrep import nwgrep, register_grep_accessor

# 1. Functional usage with Polars DataFrame
df = pl.DataFrame(
    {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
)

print("--- Eager DataFrame via nwgrep(...) ---")
# Functional call returns a native Polars DataFrame
result_eager = nwgrep(df, "active")
print(result_eager)
print(f"Type: {type(result_eager)}")
print()

# 2. Accessor usage with Polars LazyFrame
register_grep_accessor()

# Create a LazyFrame
lf = pl.LazyFrame({"id": [1, 2, 3], "text": ["apple", "banana", "cherry"]})

print("--- LazyFrame via .grep() accessor ---")
# Accessor call on LazyFrame returns a native Polars LazyFrame
result_lazy = lf.grep("a")
print(f"Type: {type(result_lazy)}")

# Collect results
print("Collected results:")
print(result_lazy.collect())
print()

# 3. Mixing with Narwhals native objects
print("--- Usage with Narwhals-wrapped objects ---")
df_nw = nw.from_native(df)
# Passing a Narwhals object returns a Narwhals object
result_nw = nwgrep(df_nw, "active")
print(f"Type: {type(result_nw)}")
print(result_nw)
