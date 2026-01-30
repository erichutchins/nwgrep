from __future__ import annotations

import pytest

from nwgrep import nwgrep, register_grep_accessor

pd = pytest.importorskip("pandas")
pl = pytest.importorskip("polars")


def _has_great_tables() -> bool:
    """Check if Great Tables is installed."""
    try:
        import great_tables  # noqa: F401
    except ImportError:
        return False
    else:
        return True


class TestHighlightPandas:
    """Test highlighting with pandas backend."""

    def test_highlight_returns_styler(self) -> None:
        """Test that highlighting returns a Styler object."""
        df = pd.DataFrame({"col": ["foo", "bar", "baz"]})
        result = nwgrep(df, "foo", highlight=True)

        # Should return Styler object
        assert hasattr(result, "to_html"), "Result should be a Styler object"

    def test_highlight_preserves_data(self) -> None:
        """Test that highlighting preserves the underlying data."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "status": ["active", "locked"]})
        result = nwgrep(df, "active", highlight=True)

        # Get underlying data
        data = result.data
        assert len(data) == 1
        assert "Alice" in data.values[0]

    def test_highlight_with_no_matches(self) -> None:
        """Test highlighting with no matches returns empty Styler."""
        df = pd.DataFrame({"col": ["foo", "bar"]})
        result = nwgrep(df, "xyz", highlight=True)

        # Should return Styler even with no matches
        assert hasattr(result, "to_html")
        assert len(result.data) == 0

    def test_highlight_with_multiple_matches(self) -> None:
        """Test highlighting with multiple matching rows."""
        df = pd.DataFrame(
            {"name": ["Alice", "Anna", "Bob"], "status": ["active", "active", "locked"]}
        )
        result = nwgrep(df, "A", highlight=True)

        # Should have 2 matching rows
        assert len(result.data) == 2

    def test_highlight_incompatible_with_count(self) -> None:
        """Test that highlight and count are incompatible."""
        df = pd.DataFrame({"col": ["foo", "bar"]})

        with pytest.raises(ValueError, match="incompatible"):
            nwgrep(df, "foo", count=True, highlight=True)

    def test_highlight_with_accessor(self) -> None:
        """Test highlighting via the accessor method."""
        register_grep_accessor()

        df = pd.DataFrame({"col": ["foo", "bar", "baz"]})
        result = df.grep("foo", highlight=True)

        # Should return Styler object
        assert hasattr(result, "to_html")


class TestHighlightPolars:
    """Test highlighting with polars backend."""

    @pytest.mark.skipif(not _has_great_tables(), reason="Great Tables not installed")
    def test_highlight_returns_gt_object(self) -> None:
        """Test that highlighting returns a Great Tables object."""
        df = pl.DataFrame({"col": ["foo", "bar", "baz"]})
        result = nwgrep(df, "foo", highlight=True)

        # Should return GT object
        from great_tables import GT

        assert isinstance(result, GT)

    @pytest.mark.skipif(not _has_great_tables(), reason="Great Tables not installed")
    def test_highlight_preserves_data_polars(self) -> None:
        """Test that highlighting preserves the underlying data for polars."""
        df = pl.DataFrame({"name": ["Alice", "Bob"], "status": ["active", "locked"]})
        result = nwgrep(df, "active", highlight=True)

        # Get underlying dataframe
        from great_tables import GT

        assert isinstance(result, GT)
        # GT wraps the dataframe
        data = result._tbl_data
        assert len(data) == 1

    @pytest.mark.skipif(not _has_great_tables(), reason="Great Tables not installed")
    def test_highlight_with_no_matches_polars(self) -> None:
        """Test highlighting with no matches for polars."""
        df = pl.DataFrame({"col": ["foo", "bar"]})
        result = nwgrep(df, "xyz", highlight=True)

        from great_tables import GT

        assert isinstance(result, GT)
        # Empty dataframe
        assert len(result._tbl_data) == 0

    @pytest.mark.skipif(not _has_great_tables(), reason="Great Tables not installed")
    def test_highlight_with_lazy_frame(self) -> None:
        """Test that highlighting collects LazyFrames."""
        df = pl.DataFrame({"col": ["foo", "bar", "baz"]}).lazy()
        result = nwgrep(df, "foo", highlight=True)

        from great_tables import GT

        assert isinstance(result, GT)
        assert len(result._tbl_data) == 1

    @pytest.mark.skipif(not _has_great_tables(), reason="Great Tables not installed")
    def test_highlight_incompatible_with_count_polars(self) -> None:
        """Test that highlight and count are incompatible for polars."""
        df = pl.DataFrame({"col": ["foo", "bar"]})

        with pytest.raises(ValueError, match="incompatible"):
            nwgrep(df, "foo", count=True, highlight=True)

    @pytest.mark.skipif(not _has_great_tables(), reason="Great Tables not installed")
    def test_highlight_with_accessor_polars(self) -> None:
        """Test highlighting via the accessor method for polars."""
        register_grep_accessor()

        df = pl.DataFrame({"col": ["foo", "bar", "baz"]})
        result = df.grep("foo", highlight=True)

        from great_tables import GT

        assert isinstance(result, GT)


class TestHighlightEdgeCases:
    """Test edge cases for highlighting."""

    def test_highlight_with_regex(self) -> None:
        """Test highlighting with regex patterns."""
        df = pd.DataFrame({"col": ["foo123", "bar456", "baz789"]})
        result = nwgrep(df, r"foo\d+", regex=True, highlight=True)

        assert hasattr(result, "to_html")
        assert len(result.data) == 1

    def test_highlight_case_insensitive(self) -> None:
        """Test highlighting with case insensitive search."""
        df = pd.DataFrame({"col": ["FOO", "bar", "BAZ"]})
        result = nwgrep(df, "foo", case_sensitive=False, highlight=True)

        assert hasattr(result, "to_html")
        assert len(result.data) == 1

    def test_highlight_with_column_filter(self) -> None:
        """Test highlighting with specific column filtering."""
        df = pd.DataFrame(
            {"name": ["Alice", "Bob"], "email": ["a@foo.com", "b@bar.com"]}
        )
        result = nwgrep(df, "foo", columns=["email"], highlight=True)

        assert hasattr(result, "to_html")
        assert len(result.data) == 1

    def test_highlight_with_whole_word(self) -> None:
        """Test highlighting with whole_word parameter."""
        df = pd.DataFrame({"col": ["foo", "foobar", "bar foo"]})
        result = nwgrep(df, "foo", whole_word=True, highlight=True)

        assert hasattr(result, "to_html")
        # Should match "foo" and "bar foo" but not "foobar"
        assert len(result.data) == 2

    def test_highlight_with_exact_match(self) -> None:
        """Test highlighting with exact match parameter."""
        df = pd.DataFrame({"col": ["foo", "foobar", "FOO"]})
        result = nwgrep(df, "foo", exact=True, highlight=True)

        assert hasattr(result, "to_html")
        # Should only match exactly "foo"
        assert len(result.data) == 1
        assert result.data.iloc[0]["col"] == "foo"

    def test_highlight_unsupported_backend(self) -> None:
        """Test highlighting with unsupported backend."""
        from unittest.mock import patch

        df = pd.DataFrame({"col": ["foo"]})

        # Patch _detect_backend to return "unsupported"
        with (
            patch("nwgrep.core._detect_backend", return_value="unsupported"),
            pytest.raises(ValueError, match="Highlighting not supported"),
        ):
            nwgrep(df, "foo", highlight=True)
