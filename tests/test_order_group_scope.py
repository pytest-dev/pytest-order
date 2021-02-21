# -*- coding: utf-8 -*-
import os
import shutil

import pytest

import pytest_order
from tests.utils import write_test, assert_test_order


@pytest.fixture(scope="module")
def fixture_path(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("group_scope"))
    testname = os.path.join(fixture_path, "test_clss.py")
    test_class_contents = """
import pytest

class Test1:
    @pytest.mark.order(2)
    def test_two(self):
        assert True

    def test_one(self):
        assert True

class Test2:
    def test_two(self):
        assert True

    @pytest.mark.order(1)
    def test_one(self):
        assert True

@pytest.mark.order(-1)
def test_two():
    assert True

def test_one():
    assert True
"""
    write_test(testname, test_class_contents)

    test_function_contents = """
import pytest

@pytest.mark.order(5)
def test1_two():
    assert True

def test1_one():
    assert True
    """
    testname = os.path.join(fixture_path, "test_fcts1.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

@pytest.mark.order(0)
def test2_two():
    assert True

def test2_one():
    assert True
    """
    testname = os.path.join(fixture_path, "test_fcts2.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

@pytest.mark.order(-2)
def test3_two():
    assert True

def test3_one():
    assert True
    """
    testname = os.path.join(fixture_path, "test_fcts3.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

def test4_one():
    assert True

def test4_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_fcts4.py")
    write_test(testname, test_function_contents)

    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.fixture(scope="module")
def fixture_file_paths(fixture_path):
    yield [
        os.path.join(fixture_path, "test_clss.py"),
        os.path.join(fixture_path, "test_fcts1.py"),
        os.path.join(fixture_path, "test_fcts2.py"),
        os.path.join(fixture_path, "test_fcts3.py"),
        os.path.join(fixture_path, "test_fcts4.py")
    ]


def test_session_scope(fixture_path, capsys):
    args = ["-v", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_fcts2.py::test2_two",
        "test_clss.py::Test2::test_one",
        "test_clss.py::Test1::test_two",
        "test_fcts1.py::test1_two",
        "test_clss.py::Test1::test_one",
        "test_clss.py::Test2::test_two",
        "test_clss.py::test_one",
        "test_fcts1.py::test1_one",
        "test_fcts2.py::test2_one",
        "test_fcts3.py::test3_one",
        "test_fcts4.py::test4_one",
        "test_fcts4.py::test4_two",
        "test_fcts3.py::test3_two",
        "test_clss.py::test_two"
    )
    assert_test_order(expected, out)


def test_module_group_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_fcts2.py::test2_two",
        "test_fcts2.py::test2_one",
        "test_clss.py::Test2::test_one",
        "test_clss.py::Test1::test_two",
        "test_clss.py::Test1::test_one",
        "test_clss.py::Test2::test_two",
        "test_clss.py::test_one",
        "test_clss.py::test_two",
        "test_fcts1.py::test1_two",
        "test_fcts1.py::test1_one",
        "test_fcts4.py::test4_one",
        "test_fcts4.py::test4_two",
        "test_fcts3.py::test3_one",
        "test_fcts3.py::test3_two",
    )
    assert_test_order(expected, out)


def test_class_group_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=class", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_fcts2.py::test2_two",
        "test_fcts2.py::test2_one",
        "test_clss.py::Test2::test_one",
        "test_clss.py::Test2::test_two",
        "test_clss.py::Test1::test_two",
        "test_clss.py::Test1::test_one",
        "test_clss.py::test_one",
        "test_clss.py::test_two",
        "test_fcts1.py::test1_two",
        "test_fcts1.py::test1_one",
        "test_fcts4.py::test4_one",
        "test_fcts4.py::test4_two",
        "test_fcts3.py::test3_one",
        "test_fcts3.py::test3_two",
    )
    assert_test_order(expected, out)


def test_class_group_scope_module_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=class",
            "--order-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_clss.py::Test2::test_one",
        "test_clss.py::Test2::test_two",
        "test_clss.py::Test1::test_two",
        "test_clss.py::Test1::test_one",
        "test_clss.py::test_one",
        "test_clss.py::test_two",
        "test_fcts1.py::test1_two",
        "test_fcts1.py::test1_one",
        "test_fcts2.py::test2_two",
        "test_fcts2.py::test2_one",
        "test_fcts3.py::test3_one",
        "test_fcts3.py::test3_two",
        "test_fcts4.py::test4_one",
        "test_fcts4.py::test4_two",
    )
    assert_test_order(expected, out)


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="Warning does not appear in output in pytest < 3.8")
def test_invalid_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=function", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert ("UserWarning: Unknown order group scope 'function', "
            "ignoring it." in out)


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="Warning does not appear in output in pytest < 3.8")
def test_ignored_scope(fixture_path, capsys):
    args = ["-v", "--order-group-scope=session",
            "--order-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert ("UserWarning: Group scope is larger than order scope, ignoring it."
            in out)
