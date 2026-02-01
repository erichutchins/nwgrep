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
    msg = "nwgrep version is empty"
    raise RuntimeError(msg)

# 2. Check that we can import main components
try:
    import importlib.util

    spec = importlib.util.find_spec("nwgrep.accessor")
    if spec is None:
        msg = "Failed to find nwgrep.accessor module"
        raise RuntimeError(msg)
    print("Successfully found nwgrep.accessor module")
except ImportError as e:
    msg = f"Failed to import nwgrep.accessor: {e}"
    raise RuntimeError(msg) from e

# 3. Basic CLI help check
try:
    subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "--help"], check=True, capture_output=True
    )
    print("CLI help check succeeded")
except subprocess.CalledProcessError as e:
    msg = f"CLI help check failed: {e.stderr.decode()}"
    raise RuntimeError(msg) from e

# 4. Functional check if a backend is available
try:
    import pandas as pd

    df = pd.DataFrame({"a": ["foo", "bar"], "b": ["baz", "qux"]})
    result = nwgrep_func(df, "foo")  # type: ignore[invalid-argument-type]

    # In pandas, result should be a DataFrame
    if len(result) == 1 and result.iloc[0, 0] == "foo":
        print("Functional smoke test with pandas succeeded")
    else:
        msg = f"Functional smoke test failed. Result: {result}"
        raise RuntimeError(msg)
except ImportError:
    print("Pandas not available, skipping functional smoke test")

print("Smoke test succeeded")
