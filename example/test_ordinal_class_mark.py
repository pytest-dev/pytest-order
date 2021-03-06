import pytest


@pytest.mark.order(1)
class Test1:
    def test_1(self):
        assert True

    def test_2(self):
        assert True


@pytest.mark.order(0)
class Test2:
    def test_1(self):
        assert True

    def test_2(self):
        assert True
