# -*- coding: utf-8 -*-
import os
import re
import shutil

import pytest

import pytest_order
from tests.utils import write_test, assert_test_order


@pytest.fixture(scope="module")
def fixture_path(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("order_scope_level"))
    test_b_contents = """
import pytest

@pytest.mark.order(2)
def test_two(): pass

@pytest.mark.order(1)
def test_one(): pass
"""
    test_a_contents = """
import pytest

@pytest.mark.order(4)
def test_four(): pass

@pytest.mark.order(3)
def test_three(): pass
"""
    for i in range(3):
        test_name = os.path.join(fixture_path, "feature{}".format(i),
                                 "test_a.py")
        write_test(test_name, test_a_contents)
        test_name = os.path.join(fixture_path, "feature{}".format(i),
                                 "test_b.py")
        write_test(test_name, test_b_contents)
        init_py = os.path.join(fixture_path, "feature{}".format(i),
                               "__init__.py")
        write_test(init_py, "")

    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


DIR_BASE = 0


def test_nodeid_length(get_nodeid, capsys):
    """Helper test to define the number of components in the node id."""
    global DIR_BASE
    args = ["-sq", get_nodeid]
    pytest.main(args)
    out, err = capsys.readouterr()
    match = re.match(".*NODEID=!!!(.*)!!!.*", out)
    node_id = match.group(1)
    DIR_BASE = node_id.count("/")


def test_session_scope(fixture_path, capsys):
    args = ["-v", fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "feature0/test_b.py::test_one",
        "feature1/test_b.py::test_one",
        "feature2/test_b.py::test_one",
        "feature0/test_b.py::test_two",
        "feature1/test_b.py::test_two",
        "feature2/test_b.py::test_two",
        "feature0/test_a.py::test_three",
        "feature1/test_a.py::test_three",
        "feature2/test_a.py::test_three",
        "feature0/test_a.py::test_four",
        "feature1/test_a.py::test_four",
        "feature2/test_a.py::test_four",
    )
    assert_test_order(expected, out.replace("\\", "/"))


def test_dir_level0(fixture_path, capsys):
    """Same as session scope."""
    args = ["-v", "--order-scope-level={}".format(DIR_BASE), fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "feature0/test_b.py::test_one",
        "feature1/test_b.py::test_one",
        "feature2/test_b.py::test_one",
        "feature0/test_b.py::test_two",
        "feature1/test_b.py::test_two",
        "feature2/test_b.py::test_two",
        "feature0/test_a.py::test_three",
        "feature1/test_a.py::test_three",
        "feature2/test_a.py::test_three",
        "feature0/test_a.py::test_four",
        "feature1/test_a.py::test_four",
        "feature2/test_a.py::test_four",
    )
    assert_test_order(expected, out.replace("\\", "/"))


def test_dir_level1(fixture_path, capsys):
    """Orders per feature path."""
    args = ["-v", "--order-scope-level={}".format(DIR_BASE + 1), fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "feature0/test_b.py::test_one",
        "feature0/test_b.py::test_two",
        "feature0/test_a.py::test_three",
        "feature0/test_a.py::test_four",
        "feature1/test_b.py::test_one",
        "feature1/test_b.py::test_two",
        "feature1/test_a.py::test_three",
        "feature1/test_a.py::test_four",
        "feature2/test_b.py::test_one",
        "feature2/test_b.py::test_two",
        "feature2/test_a.py::test_three",
        "feature2/test_a.py::test_four",
    )
    assert_test_order(expected, out.replace("\\", "/"))


def test_dir_level2(fixture_path, capsys):
    """Same as module scope."""
    args = ["-v", "--order-scope-level={}".format(DIR_BASE + 2), fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "feature0/test_a.py::test_three",
        "feature0/test_a.py::test_four",
        "feature0/test_b.py::test_one",
        "feature0/test_b.py::test_two",
        "feature1/test_a.py::test_three",
        "feature1/test_a.py::test_four",
        "feature1/test_b.py::test_one",
        "feature1/test_b.py::test_two",
        "feature2/test_a.py::test_three",
        "feature2/test_a.py::test_four",
        "feature2/test_b.py::test_one",
        "feature2/test_b.py::test_two",
    )
    assert_test_order(expected, out.replace("\\", "/"))


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="Warning does not appear in output in pytest < 3.8")
def test_invalid_scope(fixture_path, capsys):
    args = ["-s", "--order-scope=module", "--order-scope-level=1",
            fixture_path]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert ("UserWarning: order-scope-level cannot be used "
            "together with --order-scope=module") in out
