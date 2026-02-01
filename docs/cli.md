# CLI Reference

nwgrep includes a command-line interface for searching parquet, feather, and other binary dataframe formats.

## Installation

To use the CLI, install nwgrep with the `cli` extra (includes polars for efficient file scanning):

```bash
uv add nwgrep[cli]
# or
pip install nwgrep[cli]
```

## Basic Usage

```bash
nwgrep [OPTIONS] PATTERN FILE
```

Search for `PATTERN` in `FILE` and print matching rows.

## Examples

### Simple Search

```bash
# Find rows containing "error"
nwgrep "error" logfile.parquet

# Find rows containing "warning"
nwgrep "warning" data.feather
```

### Case-Insensitive Search

```bash
# Match "ERROR", "error", "Error", etc.
nwgrep -i "error" logs.parquet
nwgrep --ignore-case "warning" data.feather
```

### Invert Match

Return rows that do NOT match the pattern (like `grep -v`):

```bash
# Find rows without "success"
nwgrep -v "success" results.parquet
nwgrep --invert-match "test" data.feather
```

### Regex Search

```bash
# Find email addresses
nwgrep -E "\w+@\w+\.\w+" users.parquet

# Find IP addresses
nwgrep --regex "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" access.log.parquet
```

### Column-Specific Search

```bash
# Only search in specific columns
nwgrep --columns name,email "alice" users.parquet

# Search in a single column
nwgrep --columns status "active" users.feather
```

### Count Matches

```bash
# Print count of matching rows instead of the rows themselves
nwgrep --count "error" logs.parquet

# Useful for quick statistics
nwgrep --count -i "warning" data.feather
```

### List Files with Matches

```bash
# Print filename if matches found (like grep -l)
nwgrep -l "error" data.parquet

# With multiple files
nwgrep -l "pattern" *.parquet

# Useful for filtering which files to process
for file in $(nwgrep -l "error" *.parquet); do
    echo "Processing $file with errors"
done
```

### Show Only Matching Values

```bash
# Print only the values that matched (like grep -o)
nwgrep -o "error" logs.parquet

# Extract email addresses
nwgrep -o -E "\w+@\w+\.\w+" users.parquet

# Output format is still configurable
nwgrep -o --format csv "pattern" data.parquet
```

### Limit Output

```bash
# Show only first 10 matches
nwgrep -n 10 "error" large_file.parquet
nwgrep --max-count 10 "pattern" data.feather
```

### Output Formats

=== "Default (Table)"

    ```bash
    # Default: pretty table format
    nwgrep "pattern" data.parquet
    ```

=== "NDJSON"

    ```bash
    # Newline-delimited JSON (streams lazily!)
    nwgrep --format ndjson "pattern" data.parquet

    # Perfect for piping to other tools
    nwgrep --format ndjson "error" logs.parquet | jq '.timestamp'
    ```

=== "CSV"

    ```bash
    # CSV output
    nwgrep --format csv "pattern" data.parquet > results.csv
    ```

=== "TSV"

    ```bash
    # Tab-separated values
    nwgrep --format tsv "pattern" data.parquet
    ```

### Supported File Formats

nwgrep automatically detects the file format:

```bash
# Parquet files
nwgrep "pattern" data.parquet

# Feather files
nwgrep "pattern" data.feather
nwgrep "pattern" data.arrow

# CSV files
nwgrep "pattern" data.csv

# NDJSON files
nwgrep "pattern" data.ndjson
nwgrep "pattern" data.jsonl
```

## Command-Line Options

### Search Options

| Option           | Short | Description                                        |
| ---------------- | ----- | -------------------------------------------------- |
| `--ignore-case`  | `-i`  | Case-insensitive search                            |
| `--invert-match` | `-v`  | Select non-matching rows                           |
| `--regex`        | `-E`  | Treat pattern as regex                             |
| `--columns COLS` |       | Search only in specified columns (comma-separated) |
| `--max-count N`  | `-n`  | Stop after N matches                               |

### Output Options

| Option                 | Short | Description                                        |
| ---------------------- | ----- | -------------------------------------------------- |
| `--count`              |       | Print count of matching rows instead of rows       |
| `--files-with-matches` | `-l`  | Print only filenames with matches (like `grep -l`) |
| `--only-matching`      | `-o`  | Print only the matching values (like `grep -o`)    |
| `--format FORMAT`      | `-f`  | Output format: `table`, `csv`, `tsv`, `ndjson`     |
| `--no-header`          |       | Omit column headers in output                      |

### Other Options

| Option      | Short | Description           |
| ----------- | ----- | --------------------- |
| `--version` |       | Show version and exit |
| `--help`    | `-h`  | Show help message     |

