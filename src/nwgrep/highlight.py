from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import narwhals as nw

from nwgrep.core import _build_column_match, _get_search_columns


@dataclass
class HighlightConfig:
    """Configuration for highlighting matching cells."""

    patterns: list[str]
    case_sensitive: bool
    regex: bool
    exact: bool
    search_cols: list[str] | None


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
    df_native: Any, config: HighlightConfig
) -> dict[str, list[bool]]:
    """Build a mask of cells containing matches using Narwhals."""
    # Convert to Narwhals LazyFrame
    nw_frame = nw.from_native(df_native, pass_through=True)
    df_nw = nw_frame.lazy()

    # Determine columns to search
    cols_to_check = _get_search_columns(df_nw, config.search_cols)

    if not cols_to_check:
        return {}

    def build_column_mask(col: str) -> nw.Expr:
        """Build OR expression across all patterns for a column."""
        col_expr = nw.col(col)
        pattern_matches = [
            _build_column_match(
                col_expr,
                pat,
                case_sensitive=config.case_sensitive,
                regex=config.regex,
                exact=config.exact,
            )
            & ~col_expr.is_null()
            for pat in config.patterns
        ]
        return nw.any_horizontal(*pattern_matches, ignore_nulls=True).alias(col)

    # Build mask expression for each column
    select_exprs = [build_column_mask(col) for col in cols_to_check]

    if not select_exprs:
        return {}

    # Execute the query to get boolean dataframe
    mask_df = df_nw.select(select_exprs).collect()

    # Convert to native dictionary of lists
    return mask_df.to_dict(as_series=False)


def _highlight_pandas_dataframe(df: Any, config: HighlightConfig) -> Any:
    """Highlight matching cells in a pandas DataFrame with yellow background."""
    # Get mask of matching cells
    mask = _get_matching_mask_dict(df, config)

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


def _highlight_polars_dataframe(df: Any, config: HighlightConfig) -> Any:
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
    mask = _get_matching_mask_dict(df, config)

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


def apply_highlighting(df_native: Any, config: HighlightConfig) -> Any:
    """Apply cell-level highlighting based on the dataframe backend."""
    backend = _detect_backend(df_native)
    match backend:
        case "pandas":
            return _highlight_pandas_dataframe(df_native, config)
        case "polars":
            return _highlight_polars_dataframe(df_native, config)
        case _:
            msg = f"Highlighting not supported for backend: {backend}"
            raise ValueError(msg)
