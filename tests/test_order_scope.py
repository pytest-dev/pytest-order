import pytest


@pytest.fixture
def fixture_path(test_path):
    test_path.makepyfile(
        test_classes=(
            """
            import pytest

            class Test1:
                @pytest.mark.order("last")
                def test_two(self):
                    assert True

                @pytest.mark.order("first")
                def test_one(self):
                    assert True

            class Test2:
                @pytest.mark.order("last")
                def test_two(self):
                    assert True

                @pytest.mark.order("first")
                def test_one(self):
                    assert True

            @pytest.mark.order("last")
            def test_two():
                assert True

            @pytest.mark.order("first")
            def test_one():
                assert True
            """
        ),
        test_functions1=(
            """
            import pytest

            @pytest.mark.order("last")
            def test1_two():
                assert True

            @pytest.mark.order("first")
            def test1_one():
                assert True
            """
        ),
        test_functions2=(
            """
            import pytest

            @pytest.mark.order("last")
            def test2_two():
                assert True

            @pytest.mark.order("first")
            def test2_one():
                assert True
            """
        ),
    )
    yield test_path


def test_session_scope(fixture_path):
    result = fixture_path.runpytest("-v")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_classes.py::Test1::test_one PASSED",
            "test_classes.py::Test2::test_one PASSED",
            "test_classes.py::test_one PASSED",
            "test_functions1.py::test1_one PASSED",
            "test_functions2.py::test2_one PASSED",
            "test_classes.py::Test1::test_two PASSED",
            "test_classes.py::Test2::test_two PASSED",
            "test_classes.py::test_two PASSED",
            "test_functions1.py::test1_two PASSED",
            "test_functions2.py::test2_two PASSED",
        ]
    )


def test_module_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-scope=module")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_classes.py::Test1::test_one PASSED",
            "test_classes.py::Test2::test_one PASSED",
            "test_classes.py::test_one PASSED",
            "test_classes.py::Test1::test_two PASSED",
            "test_classes.py::Test2::test_two PASSED",
            "test_classes.py::test_two PASSED",
            "test_functions1.py::test1_one PASSED",
            "test_functions1.py::test1_two PASSED",
            "test_functions2.py::test2_one PASSED",
            "test_functions2.py::test2_two PASSED",
        ]
    )


def test_class_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-scope=class")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_classes.py::Test1::test_one PASSED",
            "test_classes.py::Test1::test_two PASSED",
            "test_classes.py::Test2::test_one PASSED",
            "test_classes.py::Test2::test_two PASSED",
            "test_classes.py::test_one PASSED",
            "test_classes.py::test_two PASSED",
            "test_functions1.py::test1_one PASSED",
            "test_functions1.py::test1_two PASSED",
            "test_functions2.py::test2_one PASSED",
            "test_functions2.py::test2_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="Warning does not appear in output in pytest < 3.8",
)
def test_invalid_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-scope=function")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        ["*UserWarning: Unknown order scope 'function', ignoring it.*"]
    )