## Advanced Usage

### Pipeline with jq

Process NDJSON output with jq:

```bash
# Extract specific fields
nwgrep --format ndjson "error" logs.parquet | jq '.timestamp, .message'

# Filter further
nwgrep --format ndjson "error" logs.parquet | jq 'select(.level == "CRITICAL")'

# Count matches
nwgrep --format ndjson "error" logs.parquet | jq -s 'length'
```

### Pipeline with Other Tools

```bash
# CSV output to grep for further filtering
nwgrep --format csv "error" logs.parquet | grep "database"

# Count matching rows
nwgrep --format csv "error" logs.parquet | wc -l

# Sort and unique
nwgrep --format csv "error" logs.parquet | sort | uniq
```

### Multiple Files

Process multiple files using shell globbing:

```bash
# Search all parquet files
for file in logs/*.parquet; do
    echo "==> $file <=="
    nwgrep "error" "$file"
done

# Or with find
find logs/ -name "*.parquet" -exec nwgrep "error" {} \;
```

### Complex Patterns

```bash
# Find error codes 400-499
nwgrep -E "HTTP [4][0-9]{2}" access.log.parquet

# Find emails from specific domains
nwgrep -E "@(gmail|yahoo)\.com" users.parquet

# Find dates in YYYY-MM-DD format
nwgrep -E "\d{4}-\d{2}-\d{2}" events.parquet
```

## Performance Tips

### Use NDJSON for Large Results

NDJSON format streams results lazily, perfect for large datasets:

```bash
# Streams output - low memory usage
nwgrep --format ndjson "pattern" huge_file.parquet | head -100
```

### Column Filtering

Significantly faster when you know which columns to search:

```bash
# Faster - only searches email column
nwgrep --columns email "@gmail.com" users.parquet

# Slower - searches all columns
nwgrep "@gmail.com" users.parquet
```

### Use Lazy Evaluation

The CLI uses polars lazy evaluation automatically:

- Parquet files are scanned lazily
- Only matching rows are loaded into memory
- Efficient even for multi-GB files

## Exit Status

- `0` - Matches found
- `1` - No matches found
- `2` - Error (invalid arguments, file not found, etc.)

## Comparison with grep

| Feature                   | grep | nwgrep |
| ------------------------- | ---- | ------ |
| Plain text files          | ✅   | ❌     |
| Binary dataframe formats  | ❌   | ✅     |
| Column-aware              | ❌   | ✅     |
| Structured output         | ❌   | ✅     |
| `-i` (ignore case)        | ✅   | ✅     |
| `-v` (invert)             | ✅   | ✅     |
| `-E` (regex)              | ✅   | ✅     |
| `-c` (count)              | ✅   | ✅     |
| `-l` (files with matches) | ✅   | ✅     |
| `-o` (only matching)      | ✅   | ✅     |
| Line numbers              | ✅   | N/A    |

nwgrep complements grep - use grep for text files, nwgrep for dataframe files.

## Examples by Use Case

### Log Analysis

```bash
# Find errors in parquet logs
nwgrep -i "error" application.log.parquet

# Find errors excluding test environment
nwgrep "error" logs.parquet | nwgrep -v "test"

# Extract error timestamps
nwgrep --format ndjson "error" logs.parquet | jq '.timestamp'
```

### Data Exploration

```bash
# Quick peek at active users
nwgrep "active" users.parquet -n 10

# Find all Gmail users
nwgrep "@gmail.com" users.parquet --columns email

# Check for missing data (null, NA, etc.)
nwgrep -E "(null|NA|None)" data.parquet
```

### Data Extraction

```bash
# Extract matching rows to CSV
nwgrep "condition" data.parquet --format csv > subset.csv

# Convert parquet subset to NDJSON
nwgrep "pattern" data.parquet --format ndjson > subset.jsonl

# Filter and transform
nwgrep --format ndjson "error" logs.parquet | jq '{time: .timestamp, msg: .message}' > errors.jsonl
```

## Troubleshooting

### File Not Found

```bash
$ nwgrep "pattern" missing.parquet
Error: File not found: missing.parquet
```

Check the file path and ensure the file exists.

### Invalid Regex

```bash
$ nwgrep -E "[invalid(regex" data.parquet
Error: Invalid regex pattern: [invalid(regex
```

Fix the regex pattern syntax.

### No CLI Installed

```bash
$ nwgrep "pattern" data.parquet
bash: nwgrep: command not found
```

Install with CLI support:

```bash
uv add nwgrep[cli]
```

## See Also

- [Usage Guide](usage.md) - Python API usage
- [API Reference](api.md) - Function reference
- [Installation](installation.md) - Setup instructions
