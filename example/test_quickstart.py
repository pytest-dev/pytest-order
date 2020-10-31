import pytest


@pytest.mark.order(2)
def test_foo():
    assert True


@pytest.mark.order(1)
def test_bar():
    assert True
