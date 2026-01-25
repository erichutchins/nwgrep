from __future__ import annotations

import pandas as pd

from nwgrep import nwgrep


def test_basic_search() -> None:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "status": ["active", "inactive", "active"],
    })

    result = nwgrep(df, "active")
    assert len(result) == 3
    assert "Alice" in result["name"].to_numpy()
    assert "Charlie" in result["name"].to_numpy()


def test_case_insensitive() -> None:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "status": ["ACTIVE", "inactive", "Active"],
    })

    result = nwgrep(df, "active", case_sensitive=False)
    assert len(result) == 3


def test_invert_match() -> None:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "status": ["active", "closed", "active"],
    })

    result = nwgrep(df, "active", invert=True)
    assert len(result) == 1
    assert "Bob" in result["name"].to_numpy()


def test_multiple_patterns() -> None:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "status": ["active", "inactive", "active"],
    })

    result = nwgrep(df, ["Alice", "Bob"])
    assert len(result) == 2


def test_specific_columns() -> None:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "status": ["active", "inactive", "active"],
    })

    result = nwgrep(df, "active", columns=["status"])
    assert len(result) == 3


def test_regex_search() -> None:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@test.com", "bob@example.com", "charlie@test.com"],
    })

    result = nwgrep(df, r".*@test\.com", regex=True)
    assert len(result) == 2


def test_whole_word() -> None:
    df = pd.DataFrame({
        "text": ["activate", "active", "actor"],
    })

    result = nwgrep(df, "active", whole_word=True)
    assert len(result) == 1
    assert result["text"].to_numpy()[0] == "active"


def test_null_handling() -> None:
    df = pd.DataFrame({
        "name": ["Alice", None, "Charlie"],
        "status": ["active", "inactive", None],
    })

    result = nwgrep(df, "active")
    assert len(result) == 2
    assert result["name"].to_numpy()[0] == "Alice"
