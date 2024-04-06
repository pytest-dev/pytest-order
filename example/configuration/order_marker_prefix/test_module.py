"""Test files showing the use of the --order-marker-prefix option.
See https://pytest-order.readthedocs.io/en/stable/configuration.html#order-marker-prefix
"""

import pytest


@pytest.mark.m3
def test_a():
    assert True


@pytest.mark.m1
def test_b():
    assert True


@pytest.mark.m2
def test_c():
    assert True
