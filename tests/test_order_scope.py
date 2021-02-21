# -*- coding: utf-8 -*-
import os
import shutil

import pytest

import pytest_order
from tests.utils import write_test, assert_test_order


@pytest.fixture(scope="module")
def fixture_path(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("order_scope"))
    testname = os.path.join(fixture_path, "test_classes.py")
    test_class_contents = """
import pytest

class Test1:
    @pytest.mark.order("last")
    def test_two(self):
        assert True

    @pytest.mark.order("first")
    def test_one(self):
        assert True

class Test2:
    @pytest.mark.order("last")
    def test_two(self):
        assert True

    @pytest.mark.order("first")
    def test_one(self):
        assert True

@pytest.mark.order("last")
def test_two():
    assert True

@pytest.mark.order("first")
def test_one():
    assert True
"""
    write_test(testname, test_class_contents)

    test_function_contents = """
import pytest

@pytest.mark.order("last")
def test1_two():
    assert True

@pytest.mark.order("first")
def test1_one():
    assert True
    """
    testname = os.path.join(fixture_path, "test_functions1.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

@pytest.mark.order("last")
def test2_two():
    assert True

@pytest.mark.order("first")
def test2_one():
    assert True
    """
    testname = os.path.join(fixture_path, "test_functions2.py")
    write_test(testname, test_function_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.fixture(scope="module")
def fixture_file_paths(fixture_path):
    yield [
        os.path.join(fixture_path, "test_classes.py"),
        os.path.join(fixture_path, "test_functions1.py"),
        os.path.join(fixture_path, "test_functions2.py")
    ]


def test_session_scope(fixture_path, capsys):
    args = ["-v", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_classes.py::Test1::test_one",
        "test_classes.py::Test2::test_one",
        "test_classes.py::test_one",
        "test_functions1.py::test1_one",
        "test_functions2.py::test2_one",
        "test_classes.py::Test1::test_two",
        "test_classes.py::Test2::test_two",
        "test_classes.py::test_two",
        "test_functions1.py::test1_two",
        "test_functions2.py::test2_two"
    )
    assert_test_order(expected, out)


def test_session_scope_multiple_files(fixture_file_paths, capsys):
    """Test that session scope works with multiple files on command line."""
    args = ["-v"] + fixture_file_paths
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    # under Windows, the module name is not listed in this case,
    # so do not expect it
    expected = (
        "::Test1::test_one",
        "::Test2::test_one",
        "::test_one",
        "::test1_one",
        "::test2_one",
        "::Test1::test_two",
        "::Test2::test_two",
        "::test_two",
        "::test1_two",
        "::test2_two"
    )
    assert_test_order(expected, out)


def test_module_scope(fixture_path, capsys):
    args = ["-v", "--order-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_classes.py::Test1::test_one",
        "test_classes.py::Test2::test_one",
        "test_classes.py::test_one",
        "test_classes.py::Test1::test_two",
        "test_classes.py::Test2::test_two",
        "test_classes.py::test_two",
        "test_functions1.py::test1_one",
        "test_functions1.py::test1_two",
        "test_functions2.py::test2_one",
        "test_functions2.py::test2_two"
    )
    assert_test_order(expected, out)


def test_class_scope(fixture_path, capsys):
    args = ["-v", "--order-scope=class", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_classes.py::Test1::test_one",
        "test_classes.py::Test1::test_two",
        "test_classes.py::Test2::test_one",
        "test_classes.py::Test2::test_two",
        "test_classes.py::test_one",
        "test_classes.py::test_two",
        "test_functions1.py::test1_one",
        "test_functions1.py::test1_two",
        "test_functions2.py::test2_one",
        "test_functions2.py::test2_two"
    )
    assert_test_order(expected, out)


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="Warning does not appear in output in pytest < 3.8")
def test_invalid_scope(fixture_path, capsys):
    args = ["-v", "--order-scope=function", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert "UserWarning: Unknown order scope 'function', ignoring it." in out
