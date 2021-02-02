"""Test showing the behavior of the --order-dependencies option.
See https://mrbean-bremen.github.io/pytest-order/dev/#order-dependencies
"""
import pytest


@pytest.mark.dependency(depends=["test_b"])
def test_a():
    assert True


@pytest.mark.dependency
def test_b():
    assert True
