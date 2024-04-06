"""One of the test files showing the use of the --order-group-scope option.
See https://pytest-order.readthedocs.io/en/stable/configuration.html#order-group-scope
"""

import pytest


@pytest.mark.order(2)
def test1():
    pass


def test2():
    pass
