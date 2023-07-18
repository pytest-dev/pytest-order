import pytest


@pytest.fixture
def fixture_path(test_path):
    test_path.makepyfile(
        test_named_dep1=(
            """
            import pytest

            class Test1:
                @pytest.mark.dependency(depends=['Test2_test2'])
                def test_one(self):
                    assert True

                def test_two(self):
                    assert True

            class Test2:
                def test_one(self):
                    assert True

                @pytest.mark.dependency(
                    name='Test2_test2',
                    depends=['dep3_test_two'],
                    scope='session',
                )
                def test_two(self):
                    assert True
            """
        ),
        test_named_dep2=(
            """
            import pytest

            @pytest.mark.dependency(
                depends=['dep3_test_two'], scope='session'
            )
            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
        test_named_dep3=(
            """
            import pytest

            def test_one():
                assert True

            @pytest.mark.dependency(name='dep3_test_two')
            def test_two():
                assert True
            """
        ),
        test_named_dep4=(
            """
            import pytest

            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
    )
    yield test_path


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="pytest-dependency < 0.5 does not support session scope",
)
def test_session_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-dependencies")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_named_dep1.py::Test1::test_two PASSED",
            "test_named_dep1.py::Test2::test_one PASSED",
            "test_named_dep2.py::test_two PASSED",
            "test_named_dep3.py::test_one PASSED",
            "test_named_dep3.py::test_two PASSED",
            "test_named_dep1.py::Test2::test_two PASSED",
            "test_named_dep1.py::Test1::test_one PASSED",
            "test_named_dep2.py::test_one PASSED",
            "test_named_dep4.py::test_one PASSED",
            "test_named_dep4.py::test_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="pytest-dependency < 0.5 does not support session scope",
)
def test_module_group_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v", "--order-dependencies", "--order-group-scope=module"
    )
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_named_dep3.py::test_one PASSED",
            "test_named_dep3.py::test_two PASSED",
            "test_named_dep1.py::Test1::test_two PASSED",
            "test_named_dep1.py::Test2::test_one PASSED",
            "test_named_dep1.py::Test2::test_two PASSED",
            "test_named_dep1.py::Test1::test_one PASSED",
            "test_named_dep2.py::test_one PASSED",
            "test_named_dep2.py::test_two PASSED",
            "test_named_dep4.py::test_one PASSED",
            "test_named_dep4.py::test_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="pytest-dependency < 0.5 does not support session scope",
)
def test_class_group_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v", "--order-dependencies", "--order-group-scope=class"
    )
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_named_dep3.py::test_one PASSED",
            "test_named_dep3.py::test_two PASSED",
            "test_named_dep1.py::Test2::test_one PASSED",
            "test_named_dep1.py::Test2::test_two PASSED",
            "test_named_dep1.py::Test1::test_one PASSED",
            "test_named_dep1.py::Test1::test_two PASSED",
            "test_named_dep2.py::test_one PASSED",
            "test_named_dep2.py::test_two PASSED",
            "test_named_dep4.py::test_one PASSED",
            "test_named_dep4.py::test_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="pytest-dependency < 0.5 does not support session scope",
)
def test_class_group_scope_module_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v",
        "--order-dependencies",
        "--order-group-scope=class",
        "--order-scope=module",
    )
    result.assert_outcomes(passed=7, skipped=3)
    result.stdout.fnmatch_lines(
        [
            "test_named_dep1.py::Test2::test_one PASSED",
            "test_named_dep1.py::Test2::test_two SKIPPED*",
            "test_named_dep1.py::Test1::test_one SKIPPED*",
            "test_named_dep1.py::Test1::test_two PASSED",
            "test_named_dep2.py::test_one SKIPPED*",
            "test_named_dep2.py::test_two PASSED",
            "test_named_dep3.py::test_one PASSED",
            "test_named_dep3.py::test_two PASSED",
            "test_named_dep4.py::test_one PASSED",
            "test_named_dep4.py::test_two PASSED",
        ]
    )
