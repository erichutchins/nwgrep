from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import narwhals as nw

from nwgrep.core import nwgrep

if TYPE_CHECKING:
    from narwhals.typing import FrameT


def _create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Grep for binary dataframes (Parquet, Feather, IPC) - search rows across any column.\n"
            "Streaming NDJSON output is supported when 'polars' is installed."
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
        help="Output format. Use 'ndjson' with polars for streaming output.",
    )
    return parser


def _load_file(file_path: Path) -> FrameT:
    """Load a binary dataframe file based on its extension."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        sys.exit(1)

    suffix = file_path.suffix.lower()
    try:
        if suffix == ".parquet":
            return nw.scan_parquet(str(file_path))
        if suffix in {".feather", ".arrow", ".ipc"}:
            # Try polars for lazy scanning first
            try:
                import polars as pl

                return nw.from_native(pl.scan_ipc(str(file_path)), eager=False)
            except ImportError:
                # Fallback to pyarrow
                try:
                    import pyarrow.feather as pf

                    return nw.from_native(pf.read_table(str(file_path)))
                except ImportError:
                    print(
                        f"Error: To read {suffix} files, please install 'polars' or 'pyarrow'.",
                        file=sys.stderr,
                    )
                    sys.exit(1)

        print(
            f"Error: Unsupported or non-binary file type '{suffix}'.\n"
            "nwgrep CLI is optimized for binary formats (Parquet, Feather, IPC).\n"
            "For text files (CSV, TSV, TXT), use standard 'grep' or 'ripgrep'.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def _write_ndjson(native_df: Any) -> None:
    """Write dataframe to ndjson format based on engine."""
    if hasattr(native_df, "to_json"):  # pandas
        print(native_df.to_json(orient="records", lines=True))
    elif hasattr(native_df, "write_ndjson"):  # polars eager
        import io

        buf = io.BytesIO()
        native_df.write_ndjson(buf)
        print(buf.getvalue().decode("utf-8").strip())
    else:
        print(
            f"Error: NDJSON output not supported for backend {type(native_df)}",
            file=sys.stderr,
        )
        sys.exit(1)


def _output_results(result: FrameT, args: argparse.Namespace) -> None:
    """Handle printing or streaming the filtered results."""
    # Handle NDJSON streaming optimization for Polars
    if args.format == "ndjson":
        native_result = nw.to_native(result)
        if hasattr(native_result, "sink_ndjson") and not args.max_rows:
            # True streaming sink for Polars LazyFrame
            native_result.sink_ndjson(sys.stdout)
            return

    # Collect results for other formats or if streaming is not available
    result_df = result.collect() if hasattr(result, "collect") else result

    # Limit rows if requested
    if args.max_rows:
        result_df = nw.from_native(result_df).head(args.max_rows).to_native()

    # Output results
    native_df = nw.to_native(nw.from_native(result_df))
    if args.format == "csv":
        print(native_df.to_csv(index=False))
    elif args.format == "tsv":
        print(native_df.to_csv(sep="\t", index=False))
    elif args.format == "ndjson":
        _write_ndjson(native_df)
    else:  # table
        print(result_df)


def main() -> None:
    """Command-line interface for nwgrep."""
    parser = _create_parser()
    args = parser.parse_args()

    file_path = Path(args.file)
    df = _load_file(file_path)

    columns = args.columns.split(",") if args.columns else None

    try:
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
    except Exception as e:  # noqa: BLE001
        print(f"Error during search: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
