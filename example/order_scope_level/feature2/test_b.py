import pytest


@pytest.mark.order(4)
def test_four():
    pass


@pytest.mark.order(3)
def test_three():
    pass
