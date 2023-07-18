import pytest


@pytest.fixture
def fixture_path(test_path):
    test_path.makepyfile(
        test_clss=(
            """
            import pytest

            class Test1:
                @pytest.mark.order(2)
                def test_two(self):
                    assert True

                def test_one(self):
                    assert True

            class Test2:
                def test_two(self):
                    assert True

                @pytest.mark.order(1)
                def test_one(self):
                    assert True

            @pytest.mark.order(-1)
            def test_two():
                assert True

            def test_one():
                assert True
            """
        ),
        test_fcts1=(
            """
            import pytest

            @pytest.mark.order(5)
            def test1_two():
                assert True

            def test1_one():
                assert True
            """
        ),
        test_fcts2=(
            """
            import pytest

            @pytest.mark.order(0)
            def test2_two():
                assert True

            def test2_one():
                assert True
            """
        ),
        test_fcts3=(
            """
            import pytest

            @pytest.mark.order(-2)
            def test3_two():
                assert True

            def test3_one():
                assert True
            """
        ),
        test_fcts4=(
            """
            import pytest

            def test4_one():
                assert True

            def test4_two():
                assert True
            """
        ),
    )
    yield test_path


def test_session_scope(fixture_path):
    result = fixture_path.runpytest("-v")
    result.assert_outcomes(passed=14, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_fcts2.py::test2_two PASSED",
            "test_clss.py::Test2::test_one PASSED",
            "test_clss.py::Test1::test_two PASSED",
            "test_fcts1.py::test1_two PASSED",
            "test_clss.py::Test1::test_one PASSED",
            "test_clss.py::Test2::test_two PASSED",
            "test_clss.py::test_one PASSED",
            "test_fcts1.py::test1_one PASSED",
            "test_fcts2.py::test2_one PASSED",
            "test_fcts3.py::test3_one PASSED",
            "test_fcts4.py::test4_one PASSED",
            "test_fcts4.py::test4_two PASSED",
            "test_fcts3.py::test3_two PASSED",
            "test_clss.py::test_two PASSED",
        ]
    )


def test_module_group_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-group-scope=module")
    result.assert_outcomes(passed=14, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_fcts2.py::test2_two PASSED",
            "test_fcts2.py::test2_one PASSED",
            "test_clss.py::Test2::test_one PASSED",
            "test_clss.py::Test1::test_two PASSED",
            "test_clss.py::Test1::test_one PASSED",
            "test_clss.py::Test2::test_two PASSED",
            "test_clss.py::test_one PASSED",
            "test_clss.py::test_two PASSED",
            "test_fcts1.py::test1_two PASSED",
            "test_fcts1.py::test1_one PASSED",
            "test_fcts4.py::test4_one PASSED",
            "test_fcts4.py::test4_two PASSED",
            "test_fcts3.py::test3_one PASSED",
            "test_fcts3.py::test3_two PASSED",
        ]
    )


def test_class_group_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-group-scope=class")
    result.assert_outcomes(passed=14, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_fcts2.py::test2_two PASSED",
            "test_fcts2.py::test2_one PASSED",
            "test_clss.py::Test2::test_one PASSED",
            "test_clss.py::Test2::test_two PASSED",
            "test_clss.py::Test1::test_two PASSED",
            "test_clss.py::Test1::test_one PASSED",
            "test_clss.py::test_one PASSED",
            "test_clss.py::test_two PASSED",
            "test_fcts1.py::test1_two PASSED",
            "test_fcts1.py::test1_one PASSED",
            "test_fcts4.py::test4_one PASSED",
            "test_fcts4.py::test4_two PASSED",
            "test_fcts3.py::test3_one PASSED",
            "test_fcts3.py::test3_two PASSED",
        ]
    )


def test_class_group_scope_module_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v", "--order-group-scope=class", "--order-scope=module"
    )
    result.assert_outcomes(passed=14, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_clss.py::Test2::test_one PASSED",
            "test_clss.py::Test2::test_two PASSED",
            "test_clss.py::Test1::test_two PASSED",
            "test_clss.py::Test1::test_one PASSED",
            "test_clss.py::test_one PASSED",
            "test_clss.py::test_two PASSED",
            "test_fcts1.py::test1_two PASSED",
            "test_fcts1.py::test1_one PASSED",
            "test_fcts2.py::test2_two PASSED",
            "test_fcts2.py::test2_one PASSED",
            "test_fcts3.py::test3_one PASSED",
            "test_fcts3.py::test3_two PASSED",
            "test_fcts4.py::test4_one PASSED",
            "test_fcts4.py::test4_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="Warning does not appear in output in pytest < 3.8",
)
def test_invalid_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-group-scope=function")
    result.assert_outcomes(passed=14, failed=0)
    result.stdout.fnmatch_lines(
        ["*UserWarning: Unknown order group scope 'function', ignoring it.*"]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="Warning does not appear in output in pytest < 3.8",
)
def test_ignored_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v", "--order-group-scope=session", "--order-scope=module"
    )
    result.assert_outcomes(passed=14, failed=0)
    result.stdout.fnmatch_lines(
        ["*UserWarning: Group scope is larger than order scope, ignoring it."]
    )
