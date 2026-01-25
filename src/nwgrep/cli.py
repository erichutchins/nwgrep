from __future__ import annotations

import argparse
import sys
from pathlib import Path

import narwhals as nw

from nwgrep.core import nwgrep


def main() -> None:
    """Command-line interface for nwgrep."""
    parser = argparse.ArgumentParser(
        description="Grep for dataframes - search rows across any column",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nwgrep "error" data.csv
  nwgrep -i "warning" data.parquet
  nwgrep -v "success" data.csv
  nwgrep -E "err(or|!)?" data.csv
  nwgrep --columns name,email "alice" data.csv
        """,
    )
    parser.add_argument("pattern", help="Search pattern")
    parser.add_argument("file", help="CSV or Parquet file to search")
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
        choices=["table", "csv", "tsv"],
        default="table",
        help="Output format",
    )

    args = parser.parse_args()

    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)

    # Read file based on extension
    try:
        if file_path.suffix.lower() == ".parquet":
            df = nw.scan_parquet(str(file_path))
        elif file_path.suffix.lower() in {".csv", ".txt"}:
            df = nw.scan_csv(str(file_path))
        else:
            print(
                f"Error: Unsupported file type '{file_path.suffix}'",
                file=sys.stderr,
            )
            sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse columns if provided
    columns = args.columns.split(",") if args.columns else None

    # Perform grep
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

        # Collect results
        result_df = result.collect() if hasattr(result, "collect") else result

        # Limit rows if requested
        if args.max_rows:
            result_df = nw.from_native(result_df).head(args.max_rows)
            result_df = nw.to_native(result_df)

        # Output results
        if args.format == "csv":
            print(nw.to_native(nw.from_native(result_df)).to_csv(index=False))
        elif args.format == "tsv":
            print(
                nw.to_native(nw.from_native(result_df)).to_csv(sep="\t", index=False)
            )
        else:  # table
            print(result_df)

    except Exception as e:  # noqa: BLE001
        print(f"Error during search: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
