from __future__ import annotations

from typing import TYPE_CHECKING, Any

import narwhals as nw

from nwgrep import nwgrep

if TYPE_CHECKING:
    from collections.abc import Callable


def to_pandas(res: Any) -> Any:
    """Helper to convert result to pandas for assertion."""
    return nw.from_native(res).to_pandas()


def test_basic_search(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    df = constructor(data)

    result = nwgrep(df, "active")

    # Assertions using pandas
    res_pd = to_pandas(result)
    assert len(res_pd) == 2
    assert "Alice" in res_pd["name"].to_numpy()
    assert "Eve" in res_pd["name"].to_numpy()


def test_case_insensitive(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"name": ["Alice", "Bob", "Eve"], "status": ["ACTIVE", "locked", "Active"]}
    df = constructor(data)

    result = nwgrep(df, "active", case_sensitive=False)
    res_pd = to_pandas(result)
    assert len(res_pd) == 2


def test_invert_match(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    df = constructor(data)

    result = nwgrep(df, "active", invert=True)
    res_pd = to_pandas(result)
    assert len(res_pd) == 1
    assert "Bob" in res_pd["name"].to_numpy()


def test_multiple_patterns(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    df = constructor(data)

    result = nwgrep(df, ["Alice", "Bob"])
    res_pd = to_pandas(result)
    assert len(res_pd) == 2


def test_specific_columns(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    df = constructor(data)

    result = nwgrep(df, "active", columns=["status"])
    res_pd = to_pandas(result)
    assert len(res_pd) == 2


def test_regex_search(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {
        "name": ["Alice", "Bob", "Eve"],
        "email": ["alice@test.com", "bob@example.com", "eve@test.com"],
    }
    df = constructor(data)

    result = nwgrep(df, r".*@test\.com", regex=True)
    res_pd = to_pandas(result)
    assert len(res_pd) == 2


def test_whole_word(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"text": ["activate", "active", "actor"]}
    df = constructor(data)

    result = nwgrep(df, "active", whole_word=True)
    res_pd = to_pandas(result)
    assert len(res_pd) == 1
    assert res_pd["text"].to_numpy()[0] == "active"


def test_null_handling(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    data = {"name": ["Alice", None, "Eve"], "status": ["active", "locked", None]}
    df = constructor(data)

    result = nwgrep(df, "active")
    res_pd = to_pandas(result)
    assert len(res_pd) == 1
    assert res_pd["name"].to_numpy()[0] == "Alice"
