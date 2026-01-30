from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Any

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
        anchored_pattern = f"^{pat}$"
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
) -> list[nw.Expr]:
    """Build matching expressions for each pattern."""
    match_exprs = []
    for pat in patterns:
        col_matches = []
        for col in search_cols:
            expr = nw.col(col)
            null_check = expr.is_null()

            match = _build_column_match(
                expr, pat, case_sensitive=case_sensitive, regex=regex, exact=exact
            )
            col_matches.append(match & ~null_check)

        if col_matches:
            match_exprs.append(nw.any_horizontal(*col_matches, ignore_nulls=True))
    return match_exprs


def _detect_backend(df_native: Any) -> str:
    """Detect the dataframe backend (pandas, polars, or other)."""
    module = type(df_native).__module__
    if module.startswith("pandas"):
        return "pandas"
    if module.startswith("polars"):
        return "polars"
    return "unsupported"


def _get_matching_cells(
    df_native: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
) -> dict[str, list[bool]]:
    """Build a mask of cells containing matches.

    Returns a dict mapping column names to lists of booleans indicating matches.
    """
    mask: dict[str, list[bool]] = {}

    # Get column names and data
    if isinstance(df_native.columns, list):  # polars
        col_names = df_native.columns
        col_data = {col: df_native[col].to_list() for col in col_names}
    else:  # pandas
        col_names = df_native.columns.tolist()
        col_data = {col: df_native[col].astype(str).tolist() for col in col_names}

    # For each column, check if cells match any pattern
    for col in col_names:
        col_mask = [
            _cell_matches_pattern(cell, patterns, case_sensitive, regex)
            for cell in col_data[col]
        ]
        mask[col] = col_mask

    return mask


def _cell_matches_pattern(
    cell_val: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
) -> bool:
    """Check if a cell value matches any of the patterns."""
    # Skip null/None values
    if cell_val is None or (isinstance(cell_val, float) and math.isnan(cell_val)):
        return False

    cell_str = str(cell_val)

    for pat in patterns:
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            if re.search(pat, cell_str, flags):
                return True
        elif case_sensitive:
            if pat in cell_str:
                return True
        elif pat.lower() in cell_str.lower():
            return True

    return False


def _highlight_pandas_dataframe(
    df: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
) -> Any:
    """Highlight matching cells in a pandas DataFrame with yellow background."""
    # Get mask of matching cells
    mask = _get_matching_cells(df, patterns, case_sensitive, regex)

    # Build a boolean dataframe for styling
    import pandas as pd

    style_mask = pd.DataFrame(False, index=df.index, columns=df.columns)
    for col, col_mask in mask.items():
        style_mask[col] = col_mask

    return df.style.apply(
        lambda row: [
            "background-color: #ffff99" if style_mask.loc[row.name, col] else ""
            for col in df.columns
        ],
        axis=1,
    )


def _highlight_polars_dataframe(
    df: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
) -> Any:
    """Highlight matching cells in a polars DataFrame using Great Tables."""
    try:
        from great_tables import GT, loc, style
    except ImportError as e:
        msg = (
            "Great Tables is required for polars highlighting. "
            "Install it with: pip install 'nwgrep[notebook]'"
        )
        raise ImportError(msg) from e

    # Get mask of matching cells
    mask = _get_matching_cells(df, patterns, case_sensitive, regex)

    # Build a boolean expression for matching cells
    gt = GT(df)

    # Apply highlighting to each matching cell
    for col, col_mask in mask.items():
        # Create a polars expression that evaluates to True for matching rows
        matching_rows = [i for i, matched in enumerate(col_mask) if matched]
        if matching_rows:
            gt = gt.tab_style(
                style=style.fill(color="#ffff99"),
                locations=loc.body(columns=col, rows=matching_rows),
            )

    return gt


def _apply_highlighting(
    df_native: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
) -> Any:
    """Apply cell-level highlighting based on the dataframe backend."""
    backend = _detect_backend(df_native)
    if backend == "pandas":
        return _highlight_pandas_dataframe(df_native, patterns, case_sensitive, regex)
    if backend == "polars":
        return _highlight_polars_dataframe(df_native, patterns, case_sensitive, regex)
    msg = f"Highlighting not supported for backend: {backend}"
    raise ValueError(msg)


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
) -> FrameT | int | Any:
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
        Highlight matching rows with yellow background (pandas/polars only, for notebooks)

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
        patterns = [rf"\b{pat}\b" for pat in patterns]
        regex = True

    # Build matching expressions for each pattern
    match_exprs = _build_match_expr(
        search_cols, patterns, case_sensitive=case_sensitive, regex=regex, exact=exact
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

    # If count requested, return integer count
    if count:
        if highlight:
            msg = "highlight and count parameters are incompatible"
            raise ValueError(msg)
        return result.collect().shape[0]

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
        return _apply_highlighting(native_df, patterns, case_sensitive, regex)

    # Return in the same format as input (Narwhals or native)
    return nw.to_native(
        result if result_is_lazy else result.collect(), pass_through=True
    )
