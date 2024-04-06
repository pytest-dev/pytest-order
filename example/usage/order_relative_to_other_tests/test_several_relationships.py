"""Shows how to use several relationships in the same marker, see
https://pytest-order.readthedocs.io/en/stable/usage.html#several-relationships-for-the-same-marker  # noqa: E501
"""

import pytest


@pytest.mark.order(after=["test_second", "other_module.py::test_other"])
def test_first():
    assert True


def test_second():
    assert True
