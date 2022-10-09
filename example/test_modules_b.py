"""Example showing ordering relative to tests in other modules.
See https://pytest-order.readthedocs.io/en/stable/#referencing-of-tests-in-other-classes-or-modules  # noqa: E501
"""
import pytest


@pytest.mark.order(after="test_module_a.py::TestA::test_a")
def test_a():
    assert True


@pytest.mark.order(before="test_module_c.py::test_submodule.test_2")
def test_b():
    assert True
