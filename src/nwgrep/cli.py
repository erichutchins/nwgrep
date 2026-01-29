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
        "-F",
        "--fixed-strings",
        action="store_true",
        help="Force literal string matching (disable regex)",
    )
    parser.add_argument(
        "-w", "--whole-word", action="store_true", help="Match whole words only"
    )
    parser.add_argument(
        "-x",
        "--exact",
        action="store_true",
        help="Exact match (equality or anchored regex)",
    )
    parser.add_argument(
        "-n",
        "--max-rows",
        type=int,
        default=None,
        help="Maximum number of rows to display",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Print count of matching rows instead of rows themselves",
    )
    parser.add_argument(
        "-l",
        "--files-with-matches",
        action="store_true",
        help="Print only filenames with matches (like grep -l)",
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


def _validate_flags(args: argparse.Namespace) -> bool:
    """Validate flag combinations and determine final regex mode.

    Returns the final regex mode after resolving flag conflicts.
    """
    # Check for incompatible flag combinations
    if args.fixed_strings and args.whole_word:
        print(
            "Error: -F/--fixed-strings and -w/--whole-word are incompatible",
            file=sys.stderr,
        )
        print("Whole-word matching requires regex boundaries (\\b)", file=sys.stderr)
        sys.exit(1)

    # Warn if both -F and -E are specified
    if args.fixed_strings and args.regex:
        print("Warning: -F/--fixed-strings overrides -E/--regex flag", file=sys.stderr)

    # Determine final regex mode based on priority: -F > -w > -E > default
    if args.fixed_strings:
        return False  # Force literal
    if args.whole_word:
        return True  # Whole-word requires regex
    return args.regex  # Use -E flag


def _output_dataframe(df: pl.DataFrame, args: argparse.Namespace) -> None:
    """Output a dataframe in the requested format."""
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


def _output_files_with_matches(
    result: pl.LazyFrame | pl.DataFrame, args: argparse.Namespace, file_path: Path
) -> None:
    """Handle files-with-matches output (-l flag)."""
    if args.format != "table":
        print(
            "Warning: --format ignored when using -l/--files-with-matches",
            file=sys.stderr,
        )
    # Check if there are any matches (short-circuit on first match)
    has_matches = (
        result.limit(1).collect().height > 0
        if isinstance(result, pl.LazyFrame)
        else len(result) > 0
    )
    if has_matches:
        print(file_path)


def _output_results(
    result: pl.LazyFrame | pl.DataFrame | int, args: argparse.Namespace, file_path: Path
) -> None:
    """Handle printing or streaming the filtered results."""
    # Handle count output (just print the integer)
    if isinstance(result, int):
        if args.format != "table":
            print("Warning: --format ignored when using --count", file=sys.stderr)
        print(result)
        return

    # Handle files-with-matches output
    if args.files_with_matches:
        _output_files_with_matches(result, args, file_path)
        return

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

    _output_dataframe(df, args)


def main() -> None:
    """Command-line interface for nwgrep."""
    _check_polars()

    parser = _create_parser()
    args = parser.parse_args()

    # Validate flags and get final regex mode
    final_regex = _validate_flags(args)

    file_path = Path(args.file)
    df = _load_file(file_path)

    columns = args.columns.split(",") if args.columns else None

    try:
        # Use nwgrep with polars LazyFrame, get back polars (or int if count)
        result = nwgrep(
            df,
            args.pattern,
            columns=columns,
            case_sensitive=not args.ignore_case,
            regex=final_regex,
            invert=args.invert,
            whole_word=args.whole_word,
            count=args.count,
            exact=args.exact,
        )
        _output_results(result, args, file_path)
    except (ValueError, RuntimeError, OSError) as e:
        print(f"Error during search: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
