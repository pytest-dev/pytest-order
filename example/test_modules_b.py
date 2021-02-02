"""Example showing ordering relative to tests in other modules.
See https://mrbean-bremen.github.io/pytest-order/dev/#referencing-of-tests-in-other-classes-or-modules  # noqa: E501
"""
import pytest


@pytest.mark.order(after="test_module_a.TestA::test_a")
def test_a():
    assert True


@pytest.mark.order(before="test_module_c.test_submodule.test_2")
def test_b():
    assert True
