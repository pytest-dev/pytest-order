# -*- coding: utf-8 -*-

import pytest


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
    warning = ("cannot execute test relative to others: "
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
    warning = ("cannot execute test relative to others: "
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
