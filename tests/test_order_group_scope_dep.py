import pytest


@pytest.fixture
def fixture_path(test_path):
    test_path.makepyfile(
        test_dep1=(
            """
            import pytest

            class Test1:
                @pytest.mark.dependency(depends=['Test2::test_two'])
                def test_one(self):
                    assert True

                @pytest.mark.dependency(depends=['test_three'], scope="class")
                def test_two(self):
                    assert True

                @pytest.mark.dependency
                def test_three(self):
                    assert True

            class Test2:
                def test_one(self):
                    assert True

                @pytest.mark.dependency(
                    depends=['test_dep3.py::test_two'], scope='session'
                )
                def test_two(self):
                    assert True
            """
        ),
        test_dep2=(
            """
            import pytest

            @pytest.mark.dependency(
                depends=['test_dep3.py::test_two'], scope='session'
            )
            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
        test_dep3=(
            """
            import pytest

            def test_one():
                assert True

            @pytest.mark.dependency
            def test_two():
                assert True
            """
        ),
        test_dep4=(
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
    result.assert_outcomes(passed=11, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_dep1.py::Test1::test_three PASSED",
            "test_dep1.py::Test1::test_two PASSED",
            "test_dep1.py::Test2::test_one PASSED",
            "test_dep2.py::test_two PASSED",
            "test_dep3.py::test_one PASSED",
            "test_dep3.py::test_two PASSED",
            "test_dep1.py::Test2::test_two PASSED",
            "test_dep1.py::Test1::test_one PASSED",
            "test_dep2.py::test_one PASSED",
            "test_dep4.py::test_one PASSED",
            "test_dep4.py::test_two PASSED",
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
    result.assert_outcomes(passed=11, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_dep3.py::test_one PASSED",
            "test_dep3.py::test_two PASSED",
            "test_dep1.py::Test1::test_three PASSED",
            "test_dep1.py::Test1::test_two PASSED",
            "test_dep1.py::Test2::test_one PASSED",
            "test_dep1.py::Test2::test_two PASSED",
            "test_dep1.py::Test1::test_one PASSED",
            "test_dep2.py::test_one PASSED",
            "test_dep2.py::test_two PASSED",
            "test_dep4.py::test_one PASSED",
            "test_dep4.py::test_two PASSED",
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
    result.assert_outcomes(passed=11, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_dep3.py::test_one PASSED",
            "test_dep3.py::test_two PASSED",
            "test_dep1.py::Test2::test_one PASSED",
            "test_dep1.py::Test2::test_two PASSED",
            "test_dep1.py::Test1::test_one PASSED",
            "test_dep1.py::Test1::test_three PASSED",
            "test_dep1.py::Test1::test_two PASSED",
            "test_dep2.py::test_one PASSED",
            "test_dep2.py::test_two PASSED",
            "test_dep4.py::test_one PASSED",
            "test_dep4.py::test_two PASSED",
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
    result.assert_outcomes(passed=8, skipped=3)
    result.stdout.fnmatch_lines(
        [
            "test_dep1.py::Test2::test_one PASSED",
            "test_dep1.py::Test2::test_two SKIPPED*",
            "test_dep1.py::Test1::test_one SKIPPED*",
            "test_dep1.py::Test1::test_three PASSED",
            "test_dep1.py::Test1::test_two PASSED",
            "test_dep2.py::test_one SKIPPED*",
            "test_dep2.py::test_two PASSED",
            "test_dep3.py::test_one PASSED",
            "test_dep3.py::test_two PASSED",
            "test_dep4.py::test_one PASSED",
            "test_dep4.py::test_two PASSED",
        ]
    )
