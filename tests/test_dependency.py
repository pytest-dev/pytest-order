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
    yield (
        """
        import pytest

        @pytest.mark.dependency()
        def test_a():
            pass

        @pytest.mark.dependency(depends=["test_a"])
        def test_b():
            pass
        """
    )


def test_dependency_already_ordered_default(ordered_test, item_names_for):
    assert item_names_for(ordered_test) == ["test_a", "test_b"]


def test_dependency_already_ordered_with_ordering(
    ordered_test, item_names_for, order_dependencies
):
    assert item_names_for(ordered_test) == ["test_a", "test_b"]


@pytest.fixture(scope="module")
def order_dependency_test():
    yield (
        """
        import pytest

        @pytest.mark.dependency(depends=["test_b"])
        def test_a():
            pass

        @pytest.mark.dependency()
        def test_b():
            pass
        """
    )


def test_order_dependency_default(order_dependency_test, item_names_for):
    assert item_names_for(order_dependency_test) == ["test_a", "test_b"]


def test_order_dependency_ordered(
    order_dependency_test, item_names_for, order_dependencies
):
    assert item_names_for(order_dependency_test) == ["test_b", "test_a"]


@pytest.fixture(scope="module")
def multiple_dependencies_test():
    yield (
        """
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
    )


def test_order_multiple_dependencies_default(
    multiple_dependencies_test, item_names_for
):
    assert item_names_for(multiple_dependencies_test) == ["test_a", "test_b", "test_c"]


def test_order_multiple_dependencies_ordered(
    multiple_dependencies_test, item_names_for, order_dependencies
):
    assert item_names_for(multiple_dependencies_test) == ["test_b", "test_c", "test_a"]


@pytest.fixture
def no_dep_marks(test_path):
    test_path.makepyfile(
        test_auto=(
            """
            import pytest

            @pytest.mark.dependency(depends=["test_b", "test_c"])
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


def test_order_dependencies_no_auto_mark(no_dep_marks):
    no_dep_marks.makefile(
        ".ini",
        pytest=(
            """
            [pytest]
            automark_dependency = 0
            console_output_style = classic
            """
        ),
    )
    result = no_dep_marks.runpytest("-v", "--order-dependencies")
    result.assert_outcomes(passed=2, skipped=1)
    result.stdout.fnmatch_lines(
        [
            "test_auto.py::test_a SKIPPED*",
            "test_auto.py::test_b PASSED",
            "test_auto.py::test_c PASSED",
        ]
    )


def test_order_dependencies_auto_mark(no_dep_marks):
    no_dep_marks.makefile(
        ".ini",
        pytest=(
            """
            [pytest]
            automark_dependency = 1
            console_output_style = classic
            """
        ),
    )
    result = no_dep_marks.runpytest("-v", "--order-dependencies")
    result.assert_outcomes(passed=3, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_auto.py::test_b PASSED",
            "test_auto.py::test_c PASSED",
            "test_auto.py::test_a PASSED",
        ]
    )


