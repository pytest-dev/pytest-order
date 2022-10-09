"""One of the test files showing the use of the --order-scope option.
See https://pytest-order.readthedocs.io/en/stable/#order-scope
"""
import pytest


@pytest.mark.order(2)
def test2():
    pass


@pytest.mark.order(1)
def test1():
    pass
