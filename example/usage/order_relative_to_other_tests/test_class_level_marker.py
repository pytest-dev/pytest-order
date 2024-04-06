"""Shows how to use relative markers on class level.
See https://pytest-order.readthedocs.io/en/stable/usage.html#id1
"""

import pytest


@pytest.mark.order(after="Test2")
class Test1:
    def test_1(self):
        assert True

    def test_2(self):
        assert True


class Test2:
    def test_1(self):
        assert True

    def test_2(self):
        assert True
