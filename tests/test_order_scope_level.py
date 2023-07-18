from textwrap import dedent

import pytest


@pytest.fixture
def fixture_path(test_path):
    test_a_contents = dedent(
        """
        import pytest

        @pytest.mark.order(4)
        def test_four(): pass

        @pytest.mark.order(3)
        def test_three(): pass
        """
    )
    test_b_contents = dedent(
        """
        import pytest

        @pytest.mark.order(2)
        def test_two(): pass

        @pytest.mark.order(1)
        def test_one(): pass
        """
    )
    for i in range(3):
        sub_path = "feature{}".format(i)
        test_path.mkpydir(sub_path)
        path = test_path.tmpdir.join(sub_path, "test_a.py")
        path.write(test_a_contents)
        path = test_path.tmpdir.join(sub_path, "test_b.py")
        path.write(test_b_contents)
    yield test_path


def test_session_scope(fixture_path):
    result = fixture_path.runpytest("-v")
    result.assert_outcomes(passed=12, failed=0)
    result.stdout.fnmatch_lines(
        [
            "feature0/test_b.py::test_one PASSED",
            "feature1/test_b.py::test_one PASSED",
            "feature2/test_b.py::test_one PASSED",
            "feature0/test_b.py::test_two PASSED",
            "feature1/test_b.py::test_two PASSED",
            "feature2/test_b.py::test_two PASSED",
            "feature0/test_a.py::test_three PASSED",
            "feature1/test_a.py::test_three PASSED",
            "feature2/test_a.py::test_three PASSED",
            "feature0/test_a.py::test_four PASSED",
            "feature1/test_a.py::test_four PASSED",
            "feature2/test_a.py::test_four PASSED",
        ]
    )


def test_dir_level0(fixture_path, capsys):
    """Same as session scope."""
    result = fixture_path.runpytest("-v", "--order-scope-level=0")
    result.assert_outcomes(passed=12, failed=0)
    result.stdout.fnmatch_lines(
        [
            "feature0/test_b.py::test_one PASSED",
            "feature1/test_b.py::test_one PASSED",
            "feature2/test_b.py::test_one PASSED",
            "feature0/test_b.py::test_two PASSED",
            "feature1/test_b.py::test_two PASSED",
            "feature2/test_b.py::test_two PASSED",
            "feature0/test_a.py::test_three PASSED",
            "feature1/test_a.py::test_three PASSED",
            "feature2/test_a.py::test_three PASSED",
            "feature0/test_a.py::test_four PASSED",
            "feature1/test_a.py::test_four PASSED",
            "feature2/test_a.py::test_four PASSED",
        ]
    )


def test_dir_level1(fixture_path, capsys):
    """Orders per feature path."""
    result = fixture_path.runpytest("-v", "--order-scope-level=1")
    result.assert_outcomes(passed=12, failed=0)
    result.stdout.fnmatch_lines(
        [
            "feature0/test_b.py::test_one PASSED",
            "feature0/test_b.py::test_two PASSED",
            "feature0/test_a.py::test_three PASSED",
            "feature0/test_a.py::test_four PASSED",
            "feature1/test_b.py::test_one PASSED",
            "feature1/test_b.py::test_two PASSED",
            "feature1/test_a.py::test_three PASSED",
            "feature1/test_a.py::test_four PASSED",
            "feature2/test_b.py::test_one PASSED",
            "feature2/test_b.py::test_two PASSED",
            "feature2/test_a.py::test_three PASSED",
            "feature2/test_a.py::test_four PASSED",
        ]
    )


def test_dir_level2(fixture_path, capsys):
    """Same as module scope."""
    result = fixture_path.runpytest("-v", "--order-scope-level=2")
    result.assert_outcomes(passed=12, failed=0)
    result.stdout.fnmatch_lines(
        [
            "feature0/test_a.py::test_three PASSED",
            "feature0/test_a.py::test_four PASSED",
            "feature0/test_b.py::test_one PASSED",
            "feature0/test_b.py::test_two PASSED",
            "feature1/test_a.py::test_three PASSED",
            "feature1/test_a.py::test_four PASSED",
            "feature1/test_b.py::test_one PASSED",
            "feature1/test_b.py::test_two PASSED",
            "feature2/test_a.py::test_three PASSED",
            "feature2/test_a.py::test_four PASSED",
            "feature2/test_b.py::test_one PASSED",
            "feature2/test_b.py::test_two PASSED",
        ]
    )


@pytest.mark.skipif(
    pytest.__version__.startswith("3.7."),
    reason="Warning does not appear in output in pytest < 3.8",
)
def test_invalid_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v", "--order-scope=module", "--order-scope-level=1"
    )
    result.assert_outcomes(passed=12, failed=0)
    result.stdout.fnmatch_lines(
        [
            "*UserWarning: order-scope-level cannot be used "
            "together with --order-scope=module*"
        ]
    )
