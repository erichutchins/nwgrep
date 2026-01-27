from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from nwgrep.core import nwgrep

if TYPE_CHECKING:
    import polars as pl

try:
    import polars as pl

    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False


def _create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Grep for binary dataframes (Parquet, Feather, IPC) - search rows across any column.\n"
            "Requires polars: pip install 'nwgrep[cli]'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nwgrep "error" data.parquet
  nwgrep -i "warning" data.feather
  nwgrep -v "success" data.ipc
  nwgrep -E "err(or|!)?" data.parquet
  nwgrep --columns name,email "alice" data.parquet --format ndjson
        """,
    )
    parser.add_argument("pattern", help="Search pattern")
    parser.add_argument(
        "file", help="Binary dataframe file to search (Parquet, Feather, IPC)"
    )
    parser.add_argument(
        "-c",
        "--columns",
        help="Comma-separated list of columns to search",
        default=None,
    )
    parser.add_argument(
        "-i", "--ignore-case", action="store_true", help="Case insensitive matching"
    )
    parser.add_argument(
        "-v", "--invert", action="store_true", help="Invert match (show non-matching)"
    )
    parser.add_argument(
        "-E", "--regex", action="store_true", help="Treat pattern as regex"
    )
    parser.add_argument(
        "-w", "--whole-word", action="store_true", help="Match whole words only"
    )
    parser.add_argument(
        "-n",
        "--max-rows",
        type=int,
        default=None,
        help="Maximum number of rows to display",
    )
    parser.add_argument(
        "--format",
        choices=["table", "csv", "tsv", "ndjson"],
        default="table",
        help="Output format (default: table)",
    )
    return parser


def _check_polars() -> None:
    """Check that polars is installed, exit with helpful message if not."""
    if not HAS_POLARS:
        print(
            "Error: The nwgrep CLI requires polars.\n"
            "Install it with: pip install 'nwgrep[cli]'",
            file=sys.stderr,
        )
        sys.exit(1)


def _load_file(file_path: Path) -> pl.LazyFrame:
    """Load a binary dataframe file using polars lazy scanning."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        sys.exit(1)

    suffix = file_path.suffix.lower()
    try:
        if suffix == ".parquet":
            return pl.scan_parquet(file_path)
        if suffix in {".feather", ".arrow", ".ipc"}:
            return pl.scan_ipc(file_path)

        print(
            f"Error: Unsupported or non-binary file type '{suffix}'.\n"
            "nwgrep CLI supports: .parquet, .feather, .arrow, .ipc\n"
            "For text files (CSV, TSV, TXT), use standard 'grep' or 'ripgrep'.",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def _output_results(
    result: pl.LazyFrame | pl.DataFrame, args: argparse.Namespace
) -> None:
    """Handle printing or streaming the filtered results."""
    # Handle NDJSON streaming for LazyFrame
    if (
        args.format == "ndjson"
        and isinstance(result, pl.LazyFrame)
        and not args.max_rows
    ):
        result.sink_ndjson(sys.stdout)
        return

    # Collect if lazy
    df: pl.DataFrame = result.collect() if isinstance(result, pl.LazyFrame) else result

    # Limit rows if requested
    if args.max_rows:
        df = df.head(args.max_rows)

    # Output in requested format
    if args.format == "csv":
        print(df.write_csv())
    elif args.format == "tsv":
        print(df.write_csv(separator="\t"))
    elif args.format == "ndjson":
        buf = io.BytesIO()
        df.write_ndjson(buf)
        print(buf.getvalue().decode("utf-8").strip())
    else:  # table
        print(df)


def main() -> None:
    """Command-line interface for nwgrep."""
    _check_polars()

    parser = _create_parser()
    args = parser.parse_args()

    file_path = Path(args.file)
    df = _load_file(file_path)

    columns = args.columns.split(",") if args.columns else None

    try:
        # Use nwgrep with polars LazyFrame, get back polars
        result = nwgrep(
            df,
            args.pattern,
            columns=columns,
            case_sensitive=not args.ignore_case,
            regex=args.regex,
            invert=args.invert,
            whole_word=args.whole_word,
        )
        _output_results(result, args)
    except (ValueError, RuntimeError, OSError) as e:
        print(f"Error during search: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
