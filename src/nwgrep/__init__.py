from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from nwgrep.accessor import register_grep_accessor
from nwgrep.core import nwgrep

try:
    __version__ = version("nwgrep")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Package not installed
__all__ = ["nwgrep", "register_grep_accessor"]
