# -*- coding: utf-8 -*-

import pytest

import pytest_order
from utils import write_test, assert_test_order


def test_ignore_order_with_dependency(test_path, capsys):
    tests_content = """
import pytest

def test_a():
    pass

@pytest.mark.dependency(depends=['test_a'])
@pytest.mark.order("first")
def test_b():
    pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_a", "test_b"], out)


def test_order_with_dependency(test_path, capsys):
    tests_content = """
import pytest

@pytest.mark.dependency(depends=['test_b'])
@pytest.mark.order("second")
def test_a():
    pass

def test_b():
    pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_b", "test_a"], out)


def test_dependency_already_ordered(test_path, capsys):
    tests_content = """
import pytest

def test_a():
    pass

@pytest.mark.dependency(depends=['test_a'])
def test_b():
    pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_a", "test_b"], out)
    pytest.main(["-v", "--order-dependencies", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_a", "test_b"], out)


def test_order_dependency(test_path, capsys):
    tests_content = """
import pytest

@pytest.mark.dependency(depends=['test_b'])
def test_a():
    pass

def test_b():
    pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_a", "test_b"], out)
    pytest.main(["-v", "--order-dependencies", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_b", "test_a"], out)


def test_order_multiple_dependencies(test_path, capsys):
    tests_content = """
import pytest

@pytest.mark.dependency(depends=["test_b", "test_c"])
def test_a():
    pass

def test_b():
    pass

def test_c():
    pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_a", "test_b", "test_c"], out)
    pytest.main(["-v", "--order-dependencies", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_b", "test_c", "test_a"], out)


def test_order_named_dependency(test_path, capsys):
    tests_content = """
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
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_a", "test_b", "test_c"], out)
    pytest.main(["-v", "--order-dependencies", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_b", "test_a", "test_c"], out)
