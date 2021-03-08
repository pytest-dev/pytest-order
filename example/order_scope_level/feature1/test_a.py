import pytest


@pytest.mark.order(2)
def test_two():
    pass


@pytest.mark.order(1)
def test_one():
    pass
