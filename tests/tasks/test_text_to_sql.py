import polars as pl
import pytest

from suite.tasks.text_to_sql import compare


@pytest.mark.parametrize("actual, expected, expected_result", [
    (
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        True,
    ),
    (
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        pl.DataFrame({"a": [4, 5, 6], "b": [1, 2, 3]}),
        True,
    ),
    (
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        pl.DataFrame({"c": [1, 2, 3], "d": [4, 5, 6]}),
        True,
    ),
    (
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        pl.DataFrame({"a": [1, 2, 3]}),
        True,
    ),
    (
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        pl.DataFrame({"a": [1, 2, 3], "b": [7, 8, 9]}),
        False,
    ),
    (
        pl.DataFrame({"a": [1, 2, 3]}),
        pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        False,
    ),
])
def test_compare(actual, expected, expected_result):
    assert compare(actual, expected) == expected_result
