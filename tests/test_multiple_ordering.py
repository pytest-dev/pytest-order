def test_multiple_markers(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order(2)
        def test_1():
            pass

        @pytest.mark.order(1)
        @pytest.mark.order(3)
        def test_2():
            pass
        """
    assert item_names_for(test_content) == [
        "test_2[index=1]",
        "test_1",
        "test_2[index=3]",
    ]


def test_with_relative_markers(item_names_for):
    test_content = """
        import pytest

        def test_1():
            pass

        @pytest.mark.order(before="test_1")
        @pytest.mark.order(2)
        def test_2():
            pass

        @pytest.mark.order(1)
        @pytest.mark.order(before="test_1")
        def test_3():
            pass

        @pytest.mark.order(-1)
        @pytest.mark.order(-3)
        def test_4():
            pass

        @pytest.mark.order(-2)
        @pytest.mark.order(-4)
        def test_5():
            pass
        """
    assert item_names_for(test_content) == [
        "test_3[index=1]",
        "test_2[index=2]",
        "test_3[before=test_1]",
        "test_2[before=test_1]",
        "test_1",
        "test_5[index=-4]",
        "test_4[index=-3]",
        "test_5[index=-2]",
        "test_4[index=-1]",
    ]


def test_multiple_markers_with_parametrization(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order(2)
        def test_1():
            pass

        @pytest.mark.parametrize("arg", ["aaaaa", "bbbbb", "ccccc", "ddddd"])
        @pytest.mark.order(1)
        @pytest.mark.order(-1)
        def test_2(arg):
            pass

        @pytest.mark.order(3)
        def test_3():
            pass
        """
    assert item_names_for(test_content) == [
        "test_2[index=1-aaaaa]",
        "test_2[index=1-bbbbb]",
        "test_2[index=1-ccccc]",
        "test_2[index=1-ddddd]",
        "test_1",
        "test_3",
        "test_2[index=-1-aaaaa]",
        "test_2[index=-1-bbbbb]",
        "test_2[index=-1-ccccc]",
        "test_2[index=-1-ddddd]",
    ]


def test_multiple_markers_in_class(item_names_for):
    test_content = """
        import pytest

        class TestA:
            @pytest.mark.order(1)
            @pytest.mark.order(3)
            def test_1_and_3():
                pass
            @pytest.mark.order(-1)
            def test_4():
                pass

        @pytest.mark.order(2)
        def test_2():
            pass
        """
    assert item_names_for(test_content) == [
        "TestA::test_1_and_3[index=1]",
        "test_2",
        "TestA::test_1_and_3[index=3]",
        "TestA::test_4",
    ]
