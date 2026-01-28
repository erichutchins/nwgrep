from __future__ import annotations

import subprocess
import sys
from pathlib import Path  # noqa: TC003

import pytest

pd = pytest.importorskip("pandas")


def test_cli_basic_search(tmp_path: Path) -> None:
    """Test basic CLI search functionality."""
    # Create test parquet file
    df = pd.DataFrame(
        {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    )
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    # Run CLI
    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "active", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Alice" in result.stdout
    assert "Eve" in result.stdout
    assert "Bob" not in result.stdout


def test_cli_case_insensitive(tmp_path: Path) -> None:
    """Test case-insensitive search."""
    df = pd.DataFrame({"text": ["HELLO", "world"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-i", "hello", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "HELLO" in result.stdout


def test_cli_invert_match(tmp_path: Path) -> None:
    """Test inverted matching."""
    df = pd.DataFrame({"col": ["foo", "bar", "baz"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-v", "foo", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "foo" not in result.stdout
    assert "bar" in result.stdout


def test_cli_file_not_found() -> None:
    """Test error handling for missing file."""
    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "pattern", "nonexistent.parquet"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "not found" in result.stderr.lower()


def test_cli_csv_output(tmp_path: Path) -> None:
    """Test CSV output format."""
    df = pd.DataFrame({"col": ["foo", "bar"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "--format", "csv", "foo", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "col" in result.stdout  # CSV header
    assert "foo" in result.stdout


def test_cli_regex_pattern(tmp_path: Path) -> None:
    """Test regex pattern matching."""
    df = pd.DataFrame({"col": ["foo123", "bar456", "baz789"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-E", "foo.*", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "foo123" in result.stdout
    assert "bar456" not in result.stdout


def test_cli_whole_word_match(tmp_path: Path) -> None:
    """Test whole word matching."""
    df = pd.DataFrame({"col": ["foo", "foobar", "barfoo"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-w", "foo", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "foo" in result.stdout
    assert "foobar" not in result.stdout
    assert "barfoo" not in result.stdout


def test_cli_count(tmp_path: Path) -> None:
    """Test CLI count flag."""
    df = pd.DataFrame({"col": ["foo", "bar", "foo"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "--count", "foo", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "2"


def test_cli_count_no_matches(tmp_path: Path) -> None:
    """Test CLI count with no matches."""
    df = pd.DataFrame({"col": ["foo", "bar"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "--count", "xyz", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "0"


def test_cli_exact_match(tmp_path: Path) -> None:
    """Test CLI exact match flag."""
    df = pd.DataFrame({"status": ["active", "user_active", "locked"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-x", "active", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "active" in result.stdout
    assert "user_active" not in result.stdout


def test_cli_exact_match_regex(tmp_path: Path) -> None:
    """Test CLI exact match with regex."""
    df = pd.DataFrame({"col": ["foo123", "bar456", "baz"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-x", "-E", "foo.*", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "foo123" in result.stdout
    assert "bar456" not in result.stdout


def test_cli_fixed_strings_conflict(tmp_path: Path) -> None:
    """Test CLI error for -F -w conflict."""
    df = pd.DataFrame({"col": ["foo"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-F", "-w", "foo", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "incompatible" in result.stderr.lower()


def test_cli_fixed_strings_override(tmp_path: Path) -> None:
    """Test CLI warning for -F -E conflict."""
    df = pd.DataFrame({"col": ["foo.*", "bar"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-F", "-E", "foo.*", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "warning" in result.stderr.lower()
    assert "foo.*" in result.stdout  # Should match literal "foo.*"


def test_cli_exact_with_count(tmp_path: Path) -> None:
    """Test combining exact match with count."""
    df = pd.DataFrame({"status": ["active", "active", "user_active"]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = subprocess.run(
        [sys.executable, "-m", "nwgrep.cli", "-x", "--count", "active", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "2"
