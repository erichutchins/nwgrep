from __future__ import annotations

import pandas as pd

from nwgrep import nwgrep, register_grep_accessor

# 1. Using nwgrep via .pipe() (Recommended for clean functional chains)
df = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Eve"],
        "status": ["active", "locked", "active"],
        "notes": ["loves narwhals", "prefers pandas", "active contributor"],
    }
)

print("--- Filtered using .pipe(nwgrep, ...) ---")
# Search for 'active' in any column
filtered_pipe = df.pipe(nwgrep, "active")
print(filtered_pipe)
print()

# 2. Using the registered accessor
register_grep_accessor()

print("--- Filtered using df.grep(...) accessor ---")
# Case-insensitive search across specific columns
filtered_accessor = df.grep("NARWHALS", case_sensitive=False, columns=["notes"])
print(filtered_accessor)
