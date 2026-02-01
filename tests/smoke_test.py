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

# 3. Basic CLI help check (optional - skip if CLI dependencies not installed)
try:
    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "--help"], check=False, capture_output=True
    )
    if result.returncode == 0:
        print("CLI help check succeeded")
    else:
        stderr = result.stderr.decode()
        # Check if this is a missing dependencies error (expected when testing without [cli])
        if "missing required dependencies" in stderr:
            print(
                "CLI dependencies not installed, skipping CLI test (expected for base install)"
            )
        else:
            msg = f"CLI help check failed unexpectedly: {stderr}"
            raise RuntimeError(msg)
except FileNotFoundError:
    print("CLI module not found, skipping CLI test")

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
