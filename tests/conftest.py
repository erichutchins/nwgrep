from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--backend",
        action="store",
        default="pandas",
        help="Backend to use for tests (pandas, polars, pyarrow)",
    )


@pytest.fixture
def backend(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--backend")


@pytest.fixture
def constructor(backend: str) -> Callable[[dict[str, list[Any]]], Any]:
    if backend == "pandas":
        import pandas as pd

        return pd.DataFrame
    if backend == "polars":
        import polars as pl

        return pl.DataFrame
    if backend == "pyarrow":
        import pyarrow as pa

        return lambda data: pa.Table.from_pydict(data)

    msg = f"Unknown backend: {backend}"
    raise ValueError(msg)
