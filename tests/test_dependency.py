# -*- coding: utf-8 -*-

import pytest

import pytest_order


@pytest.fixture
def order_dependencies(ignore_settings):
    pytest_order.Settings.order_dependencies = True
    yield
    pytest_order.Settings.order_dependencies = False


def test_ignore_order_with_dependency(item_names_for):
    tests_content = """
import pytest

def test_a():
    pass

@pytest.mark.dependency(depends=['test_a'])
@pytest.mark.order("first")
def test_b():
    pass
    """
    assert item_names_for(tests_content) == ["test_a", "test_b"]


def test_order_with_dependency(item_names_for):
    tests_content = """
import pytest

@pytest.mark.dependency(depends=['test_b'])
@pytest.mark.order("second")
def test_a():
    pass

def test_b():
    pass
    """
    assert item_names_for(tests_content) == ["test_b", "test_a"]


@pytest.fixture(scope="module")
def ordered_test():
    yield """
import pytest

def test_a():
    pass

@pytest.mark.dependency(depends=['test_a'])
def test_b():
    pass
    """


def test_dependency_already_ordered_default(ordered_test, item_names_for):
    assert item_names_for(ordered_test) == ["test_a", "test_b"]


def test_dependency_already_ordered_with_ordering(ordered_test,
                                                  item_names_for,
                                                  order_dependencies):
    assert item_names_for(ordered_test) == ["test_a", "test_b"]


@pytest.fixture(scope="module")
def order_dependency_test():
    yield """
import pytest

@pytest.mark.dependency(depends=['test_b'])
def test_a():
    pass

def test_b():
    pass
    """


def test_order_dependency_default(order_dependency_test, item_names_for):
    assert item_names_for(order_dependency_test) == ["test_a", "test_b"]


def test_order_dependency_ordered(order_dependency_test, item_names_for,
                                  order_dependencies):
    assert item_names_for(order_dependency_test) == ["test_b", "test_a"]


@pytest.fixture(scope="module")
def multiple_dependencies_test():
    yield """
import pytest

@pytest.mark.dependency(depends=["test_b", "test_c"])
def test_a():
    pass

def test_b():
    pass

def test_c():
    pass
    """


def test_order_multiple_dependencies_default(multiple_dependencies_test,
                                             item_names_for):
    assert item_names_for(multiple_dependencies_test) == [
        "test_a", "test_b", "test_c"
    ]


def test_order_multiple_dependencies_ordered(multiple_dependencies_test,
                                             item_names_for,
                                             order_dependencies):
    assert item_names_for(multiple_dependencies_test) == [
        "test_b", "test_c", "test_a"
    ]


@pytest.fixture(scope="module")
def named_dependency_test():
    yield """
import pytest

@pytest.mark.dependency(depends=["my_test"])
def test_a():
    pass

@pytest.mark.dependency(name="my_test")
def test_b():
    pass

def test_c():
    pass
    """


def test_order_named_dependency_default(named_dependency_test, item_names_for):
    assert item_names_for(named_dependency_test) == [
        "test_a", "test_b", "test_c"
    ]


def test_order_named_dependency_ordered(named_dependency_test,
                                        item_names_for, order_dependencies):
    assert item_names_for(named_dependency_test) == [
        "test_b", "test_a", "test_c"
    ]
