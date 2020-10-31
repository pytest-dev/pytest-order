import pytest


@pytest.mark.order("last")
def test_two():
    assert True


@pytest.mark.order("first")
def test_one():
    assert True
