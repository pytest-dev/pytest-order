"""Test showing that sorting is not done if it would break an existing
dependency.
See https://mrbean-bremen.github.io/pytest-order/dev/#order-dependencies
"""
import pytest


def test_a():
    assert True


@pytest.mark.dependency(depends=["test_a"])
@pytest.mark.order("first")
def test_b():
    assert True
