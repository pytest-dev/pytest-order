"""Shows how parametrized tests are sorted, see
https://pytest-order.readthedocs.io/en/stable/usage.html#relationships-with-parameterized-tests  # noqa: E501
"""

import pytest


@pytest.mark.order(after=["test_second"])
def test_first():
    assert True


@pytest.mark.parametrize("param", [1, 2, 3])
def test_second(param):
    assert True