@pytest.fixture(scope="module")
def named_dependency_test():
    yield (
        """
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
    )


def test_order_named_dependency_default(named_dependency_test, item_names_for):
    assert item_names_for(named_dependency_test) == ["test_a", "test_b", "test_c"]


def test_order_named_dependency_ordered(
    named_dependency_test, item_names_for, order_dependencies
):
    assert item_names_for(named_dependency_test) == ["test_b", "test_a", "test_c"]


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
    assert item_names_for(tests_content) == [
        "Test::test_c",
        "Test::test_a",
        "Test::test_b",
    ]


def test_unresolved_dependency_in_class(item_names_for, order_dependencies, capsys):
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
    assert item_names_for(tests_content) == [
        "Test::test_a",
        "Test::test_b",
        "Test::test_c",
    ]
    out, err = capsys.readouterr()
    warning = "Cannot resolve the dependency marker 'test_c' - ignoring it"
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
    assert item_names_for(tests_content) == [
        "Test::test_c",
        "Test::test_a",
        "Test::test_b",
    ]


def test_dependencies_in_classes(item_names_for, order_dependencies):
    tests_content = """
        import pytest

        class TestA:
            @pytest.mark.dependency(depends=["test_2"])
            def test_a(self):
                assert True

            @pytest.mark.dependency(depends=["TestB::test_b"])
            def test_b(self):
                assert True

            def test_c(self):
                assert True

        class TestB:
            @pytest.mark.dependency(name="test_2")
            def test_a(self):
                assert True

            @pytest.mark.dependency()
            def test_b(self):
                assert True

            def test_c(self):
                assert True
        """
    assert item_names_for(tests_content) == [
        "TestA::test_c",
        "TestB::test_a",
        "TestA::test_a",
        "TestB::test_b",
        "TestA::test_b",
        "TestB::test_c",
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
        "TestA::test_b",
        "TestA::test_c",
        "TestA::test_a",
    ]


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="pytest-dependency < 0.5 does not support session scope",
)
def test_named_dependency_in_modules(test_path):
    test_path.makepyfile(
        test_ndep1=(
            """
            import pytest

            class Test1:
                def test_one(self):
                    assert True

                @pytest.mark.dependency(
                    depends=['dep2_test_one'], scope='session'
                )
                def test_two(self):
                    assert True
            """
        ),
        test_ndep2=(
            """
            import pytest

            @pytest.mark.dependency(name='dep2_test_one')
            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
    )

    result = test_path.runpytest("-v", "--order-dependencies")
    result.assert_outcomes(passed=4, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_ndep1.py::Test1::test_one PASSED",
            "test_ndep2.py::test_one PASSED",
            "test_ndep1.py::Test1::test_two PASSED",
            "test_ndep2.py::test_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="pytest-dependency < 0.5 does not support session scope",
)
def test_dependency_in_modules(test_path):
    test_path.makepyfile(
        test_unnamed_dep1=(
            """
            import pytest

            class Test1:
                def test_one(self):
                    assert True

                @pytest.mark.dependency(
                    depends=['test_unnamed_dep2.py::test_one'],
                    scope='session',
                )
                def test_two(self):
                    assert True
            """
        ),
        test_unnamed_dep2=(
            """
            import pytest

            @pytest.mark.dependency
            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
    )

    result = test_path.runpytest("-v", "--order-dependencies")
    result.assert_outcomes(passed=4, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_unnamed_dep1.py::Test1::test_one PASSED",
            "test_unnamed_dep2.py::test_one PASSED",
            "test_unnamed_dep1.py::Test1::test_two PASSED",
            "test_unnamed_dep2.py::test_two PASSED",
        ]
    )


def test_same_dependency_in_modules(test_path):
    # regression test - make sure that the same dependency in different
    # modules works correctly
    test_path.makepyfile(
        test_module_dep1=(
            """
            import pytest

            @pytest.mark.dependency(depends=['test_two'])
            def test_one():
                assert True

            @pytest.mark.dependency
            def test_two():
                assert True
            """
        ),
        test_module_dep2=(
            """
            import pytest

            @pytest.mark.dependency(depends=['test_two'])
            def test_one():
                assert True

            @pytest.mark.dependency
            def test_two():
                assert True
            """
        ),
    )
    result = test_path.runpytest("-v", "--order-dependencies")
    result.assert_outcomes(passed=4, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_module_dep1.py::test_two PASSED",
            "test_module_dep1.py::test_one PASSED",
            "test_module_dep2.py::test_two PASSED",
            "test_module_dep2.py::test_one PASSED",
        ]
    )


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
    assert item_names_for(tests_content) == [
        "Test::test_a",
        "Test::test_b",
        "Test::test_c",
    ]
    out, err = capsys.readouterr()
    warning = "Cannot resolve the dependency marker 'test_3' - ignoring it."
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
