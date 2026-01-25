from __future__ import annotations

import pytest

from nwgrep import register_grep_accessor

pd = pytest.importorskip("pandas")


def test_pandas_grep_accessor() -> None:
    register_grep_accessor()

    df = pd.DataFrame(
        {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    )

    # Test accessor is registered
    assert hasattr(df, "grep")

    result = df.grep("active")
    assert len(result) == 2
    assert "Alice" in result["name"].to_numpy()

    # Test with kwargs
    result = df.grep("ACTIVE", case_sensitive=False)
    assert len(result) == 2


def test_pandas_grep_specific_columns() -> None:
    register_grep_accessor()

    df = pd.DataFrame(
        {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    )

    result = df.grep("active", columns=["status"])
    assert len(result) == 2


def test_pandas_grep_regex() -> None:
    register_grep_accessor()

    df = pd.DataFrame({"email": ["alice@test.com", "bob@example.com", "eve@test.com"]})

    result = df.grep(r".*@test\.com", regex=True)
    assert len(result) == 2
