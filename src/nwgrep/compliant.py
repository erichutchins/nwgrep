from __future__ import annotations

from typing import TYPE_CHECKING, Any

import narwhals as nw
from narwhals.compliant import (
    CompliantDataFrame,
    CompliantExpr,
    CompliantLazyFrame,
    CompliantNamespace,
)

if TYPE_CHECKING:
    from narwhals.utils import Version


class GrepLazyFrame(CompliantLazyFrame):
    def __init__(self, df: Any, version: Version) -> None:
        self._df = df
        self._version = version

    def __narwhals_lazyframe__(self) -> Any:
        return self

    def collect(self) -> GrepDataFrame:
        return GrepDataFrame(self._df.collect(), version=self._version)


class GrepDataFrame(CompliantDataFrame):
    def __init__(self, df: Any, version: Version) -> None:
        self._df = df
        self._version = version

    def __narwhals_dataframe__(self) -> Any:
        return self

    def lazy(self) -> GrepLazyFrame:
        return GrepLazyFrame(self._df.lazy(), version=self._version)


class GrepNamespace(CompliantNamespace[GrepLazyFrame, CompliantExpr]):
    def __init__(self, *, version: Version) -> None:
        self._version = version

    def from_native(self, native_object: Any) -> GrepLazyFrame:
        # Wrap the native object into a Narwhals frame, then wrap that into our compliant frame
        nw_frame = nw.from_native(native_object, version=self._version).lazy()
        return GrepLazyFrame(nw_frame, version=self._version)


def __narwhals_namespace__(version: Version) -> GrepNamespace:  # noqa: N807
    return GrepNamespace(version=version)


def is_native(obj: Any) -> bool:
    return isinstance(obj, (GrepLazyFrame, GrepDataFrame))


NATIVE_PACKAGE = "nwgrep"
