from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


class GrepAccessor:
    """Accessor class that provides .grep() method to dataframes."""

    def __init__(self, df: Any) -> None:
        self._df = df

    def __call__(
        self,
        pattern: str | Sequence[str],
        *,
        columns: Sequence[str] | None = None,
        case_sensitive: bool = True,
        regex: bool = False,
        fixed_strings: bool = False,
        invert: bool = False,
        whole_word: bool = False,
        count: bool = False,
        exact: bool = False,
    ) -> Any:
        """Search for pattern in any column and return matching rows.

        This is a convenience method that wraps nwgrep.core.nwgrep.
        See nwgrep.nwgrep for full documentation.

        Examples:
        --------
        >>> import pandas as pd
        >>> from nwgrep import register_grep_accessor
        >>> register_grep_accessor()
        >>> df = pd.DataFrame(
        ...     {"name": ["Alice", "Bob"], "status": ["active", "locked"]}
        ... )
        >>> df.grep("active")
            name  status
        0  Alice  active
        """
        from nwgrep.core import nwgrep

        # Validate flag combinations
        if fixed_strings and whole_word:
            msg = (
                "-F/--fixed-strings and -w/--whole-word are incompatible. "
                "Whole-word matching requires regex boundaries."
            )
            raise ValueError(msg)

        # Determine final regex mode based on priority: fixed_strings > whole_word > regex
        final_regex = regex
        if fixed_strings:
            final_regex = False  # Force literal
        elif whole_word:
            final_regex = True  # Whole-word requires regex

        return nwgrep(
            self._df,
            pattern,
            columns=columns,
            case_sensitive=case_sensitive,
            regex=final_regex,
            invert=invert,
            whole_word=whole_word,
            count=count,
            exact=exact,
        )


def register_grep_accessor() -> None:
    """Register .grep accessor for pandas and polars DataFrames.

    After calling this function, you can use df.grep("pattern") directly
    on pandas and polars dataframes.

    Examples:
    --------
    >>> from nwgrep import register_grep_accessor
    >>> register_grep_accessor()
    >>> import pandas as pd
    >>> df = pd.DataFrame({"col": ["foo", "bar"]})
    >>> df.grep("foo")
       col
    0  foo
    """
    # Try to register for pandas
    try:
        import pandas as pd

        if not hasattr(pd.DataFrame, "grep"):

            @pd.api.extensions.register_dataframe_accessor("grep")
            class PandasGrepAccessor(GrepAccessor):
                pass

    except ImportError:
        pass

    # Try to register for polars
    try:
        import polars as pl

        if not hasattr(pl.DataFrame, "grep"):

            @pl.api.register_dataframe_namespace("grep")
            class PolarsGrepAccessor(GrepAccessor):
                pass

        if not hasattr(pl.LazyFrame, "grep"):

            @pl.api.register_lazyframe_namespace("grep")
            class PolarsLazyGrepAccessor(GrepAccessor):
                pass

    except (ImportError, AttributeError):
        # polars.api might not exist in older versions
        pass
