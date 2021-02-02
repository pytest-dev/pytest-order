"""Shows how to use relative sorting in test classes, see
See https://mrbean-bremen.github.io/pytest-order/dev/#referencing-of-tests-in-other-classes-or-modules  # noqa: E501
"""
import pytest


class TestA:
    @pytest.mark.order(after="TestB::test_c")
    def test_a(self):
        assert True

    def test_b(self):
        assert True


class TestB:
    def test_c(self):
        assert True
