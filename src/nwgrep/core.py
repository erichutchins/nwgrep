from __future__ import annotations

from typing import TYPE_CHECKING

import narwhals as nw

if TYPE_CHECKING:
    from collections.abc import Sequence

    from narwhals.typing import FrameT


def _get_search_columns(df: nw.LazyFrame, columns: Sequence[str] | None) -> list[str]:
    """Determine which columns to search."""
    schema = df.collect_schema()
    if columns:
        return list(columns)

    # Search all string-like columns
    return [
        col_name
        for col_name, dtype in schema.items()
        if dtype in {nw.String, nw.Categorical}
    ]


def _build_match_expr(
    search_cols: list[str],
    patterns: list[str],
    *,
    case_sensitive: bool,
    regex: bool,
) -> list[nw.Expr]:
    """Build matching expressions for each pattern."""
    match_exprs = []
    for pat in patterns:
        col_matches = []
        for col in search_cols:
            expr = nw.col(col)
            null_check = expr.is_null()

            if regex:
                if case_sensitive:
                    match = expr.str.contains(pat, literal=False)
                else:
                    match = expr.str.to_lowercase().str.contains(
                        pat.lower(), literal=False
                    )
            elif case_sensitive:
                match = expr.str.contains(pat, literal=True)
            else:
                match = expr.str.to_lowercase().str.contains(pat.lower(), literal=True)

            col_matches.append(match & ~null_check)

        if col_matches:
            match_exprs.append(nw.any_horizontal(*col_matches, ignore_nulls=True))
    return match_exprs


def nwgrep(
    df: FrameT,
    pattern: str | Sequence[str],
    *,
    columns: Sequence[str] | None = None,
    case_sensitive: bool = True,
    regex: bool = False,
    invert: bool = False,
    whole_word: bool = False,
) -> FrameT:
    """Grep-like filtering for dataframes across any backend.

    Parameters
    ----------
    df : DataFrame or LazyFrame
        Input dataframe (pandas, polars, daft, etc.)
    pattern : str or list of str
        Search pattern(s) to match
    columns : list of str, optional
        Specific columns to search. If None, searches all string columns
    case_sensitive : bool, default True
        Whether matching should be case sensitive
    regex : bool, default False
        Whether to treat pattern as regex
    invert : bool, default False
        Return rows that DON'T match (like grep -v)
    whole_word : bool, default False
        Match whole words only (implies regex=True)

    Returns:
    -------
    DataFrame or LazyFrame
        Filtered dataframe with matching rows (same type as input)

    Examples:
    --------
    >>> import narwhals as nw
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "name": ["Alice", "Bob", "Eve"],
    ...     "status": ["active", "locked", "active"],
    ... })
    >>> nwgrep(df, "active")  # Find rows with "active" in any column
       name  status
    0  Alice  active
    2    Eve  active

    >>> # Works great with .pipe()
    >>> df.pipe(nwgrep, "active")
       name  status
    0  Alice  active
    2    Eve  active

    >>> nwgrep(df, "active", invert=True)  # Rows without "active"
      name  status
    1  Bob  locked

    >>> nwgrep(df, ["Alice", "Bob"])  # Multiple patterns
        name  status
    0  Alice  active
    1    Bob  locked
    """
    # Detect if we already have a Narwhals object
    is_narwhals = isinstance(df, (nw.DataFrame, nw.LazyFrame))

    # Convert to narwhals lazy frame for efficient processing
    if is_narwhals:
        # result_is_lazy is True if the input was already a LazyFrame
        result_is_lazy = isinstance(df, nw.LazyFrame)
        df_nw = df.lazy()
    else:
        # For native, detect if it's lazy by wrapping it first
        nw_temp = nw.from_native(df)
        result_is_lazy = isinstance(nw_temp, nw.LazyFrame)
        df_nw = nw_temp.lazy()

    # Convert single pattern to list
    patterns = [pattern] if isinstance(pattern, str) else list(pattern)

    # Determine which columns to search
    search_cols = _get_search_columns(df_nw, columns)

    if not search_cols:
        # No searchable columns, return empty or full based on invert
        result = df_nw.filter(nw.lit(invert))
        if is_narwhals:
            return result if result_is_lazy else result.collect()
        return nw.to_native(result if result_is_lazy else result.collect())

    # Adjust pattern for whole word matching
    if whole_word:
        patterns = [rf"\b{pat}\b" for pat in patterns]
        regex = True

    # Build matching expressions for each pattern
    match_exprs = _build_match_expr(
        search_cols, patterns, case_sensitive=case_sensitive, regex=regex
    )

    if not match_exprs:
        # No valid expressions, return based on invert
        result = df_nw.filter(nw.lit(invert))
    else:
        # Any pattern matches (OR logic across patterns)
        if len(match_exprs) == 1:
            final_match = match_exprs[0]
        else:
            final_match = nw.any_horizontal(*match_exprs, ignore_nulls=True)

        # Invert if requested (grep -v)
        if invert:
            final_match = ~final_match

        result = df_nw.filter(final_match)

    # Return as Narwhals if input was Narwhals
    if is_narwhals:
        # We can return our own compliant frame if we wanted to follow the protocol strictly
        # But returning Narwhals' own frames is better for compatibility.
        return result if result_is_lazy else result.collect()

    # Otherwise return as native
    return nw.to_native(result if result_is_lazy else result.collect())


grep = nwgrep
