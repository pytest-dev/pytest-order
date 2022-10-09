"""Shows how to sort tests relatively to each other, see
https://pytest-order.readthedocs.io/en/stable/#order-relative-to-other-tests
"""
import pytest


@pytest.mark.order(after="test_second")
def test_third():
    assert True


def test_second():
    assert True


@pytest.mark.order(before="test_second")
def test_first():
    assert True
