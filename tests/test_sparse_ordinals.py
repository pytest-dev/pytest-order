# -*- coding: utf-8 -*-

import pytest

import pytest_order
from utils import write_test, assert_test_order


def test_first(test_path, capsys):
    tests_content = """
import pytest

def test_1(): pass

@pytest.mark.order("first")
def test_2(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_2", "test_1"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_2", "test_1"], out)


def test_second(test_path, capsys):
    tests_content = """
import pytest

def test_1(): pass
def test_2(): pass
def test_3(): pass
def test_4(): pass

@pytest.mark.order("second")
def test_5(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_5", "test_1", "test_2", "test_3", "test_4"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_1", "test_5", "test_2", "test_3", "test_4"], out)


def test_third(test_path, capsys):
    tests_content = """
import pytest

def test_1(): pass
def test_2(): pass
def test_3(): pass

@pytest.mark.order("third")
def test_4(): pass

def test_5(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_4", "test_1", "test_2", "test_3", "test_5"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_1", "test_2", "test_4", "test_3", "test_5"], out)


def test_second_to_last(test_path, capsys):
    tests_content = """
import pytest

def test_1(): pass

@pytest.mark.order("second_to_last")
def test_2(): pass

def test_3(): pass
def test_4(): pass
def test_5(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_1", "test_3", "test_4", "test_5", "test_2"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_1", "test_3", "test_4", "test_2", "test_5"], out)


def test_last(test_path, capsys):
    tests_content = """
import pytest

@pytest.mark.order("last")
def test_1(): pass

def test_2(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_2", "test_1"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_2", "test_1"], out)


def test_first_last(test_path, capsys):
    tests_content = """
import pytest

@pytest.mark.order("last")
def test_1(): pass

@pytest.mark.order("first")
def test_2(): pass

def test_3(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_2", "test_3", "test_1"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_2", "test_3", "test_1"], out)


def test_duplicate_numbers(test_path, capsys):
    tests_content = """
import pytest

@pytest.mark.order(1)
def test_1(): pass

@pytest.mark.order(1)
def test_2(): pass

def test_3(): pass

def test_4(): pass

@pytest.mark.order(4)
def test_5(): pass
    """
    write_test(test_path, tests_content)
    pytest.main(["-v", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_1", "test_2", "test_5", "test_3", "test_4"], out)
    pytest.main(["-v", "--sparse-ordering", test_path], [pytest_order])
    out, err = capsys.readouterr()
    assert_test_order(["test_3", "test_1", "test_2", "test_4", "test_5"], out)
