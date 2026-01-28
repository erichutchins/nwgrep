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


# Tests for count feature
def test_count_basic(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    """Test basic count functionality."""
    data = {"name": ["Alice", "Bob", "Eve"], "status": ["active", "locked", "active"]}
    df = constructor(data)

    count = nwgrep(df, "active", count=True)
    assert count == 2
    assert isinstance(count, int)


def test_count_with_invert(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    """Test count with inverted match."""
    data = {"col": ["foo", "bar", "baz"]}
    df = constructor(data)

    count = nwgrep(df, "foo", invert=True, count=True)
    assert count == 2


def test_count_no_matches(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    """Test count returns 0 for no matches."""
    data = {"col": ["foo", "bar"]}
    df = constructor(data)

    count = nwgrep(df, "xyz", count=True)
    assert count == 0


def test_count_with_case_insensitive(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test count with case insensitive matching."""
    data = {"status": ["Active", "ACTIVE", "locked"]}
    df = constructor(data)

    count = nwgrep(df, "active", case_sensitive=False, count=True)
    assert count == 2


# Tests for exact match feature
def test_exact_match_fixed_strings(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match with fixed strings (equality)."""
    data = {"status": ["active", "user_active", "active_user"]}
    df = constructor(data)

    result = nwgrep(df, "active", exact=True)
    res_pd = to_pandas(result)

    assert len(res_pd) == 1
    assert res_pd["status"].iloc[0] == "active"


def test_exact_match_regex(constructor: Callable[[dict[str, list[Any]]], Any]) -> None:
    """Test exact match with regex (anchored)."""
    data = {"col": ["foo123", "bar456", "baz"]}
    df = constructor(data)

    result = nwgrep(df, "foo.*", exact=True, regex=True)
    res_pd = to_pandas(result)

    assert len(res_pd) == 1
    assert res_pd["col"].iloc[0] == "foo123"


def test_exact_match_case_insensitive(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match with case insensitivity."""
    data = {"status": ["Active", "ACTIVE", "active_user"]}
    df = constructor(data)

    result = nwgrep(df, "active", exact=True, case_sensitive=False)
    res_pd = to_pandas(result)

    assert len(res_pd) == 2
    assert set(res_pd["status"]) == {"Active", "ACTIVE"}


def test_exact_match_multiple_patterns(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match with multiple patterns (OR logic)."""
    data = {"status": ["active", "locked", "pending", "user_active"]}
    df = constructor(data)

    result = nwgrep(df, ["active", "locked"], exact=True)
    res_pd = to_pandas(result)

    assert len(res_pd) == 2
    assert set(res_pd["status"]) == {"active", "locked"}


def test_exact_match_with_count(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match combined with count."""
    data = {"status": ["active", "active", "user_active"]}
    df = constructor(data)

    count = nwgrep(df, "active", exact=True, count=True)
    assert count == 2


def test_exact_match_with_invert(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match with invert."""
    data = {"status": ["active", "user_active", "locked"]}
    df = constructor(data)

    result = nwgrep(df, "active", exact=True, invert=True)
    res_pd = to_pandas(result)

    assert len(res_pd) == 2
    assert set(res_pd["status"]) == {"user_active", "locked"}


def test_exact_match_with_nulls(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match handles nulls correctly."""
    data = {"status": ["active", None, "active"]}
    df = constructor(data)

    result = nwgrep(df, "active", exact=True)
    res_pd = to_pandas(result)

    assert len(res_pd) == 2
    assert all(res_pd["status"] == "active")


def test_exact_match_no_matches(
    constructor: Callable[[dict[str, list[Any]]], Any],
) -> None:
    """Test exact match with no matches returns empty."""
    data = {"status": ["user_active", "active_user"]}
    df = constructor(data)

    result = nwgrep(df, "active", exact=True)
    res_pd = to_pandas(result)

    assert len(res_pd) == 0
