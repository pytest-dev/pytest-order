"""One of the test files showing the use of the --order-scope-level option.
See https://pytest-order.readthedocs.io/en/stable/configuration.html#order-scope-level
"""

import pytest


@pytest.mark.order(2)
def test_two():
    pass


@pytest.mark.order(1)
def test_one():
    pass
