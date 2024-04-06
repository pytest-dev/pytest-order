"""One of the test files showing the use of the --order-scope-level option.
See https://pytest-order.readthedocs.io/en/stable/configuration.html#order-scope-level
"""

import pytest


@pytest.mark.order(4)
def test_four():
    pass


@pytest.mark.order(3)
def test_three():
    pass
