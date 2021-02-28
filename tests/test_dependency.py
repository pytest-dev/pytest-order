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


def test_ignore_order_with_dependency(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.dependency()
    def test_a():
        pass

    @pytest.mark.dependency(depends=["test_a"])
    @pytest.mark.order("first")
    def test_b():
        pass
    """
    assert item_names_for(tests_content) == ["test_a", "test_b"]


def test_order_with_dependency(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.dependency(depends=["test_b"])
    @pytest.mark.order("second")
    def test_a():
        pass

    @pytest.mark.dependency()
    def test_b():
        pass
    """
    assert item_names_for(tests_content) == ["test_b", "test_a"]


@pytest.fixture(scope="module")
def ordered_test():
    yield """
    import pytest

    @pytest.mark.dependency()
    def test_a():
        pass

    @pytest.mark.dependency(depends=["test_a"])
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

    @pytest.mark.dependency(depends=["test_b"])
    def test_a():
        pass

    @pytest.mark.dependency()
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

    @pytest.mark.dependency()
    def test_b():
        pass

    @pytest.mark.dependency()
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


def test_dependency_in_class(item_names_for, order_dependencies):
    tests_content = """
    import pytest

    class Test:
        @pytest.mark.dependency(depends=["Test::test_c"])
        def test_a(self):
            assert True

        @pytest.mark.dependency(depends=["Test::test_c"])
        def test_b(self):
            assert True

        @pytest.mark.dependency()
        def test_c(self):
            assert True
    """
    assert item_names_for(tests_content) == ["test_c", "test_a", "test_b"]


def test_unresolved_dependency_in_class(item_names_for, order_dependencies,
                                        capsys):
    tests_content = """
    import pytest

    class Test:
        @pytest.mark.dependency(depends=["test_c"])
        def test_a(self):
            assert True

        @pytest.mark.dependency(depends=["test_c"])
        def test_b(self):
            assert True

        @pytest.mark.dependency()
        def test_c(self):
            assert True
    """
    assert item_names_for(tests_content) == ["test_a", "test_b", "test_c"]
    out, err = capsys.readouterr()
    warning = ("cannot resolve the dependency marker(s): "
               "test_c - ignoring the marker")
    assert warning in out


def test_named_dependency_in_class(item_names_for, order_dependencies):
    tests_content = """
    import pytest

    class Test:
        @pytest.mark.dependency(name="test_1", depends=["test_3"])
        def test_a(self):
            assert True

        @pytest.mark.dependency(name="test_2", depends=["test_3"])
        def test_b(self):
            assert True

        @pytest.mark.dependency(name="test_3")
        def test_c(self):
            assert True
    """
    assert item_names_for(tests_content) == ["test_c", "test_a", "test_b"]


def test_dependencies_in_classes(item_names_for, order_dependencies):
    tests_content = """
    import pytest

    class TestA:
        @pytest.mark.dependency(depends=["test_2"])
        def test_a(self):
            assert True

        @pytest.mark.dependency(depends=["TestB::test_e"])
        def test_b(self):
            assert True

        def test_c(self):
            assert True

    class TestB:
        @pytest.mark.dependency(name="test_2")
        def test_d(self):
            assert True

        @pytest.mark.dependency()
        def test_e(self):
            assert True

        def test_f(self):
            assert True
    """
    assert item_names_for(tests_content) == [
        "test_c", "test_d", "test_a", "test_e", "test_b", "test_f"
    ]


def test_class_scope_dependencies(item_names_for, order_dependencies):
    tests_content = """
    import pytest

    class TestA:
        @pytest.mark.dependency(depends=["test_c"], scope='class')
        def test_a(self):
            assert True

        def test_b(self):
            assert True

        @pytest.mark.dependency
        def test_c(self):
            assert True
    """
    assert item_names_for(tests_content) == [
        "test_b", "test_c", "test_a"
    ]


@pytest.fixture
def fixture_path_named(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("named_dep"))
    testname = os.path.join(fixture_path, "test_ndep1.py")
    test_contents = """
import pytest

class Test1:
    def test_one(self):
        assert True

    @pytest.mark.dependency(depends=['dep2_test_one'], scope='session')
    def test_two(self):
        assert True
"""
    write_test(testname, test_contents)
    test_contents = """
import pytest

@pytest.mark.dependency(name='dep2_test_one')
def test_one():
    assert True

def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_ndep2.py")
    write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="pytest-dependency < 0.5 does not support "
                           "session scope")
