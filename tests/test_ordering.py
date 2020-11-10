# -*- coding: utf-8 -*-

import pytest


def test_no_marks(item_names_for):
    tests_content = """
    def test_1(): pass

    def test_2(): pass
    """

    assert item_names_for(tests_content) == ["test_1", "test_2"]


def test_first_mark(item_names_for):
    tests_content = """
    import pytest

    def test_1(): pass

    @pytest.mark.order("first")
    def test_2(): pass
    """

    assert item_names_for(tests_content) == ["test_2", "test_1"]


def test_last_mark(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order("last")
    def test_1(): pass

    def test_2(): pass
    """

    assert item_names_for(tests_content) == ["test_2", "test_1"]


def test_first_last_marks(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order("last")
    def test_1(): pass

    @pytest.mark.order("first")
    def test_2(): pass

    def test_3(): pass
    """

    assert item_names_for(tests_content) == ["test_2", "test_3", "test_1"]


def test_order_marks(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(-1)
    def test_1(): pass

    @pytest.mark.order(-2)
    def test_2(): pass

    @pytest.mark.order(1)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ["test_3", "test_2", "test_1"]


def test_order_marks_by_index(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(index=-1)
    def test_1(): pass

    @pytest.mark.order(index=-2)
    def test_2(): pass

    @pytest.mark.order(index=1)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ["test_3", "test_2", "test_1"]


def test_non_contiguous_positive(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(10)
    def test_1(): pass

    @pytest.mark.order(20)
    def test_2(): pass

    @pytest.mark.order(5)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ["test_3", "test_1", "test_2"]


def test_non_contiguous_negative(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(-10)
    def test_1(): pass

    @pytest.mark.order(-20)
    def test_2(): pass

    @pytest.mark.order(-5)
    def test_3(): pass
    """

    assert item_names_for(tests_content) == ["test_2", "test_1", "test_3"]


def test_non_contiguous_inc_zero(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(10)
    def test_1(): pass

    @pytest.mark.order(20)
    def test_2(): pass

    @pytest.mark.order(5)
    def test_3(): pass

    @pytest.mark.order(-10)
    def test_4(): pass

    @pytest.mark.order(-20)
    def test_5(): pass

    @pytest.mark.order(-5)
    def test_6(): pass

    @pytest.mark.order(0)
    def test_7(): pass
    """

    assert item_names_for(tests_content) == ["test_7", "test_3", "test_1",
                                             "test_2", "test_5", "test_4",
                                             "test_6"]


def test_non_contiguous_inc_none(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(5)
    def test_1(): pass

    @pytest.mark.order(0)
    def test_2(): pass

    @pytest.mark.order(1)
    def test_3(): pass

    @pytest.mark.order(-1)
    def test_4(): pass

    @pytest.mark.order(-5)
    def test_5(): pass

    def test_6(): pass
    """

    assert item_names_for(tests_content) == ["test_2", "test_3", "test_1",
                                             "test_6", "test_5", "test_4"]


def test_first_mark_class(item_names_for):
    tests_content = """
    import pytest

    def test_1(): pass


    @pytest.mark.order("first")
    class TestSuite(object):

        def test_3(self): pass

        def test_2(self): pass

    """

    assert item_names_for(tests_content) == ["test_3", "test_2", "test_1"]


def test_last_mark_class(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order("last")
    class TestSuite(object):

        def test_1(self): pass

        def test_2(self): pass


    def test_3(): pass
    """

    assert item_names_for(tests_content) == ["test_3", "test_1", "test_2"]


def test_first_last_mark_class(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order("last")
    class TestLast(object):

        def test_1(self): pass

        def test_2(self): pass


    def test_3(): pass


    @pytest.mark.order("first")
    class TestFirst(object):

        def test_4(self): pass

        def test_5(self): pass

    """

    assert item_names_for(tests_content) == ["test_4", "test_5", "test_3",
                                             "test_1", "test_2"]


def test_order_mark_class(item_names_for):
    tests_content = """
    import pytest

    @pytest.mark.order(-1)
    class TestLast(object):

        def test_1(self): pass

        def test_2(self): pass


    @pytest.mark.order(0)
    def test_3(): pass


    @pytest.mark.order(-2)
    class TestFirst(object):

        def test_4(self): pass

        def test_5(self): pass
    """

    assert item_names_for(tests_content) == ["test_3", "test_4", "test_5",
                                             "test_1", "test_2"]


def test_run_ordinals(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order("second_to_last")
    def test_three():
        pass

    @pytest.mark.order("last")
    def test_four():
        pass

    @pytest.mark.order("second")
    def test_two():
        pass

    @pytest.mark.order("first")
    def test_one():
        pass
    """

    assert item_names_for(test_content) == ["test_one", "test_two",
                                            "test_three", "test_four"]


def test_sparse_numbers(item_names_for):
    test_content = """
     import pytest

     @pytest.mark.order(4)
     def test_two():
         assert True

     def test_three():
         assert True

     @pytest.mark.order(2)
     def test_one():
         assert True
    """
    assert item_names_for(test_content) == ["test_one", "test_two",
                                            "test_three"]


def test_quickstart(item_names_for):
    test_content = """
    import pytest

    def test_foo():
        pass

    def test_bar():
        pass
    """
    assert item_names_for(test_content) == ["test_foo", "test_bar"]


def test_quickstart2(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order(2)
    def test_foo():
        pass

    @pytest.mark.order(1)
    def test_bar():
        pass
    """
    assert item_names_for(test_content) == ["test_bar", "test_foo"]


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
        @pytest.mark.order(after='test_b')
        def test_a(self):
            assert True

        def test_b(self):
            assert True

        def test_c(self):
            assert True
    """
    assert item_names_for(tests_content) == ["test_b", "test_a", "test_c"]


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
    assert item_names_for(test_content) == ["test_second", "test_first",
                                            "test_third"]


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


def test_combined_markers(item_names_for):
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


def test_dependency_after_unknown_test(item_names_for, capsys):
    test_content = """
    import pytest

    @pytest.mark.order(after="some_module.test_2")
    def test_1():
        pass

    def test_2():
        pass
    """
    assert item_names_for(test_content) == ["test_2", "test_1"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "some_module.test_2 enqueue them behind the others")
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
    assert item_names_for(test_content) == ["test_1", "test_3", "test_2"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "test_dependency_before_unknown_test.test_4 enqueue them "
               "behind the others")
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
    assert item_names_for(test_content) == ["test_1", "test_3", "test_2"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "test_dependency_in_class_before_unknown_test.Test.test_4 "
               "enqueue them behind the others")
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
    assert item_names_for(test_content) == ["test_2", "test_3", "test_1"]
    out, err = capsys.readouterr()
    warning = ("cannot execute test relative to others: "
               "test_dependency_loop.test_1 test_dependency_loop.test_3 "
               "enqueue them behind the others")
    assert warning in out


def test_unsupported_order(item_names_for):
    test_content = """
    import pytest

    @pytest.mark.order("unknown")
    def test_1():
        pass

    def test_2():
        pass
    """
    with pytest.warns(UserWarning, match="Unknown order attribute:'unknown'"):
        assert item_names_for(test_content) == ["test_1", "test_2"]
