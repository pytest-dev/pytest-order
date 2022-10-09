"""Shows how to use both positive and negative numbers for sorting,
and the use of the long form (index attribute) and short form (number only).
See https://pytest-order.readthedocs.io/en/stable/#order-by-index
"""
import pytest


@pytest.mark.order(-2)
def test_three():
    assert True


@pytest.mark.order(index=-1)
def test_four():
    assert True


@pytest.mark.order(index=2)
def test_two():
    assert True


@pytest.mark.order(1)
def test_one():
    assert True