def test_named_dependency_in_modules(fixture_path_named, capsys):
    args = ["-v", "--order-dependencies", fixture_path_named]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_ndep1.py::Test1::test_one",
        "test_ndep2.py::test_one",
        "test_ndep1.py::Test1::test_two",
        "test_ndep2.py::test_two",
    )
    assert_test_order(expected, out)
    assert "SKIPPED" not in out


@pytest.fixture
def fixture_path_unnamed(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("unnamed_dep"))
    testname = os.path.join(fixture_path, "test_unnamed_dep1.py")
    nodeid_root = NODEID_ROOT.replace("nodeid_path", "unnamed_dep")
    test_contents = """
import pytest

class Test1:
    def test_one(self):
        assert True

    @pytest.mark.dependency(depends=['{}test_unnamed_dep2.py::test_one'],
                            scope='session')
    def test_two(self):
        assert True
""".format(nodeid_root)
    write_test(testname, test_contents)
    test_contents = """
import pytest

@pytest.mark.dependency
def test_one():
    assert True

def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_unnamed_dep2.py")
    write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.mark.skipif(pytest.__version__.startswith("3.7."),
                    reason="pytest-dependency < 0.5 does not support "
                           "session scope")
def test_dependency_in_modules(fixture_path_unnamed, capsys):
    args = ["-v", "--order-dependencies", fixture_path_unnamed]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_unnamed_dep1.py::Test1::test_one",
        "test_unnamed_dep2.py::test_one",
        "test_unnamed_dep1.py::Test1::test_two",
        "test_unnamed_dep2.py::test_two",
    )
    assert_test_order(expected, out)
    assert "SKIPPED" not in out


@pytest.fixture
def fixture_path_modules_with_same_dep(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("modules_dep"))
    testname = os.path.join(fixture_path, "test_module_dep1.py")
    test_contents = """
import pytest

@pytest.mark.dependency(depends=['test_two'])
def test_one():
    assert True

@pytest.mark.dependency
def test_two():
    assert True
"""
    write_test(testname, test_contents)
    test_contents = """
import pytest

@pytest.mark.dependency(depends=['test_two'])
def test_one():
    assert True

@pytest.mark.dependency
def test_two():
    assert True
    """
    testname = os.path.join(fixture_path, "test_module_dep2.py")
    write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


def test_same_dependency_in_modules(
        fixture_path_modules_with_same_dep, capsys):
    # regression test - make sure that the same dependency in different
    # modules works correctly
    args = ["-v", "--order-dependencies", fixture_path_modules_with_same_dep]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "test_module_dep1.py::test_two",
        "test_module_dep1.py::test_one",
        "test_module_dep2.py::test_two",
        "test_module_dep2.py::test_one",
    )
    assert_test_order(expected, out)
    assert "SKIPPED" not in out


def test_unknown_dependency(item_names_for, order_dependencies, capsys):
    tests_content = """
    import pytest

    class Test:
        def test_a(self):
            assert True

        @pytest.mark.dependency(depends=["test_3"])
        def test_b(self):
            assert True

        def test_c(self):
            assert True
    """
    assert item_names_for(tests_content) == ["test_a", "test_b", "test_c"]
    out, err = capsys.readouterr()
    warning = ("cannot resolve the dependency marker(s): "
               "test_3 - ignoring the marker")
    assert warning in out


def test_unsupported_order_with_dependency(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.dependency(depends=["test_2"])
    @pytest.mark.order("unknown")
    def test_1():
        pass

    def test_2():
        pass
    """
    with pytest.warns(UserWarning, match="Unknown order attribute:'unknown'"):
        assert item_names_for(test_content) == ["test_1", "test_2"]
