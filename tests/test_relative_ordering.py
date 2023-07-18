from textwrap import dedent

import pytest


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
    assert item_names_for(test_content) == ["test_first", "test_second", "test_third"]


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
    assert item_names_for(test_content) == [
        "test_first",
        "test_second",
        "test_third",
        "test_four",
        "test_five",
    ]


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
    assert item_names_for(test_content) == [
        "test_first",
        "test_second",
        "test_third",
        "test_four",
        "test_five",
    ]


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
    assert item_names_for(tests_content) == [
        "Test::test_b",
        "Test::test_a",
        "Test::test_c",
    ]


def test_relative_in_classes(item_names_for):
    tests_content = """
        import pytest

        class TestA:
            @pytest.mark.order(after="TestB::test_b")
            def test_a(self):
                pass

            @pytest.mark.order(after="test_c")
            def test_b(self):
                pass

            def test_c(self):
                pass

        class TestB:
            @pytest.mark.order(before="TestA::test_c")
            def test_a(self):
                pass

            def test_b(self):
                pass

            def test_c(self):
                pass
        """
    assert item_names_for(tests_content) == [
        "TestB::test_a",
        "TestA::test_c",
        "TestA::test_b",
        "TestB::test_b",
        "TestA::test_a",
        "TestB::test_c",
    ]


@pytest.fixture
def fixture_path(test_path):
    test_path.makepyfile(
        mod1_test=(
            """
            import pytest

            class TestA:
                @pytest.mark.order(after="mod2_test.py::TestB::test_b")
                def test_a(self):
                    pass

                @pytest.mark.order(after="sub/mod3_test.py::test_b")
                def test_b(self):
                    pass

                def test_c(self):
                    pass
            """
        ),
        mod2_test=(
            """
            import pytest

            class TestB:
                @pytest.mark.order(before="mod1_test.py::TestA::test_c")
                def test_a(self):
                    pass

                def test_b(self):
                    pass

                def test_c(self):
                    pass
            """
        ),
    )
    test_path.mkpydir("sub")
    path = test_path.tmpdir.join("sub", "mod3_test.py")
    path.write(
        dedent(
            """
        import pytest

        @pytest.mark.order(before="mod2_test.py::TestB::test_c")
        def test_a():
            pass

        def test_b():
            pass

        def test_c():
            pass
        """
        )
    )
    yield test_path


def test_relative_in_modules(fixture_path):
    result = fixture_path.runpytest("-v")
    result.assert_outcomes(passed=9, failed=0)
    result.stdout.fnmatch_lines(
        [
            "mod2_test.py::TestB::test_a PASSED",
            "mod1_test.py::TestA::test_c PASSED",
            "mod2_test.py::TestB::test_b PASSED",
            "mod1_test.py::TestA::test_a PASSED",
            "sub/mod3_test.py::test_a PASSED",
            "mod2_test.py::TestB::test_c PASSED",
            "sub/mod3_test.py::test_b PASSED",
            "mod1_test.py::TestA::test_b PASSED",
            "sub/mod3_test.py::test_c PASSED",
        ]
    )


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
    assert item_names_for(test_content) == ["test_third", "test_second", "test_first"]


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


def test_mixed_markers4(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order(2)
        def test_1():
            pass

        @pytest.mark.order(index=1, after="test_3")
        def test_2():
            pass

        def test_3():
            pass
        """
    assert item_names_for(test_content) == ["test_3", "test_2", "test_1"]


def test_multiple_markers_in_same_test(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order(after=["test_3", "test_4", "test_5"])
        def test_1():
            pass

        def test_2():
            pass

        def test_3():
            pass

        @pytest.mark.order(before=["test_3", "test_2"])
        def test_4():
            pass

        def test_5():
            pass
        """
    assert item_names_for(test_content) == [
        "test_4",
        "test_2",
        "test_3",
        "test_5",
        "test_1",
    ]


def test_dependency_after_unknown_test(item_names_for, capsys):
    test_content = """
        import pytest

        @pytest.mark.order(after="some_module.py::test_2")
        def test_1():
            pass

        def test_2():
            pass
        """
    assert item_names_for(test_content) == ["test_1", "test_2"]
    out, err = capsys.readouterr()
    warning = (
        "cannot execute 'test_1' relative to others: 'some_module.py::test_2' "
        "- ignoring the marker"
    )
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
    warning = (
        "cannot execute 'test_2' relative to others: 'test_4' " "- ignoring the marker"
    )
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
    assert item_names_for(test_content) == [
        "Test::test_1",
        "Test::test_2",
        "Test::test_3",
    ]
    out, err = capsys.readouterr()
    warning = (
        "cannot execute 'test_2' relative to others: 'test_4' " "- ignoring the marker"
    )
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
    warning = (
        "cannot execute test relative to others: " "test_dependency_loop.py::test_3"
    )
    assert warning in out


def test_dependency_on_parametrized_test(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order(after="test_2")
        def test_1():
            pass

        @pytest.mark.parametrize("arg", ["aaaaa", "bbbbb", "ccccc", "ddddd"])
        def test_2(arg):
            pass

        @pytest.mark.order(before="test_2")
        def test_3():
            pass
        """
    assert item_names_for(test_content) == [
        "test_3",
        "test_2[aaaaa]",
        "test_2[bbbbb]",
        "test_2[ccccc]",
        "test_2[ddddd]",
        "test_1",
    ]
