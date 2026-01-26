"""Check that basic features work after packaging.

Catch cases where e.g. files are missing so the import doesn't work.
"""

from __future__ import annotations

import subprocess
import sys

import nwgrep
from nwgrep import nwgrep as nwgrep_func

# 1. Check version
print(f"nwgrep version: {nwgrep.__version__}")
if not nwgrep.__version__:
    raise RuntimeError("nwgrep version is empty")

# 2. Check that we can import main components
try:
    from nwgrep import register_grep_accessor

    print("Successfully imported register_grep_accessor")
except ImportError as e:
    raise RuntimeError(f"Failed to import register_grep_accessor: {e}") from e

# 3. Basic CLI help check
try:
    subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "--help"], check=True, capture_output=True
    )
    print("CLI help check succeeded")
except subprocess.CalledProcessError as e:
    raise RuntimeError(f"CLI help check failed: {e.stderr.decode()}") from e

# 4. Functional check if a backend is available
try:
    import pandas as pd

    df = pd.DataFrame({"a": ["foo", "bar"], "b": ["baz", "qux"]})
    result = nwgrep_func(df, "foo")

    # In pandas, result should be a DataFrame
    if len(result) == 1 and result.iloc[0, 0] == "foo":
        print("Functional smoke test with pandas succeeded")
    else:
        raise RuntimeError(f"Functional smoke test failed. Result: {result}")
except ImportError:
    print("Pandas not available, skipping functional smoke test")

print("Smoke test succeeded")
