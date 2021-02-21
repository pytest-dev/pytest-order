# -*- coding: utf-8 -*-
import os
import shutil

import pytest

import pytest_order

from tests.utils import write_test, assert_test_order


@pytest.fixture(scope="module")
def fixture_path(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("rel_scope"))
    testname = os.path.join(fixture_path, "test_rel1.py")
    test_class_contents = """
import pytest

class Test1:
    @pytest.mark.order(after='Test2::test_two')
    def test_one(self):
        assert True

    def test_two(self):
        assert True

class Test2:
    @pytest.mark.order(after='invalid')
    def test_one(self):
        assert True

    @pytest.mark.order(after='test_rel3.test_two')
    def test_two(self):
        assert True
"""
    write_test(testname, test_class_contents)

    test_function_contents = """
def test_one():
    assert True

def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_rel2.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

def test_one():
    assert True

@pytest.mark.order(before='test_rel2.test_one')
def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_rel3.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

def test_one():
    assert True

def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_rel4.py")
    write_test(testname, test_function_contents)

    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.fixture(scope="module")
def fixture_file_paths(fixture_path):
    yield [
        os.path.join(fixture_path, "test_rel1.py"),
        os.path.join(fixture_path, "test_rel2.py"),
        os.path.join(fixture_path, "test_rel3.py"),
        os.path.join(fixture_path, "test_rel4.py")
    ]


def test_session_scope(fixture_path, capsys):
    args = ["-v", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_rel1.py::Test1::test_two",
        "test_rel1.py::Test2::test_one",
        "test_rel3.py::test_two",
        "test_rel1.py::Test2::test_two",
        "test_rel1.py::Test1::test_one",
        "test_rel2.py::test_one",
        "test_rel2.py::test_two",
        "test_rel3.py::test_one",
        "test_rel4.py::test_one",
        "test_rel4.py::test_two",
    )
    assert_test_order(expected, out)
    assert "invalid - ignoring the marker." in out


def test_module_group_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_rel3.py::test_one",
        "test_rel3.py::test_two",
        "test_rel1.py::Test1::test_two",
        "test_rel1.py::Test2::test_one",
        "test_rel1.py::Test2::test_two",
        "test_rel1.py::Test1::test_one",
        "test_rel2.py::test_one",
        "test_rel2.py::test_two",
        "test_rel4.py::test_one",
        "test_rel4.py::test_two",
    )
    assert_test_order(expected, out)


def test_class_group_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=class", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_rel3.py::test_one",
        "test_rel3.py::test_two",
        "test_rel1.py::Test2::test_one",
        "test_rel1.py::Test2::test_two",
        "test_rel1.py::Test1::test_one",
        "test_rel1.py::Test1::test_two",
        "test_rel2.py::test_one",
        "test_rel2.py::test_two",
        "test_rel4.py::test_one",
        "test_rel4.py::test_two",
    )
    assert_test_order(expected, out)


def test_class_group_scope_module_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=class",
            "--order-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_rel1.py::Test2::test_one",
        "test_rel1.py::Test2::test_two",
        "test_rel1.py::Test1::test_one",
        "test_rel1.py::Test1::test_two",
        "test_rel2.py::test_one",
        "test_rel2.py::test_two",
        "test_rel3.py::test_one",
        "test_rel3.py::test_two",
        "test_rel4.py::test_one",
        "test_rel4.py::test_two",
    )
    assert_test_order(expected, out)
