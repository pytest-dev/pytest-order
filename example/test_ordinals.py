import pytest


@pytest.mark.order('second_to_last')
def test_three():
    assert True


@pytest.mark.order('last')
def test_four():
    assert True


@pytest.mark.order('second')
def test_two():
    assert True


@pytest.mark.order('first')
def test_one():
    assert True
