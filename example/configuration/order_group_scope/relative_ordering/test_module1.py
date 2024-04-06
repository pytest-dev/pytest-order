"""One of the test files showing the use of the --order-group-scope option.
See https://pytest-order.readthedocs.io/en/stable/configuration.html#order-group-scope
"""

import pytest


@pytest.mark.order(after="test_module2.py::test1")
def test1():
    pass


def test2():
    pass
