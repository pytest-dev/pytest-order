import pytest


class Test1:
    @pytest.mark.order("last")
    def test_two(self):
        assert True

    @pytest.mark.order("first")
    def test_one(self):
        assert True


class Test2:
    @pytest.mark.order("last")
    def test_two(self):
        assert True

    @pytest.mark.order("first")
    def test_one(self):
        assert True


@pytest.mark.order("last")
def test_two():
    assert True


@pytest.mark.order("first")
def test_one():
    assert True
