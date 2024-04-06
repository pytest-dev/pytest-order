"""Shows how to use several order markers in combination with parametrized tests, see
https://pytest-order.readthedocs.io/en/stable/usage.html#parametrized-tests
"""

import pytest


@pytest.mark.order(1)
@pytest.mark.order(3)
@pytest.mark.parametrize("foo", ["aaa", "bbb"])
def test_one_and_three(foo):
    pass


@pytest.mark.order(4)
@pytest.mark.parametrize("bar", ["bbb", "ccc"])
@pytest.mark.order(2)
def test_two_and_four(bar):
    pass
