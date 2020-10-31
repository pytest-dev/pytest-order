# -*- coding: utf-8 -*-
import os

import pytest

import pytest_order


def fixture_path():
    base_path = os.path.split(os.path.dirname(__file__))[0]
    return os.path.join(base_path, "fixture")


def test_session_scope(capsys):
    args = ["-v", fixture_path()]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    i_class1_one = out.index("test_classes.py::Test1::test_one")
    i_class2_one = out.index("test_classes.py::Test2::test_one")
    i_noclass_one = out.index("test_classes.py::test_one")
    i_func1_one = out.index("test_functions1.py::test_one")
    i_func2_one = out.index("test_functions2.py::test_one")
    i_class1_two = out.index("test_classes.py::Test1::test_two")
    i_class2_two = out.index("test_classes.py::Test2::test_two")
    i_noclass_two = out.index("test_classes.py::test_two")
    i_func1_two = out.index("test_functions1.py::test_two")
    i_func2_two = out.index("test_functions2.py::test_two")
    assert (i_class1_one < i_class2_one < i_noclass_one
            < i_func1_one < i_func2_one
            < i_class1_two < i_class2_two < i_noclass_two
            < i_func1_two < i_func2_two)


def test_module_scope(capsys):
    args = ["-v", "--order-scope=module", fixture_path()]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    print('module:', out)
    i_class1_one = out.index("test_classes.py::Test1::test_one")
    i_class2_one = out.index("test_classes.py::Test2::test_one")
    i_noclass_one = out.index("test_classes.py::test_one")
    i_func1_one = out.index("test_functions1.py::test_one")
    i_func2_one = out.index("test_functions2.py::test_one")
    i_class1_two = out.index("test_classes.py::Test1::test_two")
    i_class2_two = out.index("test_classes.py::Test2::test_two")
    i_noclass_two = out.index("test_classes.py::test_two")
    i_func1_two = out.index("test_functions1.py::test_two")
    i_func2_two = out.index("test_functions2.py::test_two")
    assert (i_class1_one < i_class2_one < i_noclass_one
            < i_class1_two < i_class2_two < i_noclass_two
            < i_func1_one < i_func1_two
            < i_func2_one < i_func2_two)


def test_class_scope(capsys):
    args = ["-v", "--order-scope=class", fixture_path()]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    print('class:', out)
    i_class1_one = out.index("test_classes.py::Test1::test_one")
    i_class2_one = out.index("test_classes.py::Test2::test_one")
    i_noclass_one = out.index("test_classes.py::test_one")
    i_func1_one = out.index("test_functions1.py::test_one")
    i_func2_one = out.index("test_functions2.py::test_one")
    i_class1_two = out.index("test_classes.py::Test1::test_two")
    i_class2_two = out.index("test_classes.py::Test2::test_two")
    i_noclass_two = out.index("test_classes.py::test_two")
    i_func1_two = out.index("test_functions1.py::test_two")
    i_func2_two = out.index("test_functions2.py::test_two")
    assert (i_class1_one < i_class1_two < i_class2_one < i_class2_two
            < i_noclass_one < i_noclass_two
            < i_func1_one < i_func1_two
            < i_func2_one < i_func2_two)


@pytest.mark.skipif(pytest.__version__.startswith(("3.6.", "3.7.")),
                    reason="Warning does  not appear in out in pytest < 3.8")
def test_invalid_scope(capsys):
    args = ["-v", "--order-scope=function", fixture_path()]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert "UserWarning: Unknown order scope 'function', ignoring it." in out
