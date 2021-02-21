# -*- coding: utf-8 -*-
import os
import shutil

import pytest

import pytest_order
from tests.utils import write_test, assert_test_order


def test_relative(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(after="test_second")
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.order(before="test_second")
    def test_first():
        pass
    """
    assert item_names_for(test_content) == ["test_first", "test_second",
                                            "test_third"]


def test_relative2(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(after="test_second")
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.order(before="test_second")
    def test_first():
        pass

    def test_five():
        pass

    @pytest.mark.order(before="test_five")
    def test_four():
        pass

    """
    assert item_names_for(test_content) == ["test_first", "test_second",
                                            "test_third", "test_four",
                                            "test_five"]


def test_relative3(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(after="test_second")
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.order(before="test_second")
    def test_first():
        pass

    def test_five():
        pass

    @pytest.mark.order(before="test_five")
    def test_four():
        pass

    """
    assert item_names_for(test_content) == ["test_first", "test_second",
                                            "test_third", "test_four",
                                            "test_five"]


def test_relative_in_class(item_names_for):
    tests_content = """
    import pytest

    class Test:
        @pytest.mark.order(after="test_b")
        def test_a(self):
            pass

        def test_b(self):
            pass

        def test_c(self):
            pass
    """
    assert item_names_for(tests_content) == ["test_b", "test_a", "test_c"]


def test_relative_in_classes(item_names_for):
    tests_content = """
    import pytest

    class TestA:
        @pytest.mark.order(after="TestB::test_e")
        def test_a(self):
            pass

        @pytest.mark.order(after="test_c")
        def test_b(self):
            pass

        def test_c(self):
            pass

    class TestB:
        @pytest.mark.order(before="TestA::test_c")
        def test_d(self):
            pass

        def test_e(self):
            pass

        def test_f(self):
            pass
    """
    assert item_names_for(tests_content) == [
        "test_d", "test_c", "test_b", "test_e", "test_a", "test_f"
    ]


@pytest.fixture
def fixture_path(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("relative"))
    tests_content1 = """
import pytest

class TestA:
    @pytest.mark.order(after="mod2_test.TestB::test_b")
    def test_a(self):
        pass

    @pytest.mark.order(after="sub.mod3_test.test_b")
    def test_b(self):
        pass

    def test_c(self):
        pass
    """
    write_test(os.path.join(fixture_path, "mod1_test.py",), tests_content1)

    tests_content2 = """
import pytest

class TestB:
    @pytest.mark.order(before="mod1_test.TestA::test_c")
    def test_a(self):
        pass

    def test_b(self):
        pass

    def test_c(self):
        pass
    """
    write_test(os.path.join(fixture_path, "mod2_test.py"), tests_content2)

    tests_content3 = """
import pytest

@pytest.mark.order(before="mod2_test.TestB::test_c")
def test_a():
    pass

def test_b():
    pass

def test_c():
    pass
    """
    sub_path = os.path.join(fixture_path, "sub")
    os.mkdir(sub_path)
    write_test(os.path.join(sub_path, "mod3_test.py"), tests_content3)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


def test_relative_in_modules(fixture_path, capsys):
    pytest.main(["-v", fixture_path], [pytest_order])
    out, err = capsys.readouterr()
    expected = (
        "mod2_test.py::TestB::test_a",
        "mod1_test.py::TestA::test_c",
        "mod2_test.py::TestB::test_b",
        "mod1_test.py::TestA::test_a",
        "mod3_test.py::test_a",
        "mod2_test.py::TestB::test_c",
        "mod3_test.py::test_b",
        "mod1_test.py::TestA::test_b",
        "mod3_test.py::test_c",
    )
    assert_test_order(expected, out)


def test_false_insert(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(after="test_a")
    def test_third():
        pass

    def test_second():
        pass

    @pytest.mark.order(before="test_b")
    def test_first():
        pass
    """
    assert item_names_for(test_content) == ["test_third", "test_second",
                                            "test_first"]


def test_mixed_markers1(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(2)
    def test_1():
        pass

    @pytest.mark.order(after="test_1")
    def test_2():
        pass

    @pytest.mark.order(1)
    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_3", "test_1", "test_2"]


def test_mixed_markers2(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(2)
    def test_1():
        pass

    @pytest.mark.order(1)
    def test_2():
        pass

    @pytest.mark.order(before="test_2")
    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_3", "test_2", "test_1"]


def test_combined_markers1(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(2)
    def test_1():
        pass

    def test_2():
        pass

    @pytest.mark.order(index=1, before="test_2")
    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_3", "test_1", "test_2"]


def test_combined_markers2(item_names_for):
    test_content = """
    import pytest

    def test_1():
        pass

    @pytest.mark.order(index=2, before="test_1")
    def test_2():
        pass

    @pytest.mark.order(index=1, before="test_1")
    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_3", "test_2", "test_1"]


def test_combined_markers3(item_names_for):
    test_content = """
    import pytest

    def test_1():
        pass

    @pytest.mark.order(index=2, before="test_3")
    def test_2():
        pass

    @pytest.mark.order(index=1, before="test_1")
    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_2", "test_3", "test_1"]


def test_dependency_after_unknown_test(item_names_for, capsys):
    test_content = """
    import pytest

    @pytest.mark.order(after="some_module.test_2")
    def test_1():
        pass

    def test_2():
        pass
    """
    assert item_names_for(test_content) == ["test_1", "test_2"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "some_module.test_2 - ignoring the marker")
    assert warning in out


def test_dependency_before_unknown_test(item_names_for, capsys):
    test_content = """
    import pytest

    def test_1():
        pass

    @pytest.mark.order(before="test_4")
    def test_2():
        pass

    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_1", "test_2", "test_3"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "test_dependency_before_unknown_test.test_4 - "
               "ignoring the marker")
    assert warning in out


def test_dependency_in_class_before_unknown_test(item_names_for, capsys):
    test_content = """
    import pytest

    class Test:
        def test_1(self):
            pass

        @pytest.mark.order(before="test_4")
        def test_2(self):
            pass

        def test_3(self):
            pass
    """
    assert item_names_for(test_content) == ["test_1", "test_2", "test_3"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "test_dependency_in_class_before_unknown_test.Test::test_4 "
               "- ignoring the marker")
    assert warning in out


def test_dependency_loop(item_names_for, capsys):
    test_content = """
    import pytest

    @pytest.mark.order(after="test_3")
    def test_1():
        pass

    @pytest.mark.order(1)
    def test_2():
        pass

    @pytest.mark.order(before="test_1")
    def test_3():
        pass
    """
    assert item_names_for(test_content) == ["test_2", "test_1", "test_3"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "test_dependency_loop.test_1 test_dependency_loop.test_3 "
               "- ignoring the marker")
    assert warning in out
