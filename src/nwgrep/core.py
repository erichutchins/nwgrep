from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal, overload

import narwhals as nw

if TYPE_CHECKING:
    from collections.abc import Sequence

    from great_tables import GT
    from narwhals.typing import FrameT
    from pandas.io.formats.style import Styler


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
    """Build a match expression for a single column and pattern.

    Consolidates exact, regex, and literal matching with unified case-handling.
    """
    # For regex mode, use regex flags for case-insensitivity instead of lowercasing
    # (lowercasing the pattern breaks character classes like [A-Z])
    if regex:
        if exact:
            # Wrap pattern with anchors for exact regex matching
            anchored_pattern = f"^(?:{pat})$"
            # Use (?i) flag for case-insensitive matching
            final_pattern = (
                anchored_pattern if case_sensitive else f"(?i){anchored_pattern}"
            )
            return expr.str.contains(final_pattern, literal=False)
        # Regular regex matching
        # Use (?i) flag for case-insensitive matching
        final_pattern = pat if case_sensitive else f"(?i){pat}"
        return expr.str.contains(final_pattern, literal=False)

    # For non-regex (literal/exact fixed strings), normalize to lowercase
    search_expr = expr if case_sensitive else expr.str.to_lowercase()
    search_pat = pat if case_sensitive else pat.lower()

    if exact:
        # Use equality for exact fixed string matching
        return search_expr == search_pat
    # Literal string matching (default)
    return search_expr.str.contains(search_pat, literal=True)


def _build_match_expr(
    search_cols: list[str],
    patterns: list[str],
    *,
    case_sensitive: bool,
    regex: bool,
    exact: bool,
) -> nw.Expr:
    """Build matching expression: any(pattern) matches any(column)."""
    # Flatten matching logic into a single list of candidate expressions.
    # Since we want to know if ANY pattern matches ANY column, a flat list
    # of all combinations combined with OR is mathematically equivalent
    # to the nested OR logic.
    exprs = [
        _build_column_match(
            nw.col(col), pat, case_sensitive=case_sensitive, regex=regex, exact=exact
        )
        for pat in patterns
        for col in search_cols
    ]

    # Fast-path: If there's only one pattern and one column, avoid any_horizontal overhead.
    if len(exprs) == 1:
        return exprs[0]

    return nw.any_horizontal(*exprs, ignore_nulls=True)


def _apply_highlighting_to_result(
    result: nw.LazyFrame,
    *,
    result_is_lazy: bool,
    patterns: list[str],
    case_sensitive: bool,
    regex: bool,
    exact: bool,
    search_cols: list[str],
) -> Styler | GT:
    """Handle all highlighting logic.

    Note: result_is_lazy is a keyword-only boolean parameter that tracks whether
    the original input was lazy. This is an internal implementation detail for
    determining collection behavior, not a user-facing configuration option.
    """
    # Always collect if lazy (highlighting requires materialized data)
    if result_is_lazy:
        result_collected = result.collect()
    else:
        result_collected = (
            result.collect() if isinstance(result, nw.LazyFrame) else result
        )

    # Convert to native
    native_df = nw.to_native(result_collected, pass_through=True)

    # Construct highlighting config at this layer
    from nwgrep.highlight import HighlightConfig, apply_highlighting

    config = HighlightConfig(
        patterns=patterns,
        case_sensitive=case_sensitive,
        regex=regex,
        exact=exact,
        search_cols=search_cols,
    )

    return apply_highlighting(native_df, config)


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
    highlight: Literal[False] = False,
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
    highlight: Literal[True],
) -> Styler | GT: ...


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
    highlight: Literal[False] = False,
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
) -> FrameT | int | Styler | GT:
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
    if isinstance(nw_frame, nw.LazyFrame):
        result_is_lazy = True
        df_nw = nw_frame
    elif isinstance(nw_frame, nw.DataFrame):
        result_is_lazy = False
        df_nw = nw_frame.lazy()
    else:
        # This branch should ideally not be reached if FrameT is correctly defined
        # as DataFrame | LazyFrame, but it's good for robustness.
        msg = f"Expected DataFrame or LazyFrame, got {type(nw_frame)}"
        raise TypeError(msg)

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
        # .item() returns the scalar value. We know nw.len() returns an integer.
        # Cast to int to satisfy the type checker and handle backend-specific int types.
        count_value = result.select(nw.len()).collect().item()
        return int(count_value)  # type: ignore[arg-type]

    # Handle highlighting
    if highlight:
        return _apply_highlighting_to_result(
            result,
            result_is_lazy=result_is_lazy,
            patterns=patterns,
            case_sensitive=case_sensitive,
            regex=regex,
            exact=exact,
            search_cols=search_cols,
        )

    # Return in the same format as input (Narwhals or native)
    return nw.to_native(
        result if result_is_lazy else result.collect(), pass_through=True
    )
