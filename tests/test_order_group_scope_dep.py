# -*- coding: utf-8 -*-
import os
import re
import shutil

import pytest

import pytest_order
from tests.utils import write_test, assert_test_order

NODEID_ROOT = ""


def test_nodeid(get_nodeid, capsys):
    """Helper test to define the real nodeid."""
    global NODEID_ROOT
    args = ["-sq", get_nodeid]
    pytest.main(args)
    out, err = capsys.readouterr()
    match = re.match(".*NODEID=!!!(.*)!!!.*", out)
    NODEID_ROOT = match.group(1)
    if "/" in NODEID_ROOT:
        NODEID_ROOT = NODEID_ROOT[:NODEID_ROOT.rindex("/") + 1]
    else:
        NODEID_ROOT = ""


@pytest.fixture(scope="module")
def fixture_path(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("group_scope_dep"))
    testname = os.path.join(fixture_path, "test_dep1.py")
    nodeid_root = NODEID_ROOT.replace("nodeid_path", "group_scope_dep")
    test_class_contents = """
import pytest

class Test1:
    @pytest.mark.dependency(depends=['Test2::test_two'])
    def test_one(self):
        assert True

    @pytest.mark.dependency(depends=['test_three'], scope="class")
    def test_two(self):
        assert True

    @pytest.mark.dependency
    def test_three(self):
        assert True

class Test2:
    def test_one(self):
        assert True

    @pytest.mark.dependency(depends=['{}test_dep3.py::test_two'],
                            scope='session')
    def test_two(self):
        assert True
""".format(nodeid_root)
    write_test(testname, test_class_contents)

    test_function_contents = """
import pytest

@pytest.mark.dependency(depends=['{}test_dep3.py::test_two'], scope='session')
def test_one():
    assert True

def test_two():
    assert True
    """.format(nodeid_root)
    testname = os.path.join(fixture_path, "test_dep2.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

def test_one():
    assert True

@pytest.mark.dependency
def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_dep3.py")
    write_test(testname, test_function_contents)
    test_function_contents = """
import pytest

def test_one():
    assert True

def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_dep4.py")
    write_test(testname, test_function_contents)

    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.fixture(scope="module")
def fixture_file_paths(fixture_path):
    yield [
        os.path.join(fixture_path, "test_dep1.py"),
        os.path.join(fixture_path, "test_dep2.py"),
        os.path.join(fixture_path, "test_dep3.py"),
        os.path.join(fixture_path, "test_dep4.py")
    ]


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="pytest-dependency < 0.5 does not support "
                           "session scope")
def test_session_scope(fixture_path, capsys):
    args = ["-v", "--order-dependencies", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_dep1.py::Test1::test_three",
        "test_dep1.py::Test1::test_two",
        "test_dep1.py::Test2::test_one",
        "test_dep2.py::test_two",
        "test_dep3.py::test_one",
        "test_dep3.py::test_two",
        "test_dep1.py::Test2::test_two",
        "test_dep1.py::Test1::test_one",
        "test_dep2.py::test_one",
        "test_dep4.py::test_one",
        "test_dep4.py::test_two",
    )
    assert_test_order(expected, out)
    assert "SKIPPED" not in out


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="pytest-dependency < 0.5 does not support "
                           "session scope")
def test_module_group_scope(fixture_path, capsys):
    args = ["-v", "--order-dependencies",
            "--order-group-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_dep3.py::test_one",
        "test_dep3.py::test_two",
        "test_dep1.py::Test1::test_three",
        "test_dep1.py::Test1::test_two",
        "test_dep1.py::Test2::test_one",
        "test_dep1.py::Test2::test_two",
        "test_dep1.py::Test1::test_one",
        "test_dep2.py::test_one",
        "test_dep2.py::test_two",
        "test_dep4.py::test_one",
        "test_dep4.py::test_two",
    )
    assert_test_order(expected, out)
    assert "SKIPPED" not in out


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="pytest-dependency < 0.5 does not support "
                           "session scope")
def test_class_group_scope(fixture_path, capsys):
    args = ["-v", "--order-dependencies",
            "--order-group-scope=class", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_dep3.py::test_one",
        "test_dep3.py::test_two",
        "test_dep1.py::Test2::test_one",
        "test_dep1.py::Test2::test_two",
        "test_dep1.py::Test1::test_one",
        "test_dep1.py::Test1::test_three",
        "test_dep1.py::Test1::test_two",
        "test_dep2.py::test_one",
        "test_dep2.py::test_two",
        "test_dep4.py::test_one",
        "test_dep4.py::test_two",
    )
    assert_test_order(expected, out)
    assert "SKIPPED" not in out


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="pytest-dependency < 0.5 does not support "
                           "session scope")
def test_class_group_scope_module_scope(fixture_path, capsys):
    args = ["-v", "--order-dependencies", "--order-group-scope=class",
            "--order-scope=module", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_dep1.py::Test2::test_one",
        "test_dep1.py::Test2::test_two",
        "test_dep1.py::Test1::test_one",
        "test_dep1.py::Test1::test_three",
        "test_dep1.py::Test1::test_two",
        "test_dep2.py::test_one",
        "test_dep2.py::test_two",
        "test_dep3.py::test_one",
        "test_dep3.py::test_two",
        "test_dep4.py::test_one",
        "test_dep4.py::test_two",
    )
    assert_test_order(expected, out)
    # with module scope, dependencies cannot be ordered as needed
    assert "SKIPPED" in out
