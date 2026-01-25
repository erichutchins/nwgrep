from __future__ import annotations

from typing import TYPE_CHECKING

from nwgrep.accessor import register_grep_accessor
from nwgrep.core import grep, nwgrep

if TYPE_CHECKING:
    from narwhals.utils import Version

    from nwgrep.compliant import GrepNamespace

__version__ = "0.1.0"
__all__ = ["grep", "nwgrep", "register_grep_accessor"]

# Narwhals Plugin Protocol
NATIVE_PACKAGE = "nwgrep"


def is_native(_obj: object) -> bool:
    """Check if an object is native to nwgrep."""
    return False


def __narwhals_namespace__(version: Version) -> GrepNamespace:  # noqa: N807
    """Return a Narwhals-compliant namespace for nwgrep."""
    from nwgrep.compliant import GrepNamespace

    return GrepNamespace(version=version)
