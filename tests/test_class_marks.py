def test_ordinal_class_marks(item_names_for):
    tests_content = """
        import pytest

        @pytest.mark.order(1)
        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        @pytest.mark.order(0)
        class Test2:
            def test_1(self): pass
            def test_2(self): pass

        """
    assert item_names_for(tests_content) == [
        "Test2::test_1",
        "Test2::test_2",
        "Test1::test_1",
        "Test1::test_2",
    ]


def test_after_class_mark(item_names_for):
    tests_content = """
        import pytest

        @pytest.mark.order(after="Test2")
        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test2::test_1",
        "Test2::test_2",
        "Test1::test_1",
        "Test1::test_2",
    ]


def test_invalid_class_mark(item_names_for, capsys):
    tests_content = """
        import pytest

        @pytest.mark.order(after="Test3")
        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test1::test_1",
        "Test1::test_2",
        "Test2::test_1",
        "Test2::test_2",
    ]
    out, err = capsys.readouterr()
    assert (
        "WARNING: cannot execute 'test_2' relative to others: "
        "'Test3' - ignoring the marker" in out
    )


def test_before_class_mark(item_names_for):
    tests_content = """
        import pytest

        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        @pytest.mark.order(before="Test1")
        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test2::test_1",
        "Test2::test_2",
        "Test1::test_1",
        "Test1::test_2",
    ]


def test_after_class_marks_for_single_test_in_class(item_names_for):
    tests_content = """
        import pytest

        @pytest.mark.order(after="Test2::test_1")
        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test2::test_1",
        "Test1::test_1",
        "Test1::test_2",
        "Test2::test_2",
    ]


def test_before_class_marks_for_single_test_in_class(item_names_for):
    tests_content = """
        import pytest

        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        @pytest.mark.order(before="Test1::test_2")
        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test1::test_1",
        "Test2::test_1",
        "Test2::test_2",
        "Test1::test_2",
    ]


def test_after_class_marks_for_single_test(item_names_for):
    tests_content = """
        import pytest

        @pytest.mark.order(after="test_1")
        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        def test_1(): pass

        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "test_1",
        "Test1::test_1",
        "Test1::test_2",
        "Test2::test_1",
        "Test2::test_2",
    ]


def test_before_class_marks_for_single_test(item_names_for):
    tests_content = """
        import pytest

        def test_1(): pass

        class Test1:
            def test_1(self): pass
            def test_2(self): pass

        @pytest.mark.order(before="test_1")
        class Test2:
            def test_1(self): pass
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test2::test_1",
        "Test2::test_2",
        "test_1",
        "Test1::test_1",
        "Test1::test_2",
    ]


def test_rel_class_mark_with_order_mark(item_names_for):
    tests_content = """
        import pytest

        class Test1:
            def test_1(self): pass

            def test_2(self): pass

        @pytest.mark.order(before="Test1")
        class Test2:
            @pytest.mark.order(2)
            def test_1(self): pass

            @pytest.mark.order(1)
            def test_2(self): pass
        """
    assert item_names_for(tests_content) == [
        "Test2::test_2",
        "Test2::test_1",
        "Test1::test_1",
        "Test1::test_2",
    ]
