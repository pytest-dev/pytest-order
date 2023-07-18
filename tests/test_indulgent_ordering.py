def test_run_marker_registered(test_path):
    test_path.makepyfile(
        test_failing=(
            """
            import pytest

            @pytest.mark.order("second")
            def test_me_second():
                assert True

            def test_that_fails():
                assert False

            @pytest.mark.order("first")
            def test_me_first():
                assert True
            """
        )
    )
    result = test_path.runpytest("-v")
    result.assert_outcomes(passed=2, failed=1)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_that_fails FAILED",
        ]
    )

    result = test_path.runpytest("-v", "--ff", "--indulgent-ordering")
    result.assert_outcomes(passed=2, failed=1)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_that_fails FAILED",
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
        ]
    )
