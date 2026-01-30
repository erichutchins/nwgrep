from __future__ import annotations

from typing import Any

import narwhals as nw

from nwgrep.core import _build_column_match, _get_search_columns


def _detect_backend(df_native: Any) -> str:
    """Detect the dataframe backend (pandas, polars, or other)."""
    module = type(df_native).__module__
    if not module:
        return "unsupported"
    base_module = module.partition(".")[0]
    if base_module == "pandas":
        return "pandas"
    if base_module == "polars":
        return "polars"
    return "unsupported"


def _get_matching_mask_dict(
    df_native: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
    exact: bool,  # noqa: FBT001
    search_cols: list[str] | None,
) -> dict[str, list[bool]]:
    """Build a mask of cells containing matches using Narwhals."""
    # Convert to Narwhals LazyFrame
    nw_frame = nw.from_native(df_native, pass_through=True)
    df_nw = nw_frame.lazy()

    # Determine columns to search
    cols_to_check = _get_search_columns(df_nw, search_cols)

    if not cols_to_check:
        return {}

    # Build boolean expression for each column
    # For a cell to match, it must match ANY of the patterns
    select_exprs = []

    for col in cols_to_check:
        col_expr = nw.col(col)
        # Check against each pattern
        pattern_matches = []
        for pat in patterns:
            match = _build_column_match(
                col_expr, pat, case_sensitive=case_sensitive, regex=regex, exact=exact
            )
            # Match must be true and not null
            pattern_matches.append(match & ~col_expr.is_null())

        if pattern_matches:
            # Combine pattern matches with OR
            combined = nw.any_horizontal(*pattern_matches, ignore_nulls=True)
            select_exprs.append(combined.alias(col))
        else:
            select_exprs.append(nw.lit(False).alias(col))

    if not select_exprs:
        return {}

    # Execute the query to get boolean dataframe
    mask_df = df_nw.select(select_exprs).collect()

    # Convert to native dictionary of lists
    return mask_df.to_dict(as_series=False)


def _highlight_pandas_dataframe(
    df: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
    exact: bool,  # noqa: FBT001
    search_cols: list[str] | None,
) -> Any:
    """Highlight matching cells in a pandas DataFrame with yellow background."""
    # Get mask of matching cells
    mask = _get_matching_mask_dict(
        df, patterns, case_sensitive, regex, exact, search_cols
    )

    # Build a boolean dataframe for styling
    import pandas as pd

    style_mask = pd.DataFrame(False, index=df.index, columns=df.columns)
    for col, col_mask in mask.items():
        if col in style_mask.columns:
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
    exact: bool,  # noqa: FBT001
    search_cols: list[str] | None,
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
    mask = _get_matching_mask_dict(
        df, patterns, case_sensitive, regex, exact, search_cols
    )

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


def apply_highlighting(
    df_native: Any,
    patterns: list[str],
    case_sensitive: bool,  # noqa: FBT001
    regex: bool,  # noqa: FBT001
    exact: bool,  # noqa: FBT001
    search_cols: list[str] | None,
) -> Any:
    """Apply cell-level highlighting based on the dataframe backend."""
    backend = _detect_backend(df_native)
    if backend == "pandas":
        return _highlight_pandas_dataframe(
            df_native, patterns, case_sensitive, regex, exact, search_cols
        )
    if backend == "polars":
        return _highlight_polars_dataframe(
            df_native, patterns, case_sensitive, regex, exact, search_cols
        )
    msg = f"Highlighting not supported for backend: {backend}"
    raise ValueError(msg)
