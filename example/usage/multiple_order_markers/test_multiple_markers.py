"""Shows how to use several order markers to execute tests more than once, see
https://pytest-order.readthedocs.io/en/stable/usage.html#multiple-test-order-markers
"""

import pytest


@pytest.mark.order(1)
@pytest.mark.order(-1)
def test_one_and_seven():
    pass


@pytest.mark.order(2)
@pytest.mark.order(-2)
def test_two_and_six():
    pass


def test_four():
    pass


@pytest.mark.order(before="test_four")
@pytest.mark.order(after="test_four")
def test_three_and_five():
    pass
