"""Test with ordering (as opposed to test.py) from the quick start chapter.
See https://mrbean-bremen.github.io/pytest-order/dev/#quickstart
"""
import pytest


@pytest.mark.order(2)
def test_foo():
    assert True


@pytest.mark.order(1)
def test_bar():
    assert True
