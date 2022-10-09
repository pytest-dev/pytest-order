"""Shows how combined ordinal and relative sorting is handled.
See https://pytest-order.readthedocs.io/en/stable/#combination-of-absolute-and-relative-ordering  # noqa: E501
"""
import pytest


@pytest.mark.order(index=0, after="test_second")
def test_first():
    assert True


@pytest.mark.order(1)
def test_second():
    assert True
