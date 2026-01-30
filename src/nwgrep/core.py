from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal, overload

import narwhals as nw

if TYPE_CHECKING:
    from collections.abc import Sequence

    from narwhals.typing import FrameT


def _get_search_columns(df: nw.LazyFrame, columns: Sequence[str] | None) -> list[str]:
    """Determine which columns to search."""
    if columns:
        return list(columns)

    schema = df.collect_schema()

    # Search all string-like columns
    return [
        col_name
        for col_name, dtype in schema.items()
        if dtype in {nw.String, nw.Categorical}
    ]


def _build_column_match(
    expr: nw.Expr, pat: str, *, case_sensitive: bool, regex: bool, exact: bool
) -> nw.Expr:
    """Build a match expression for a single column and pattern."""
    if exact:
        return _build_exact_match(expr, pat, case_sensitive=case_sensitive, regex=regex)
    if regex:
        return _build_regex_match(expr, pat, case_sensitive=case_sensitive)
    return _build_literal_match(expr, pat, case_sensitive=case_sensitive)


def _build_exact_match(
    expr: nw.Expr, pat: str, *, case_sensitive: bool, regex: bool
) -> nw.Expr:
    """Build exact match expression (equality or anchored regex)."""
    if regex:
        # Wrap pattern with anchors for exact regex matching
        anchored_pattern = f"^(?:{pat})$"
        if case_sensitive:
            return expr.str.contains(anchored_pattern, literal=False)
        return expr.str.to_lowercase().str.contains(
            anchored_pattern.lower(), literal=False
        )
    # Use equality for exact fixed string matching
    if case_sensitive:
        return expr == pat
    return expr.str.to_lowercase() == pat.lower()


def _build_regex_match(expr: nw.Expr, pat: str, *, case_sensitive: bool) -> nw.Expr:
    """Build regex match expression."""
    if case_sensitive:
        return expr.str.contains(pat, literal=False)
    return expr.str.to_lowercase().str.contains(pat.lower(), literal=False)


def _build_literal_match(expr: nw.Expr, pat: str, *, case_sensitive: bool) -> nw.Expr:
    """Build literal string match expression."""
    if case_sensitive:
        return expr.str.contains(pat, literal=True)
    return expr.str.to_lowercase().str.contains(pat.lower(), literal=True)


def _build_match_expr(
    search_cols: list[str],
    patterns: list[str],
    *,
    case_sensitive: bool,
    regex: bool,
    exact: bool,
) -> nw.Expr:
    """Build matching expressions for each pattern."""
    exprs = []
    for pat in patterns:
        per_col = [
            _build_column_match(
                nw.col(c), pat, case_sensitive=case_sensitive, regex=regex, exact=exact
            )
            for c in search_cols
        ]
        exprs.append(nw.any_horizontal(*per_col, ignore_nulls=True))

    return nw.any_horizontal(*exprs, ignore_nulls=True)


@overload
def nwgrep(
    df: FrameT,
    pattern: str | Sequence[str],
    *,
    columns: Sequence[str] | None = None,
    case_sensitive: bool = True,
    regex: bool = False,
    invert: bool = False,
    whole_word: bool = False,
    count: Literal[True],
    exact: bool = False,
    highlight: bool = False,
) -> int: ...


@overload
def nwgrep(
    df: FrameT,
    pattern: str | Sequence[str],
    *,
    columns: Sequence[str] | None = None,
    case_sensitive: bool = True,
    regex: bool = False,
    invert: bool = False,
    whole_word: bool = False,
    count: Literal[False] = False,
    exact: bool = False,
    highlight: bool = False,
) -> FrameT: ...


def nwgrep(
    df: FrameT,
    pattern: str | Sequence[str],
    *,
    columns: Sequence[str] | None = None,
    case_sensitive: bool = True,
    regex: bool = False,
    invert: bool = False,
    whole_word: bool = False,
    count: bool = False,
    exact: bool = False,
    highlight: bool = False,
) -> FrameT | int:
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
    count : bool, default False
        Return count of matching rows instead of rows themselves
    exact : bool, default False
        Exact match - use equality for fixed strings, anchored regex otherwise
    highlight : bool, default False
        Highlight matching cells with yellow background (pandas/polars only, for notebooks)

    Returns:
    -------
    DataFrame, LazyFrame, or int
        If count=True: Integer count of matching rows
        Otherwise: Filtered dataframe with matching rows (same type as input)

    Examples:
    --------
    >>> import narwhals as nw
    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    ... )
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
    # Convert to Narwhals (pass through if already Narwhals)
    nw_frame = nw.from_native(df, pass_through=True)
    result_is_lazy = isinstance(nw_frame, nw.LazyFrame)
    df_nw = nw_frame.lazy()

    # Convert single pattern to list
    patterns = [pattern] if isinstance(pattern, str) else list(pattern)

    # Determine which columns to search
    search_cols = _get_search_columns(df_nw, columns)

    if not search_cols:
        # No searchable columns, return empty or full based on invert
        result = df_nw.filter(nw.lit(invert))
        return nw.to_native(
            result if result_is_lazy else result.collect(), pass_through=True
        )

    # Adjust pattern for whole word matching
    if whole_word:
        patterns = [rf"\b{re.escape(pat)}\b" for pat in patterns]
        regex = True

    # Build matching expressions for each pattern
    match_expr = _build_match_expr(
        search_cols, patterns, case_sensitive=case_sensitive, regex=regex, exact=exact
    )

    # Invert if requested (grep -v)
    mask = match_expr
    if invert:
        mask = ~mask

    result = df_nw.filter(mask)

    # If count requested, return integer count
    if count:
        if highlight:
            msg = "highlight and count parameters are incompatible"
            raise ValueError(msg)
        return int(result.select(nw.len()).collect().item())

    # Handle highlighting
    if highlight:
        # Always collect if lazy (highlighting requires materialized data)
        if result_is_lazy:
            result_collected = result.collect()
        else:
            result_collected = (
                result.collect() if isinstance(result, nw.LazyFrame) else result
            )

        # Convert to native
        native_df = nw.to_native(result_collected, pass_through=True)

        # Apply highlighting based on backend
        # Note: Patterns are transformed (e.g., by whole_word) and regex/exact flags
        # are updated accordingly, so we pass current values to matching logic.
        from nwgrep.highlight import apply_highlighting

        return apply_highlighting(
            native_df, patterns, case_sensitive, regex, exact, search_cols
        )

    # Return in the same format as input (Narwhals or native)
    return nw.to_native(
        result if result_is_lazy else result.collect(), pass_through=True
    )
