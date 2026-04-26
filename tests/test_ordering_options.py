def test_order_after_ff(test_path):
    test_path.makepyfile(
        test_failing=(
            """
            import pytest

            @pytest.mark.order("second")
            def test_me_second():
                assert True

            def test_that_fails():
                assert False

            def test_after_failed():
                assert True

            @pytest.mark.order("first")
            def test_me_first():
                assert True
            """
        )
    )
    result = test_path.runpytest("-v")
    result.assert_outcomes(passed=3, failed=1)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_that_fails FAILED",
            "test_failing.py::test_after_failed PASSED",
        ]
    )

    result = test_path.runpytest("-v", "--ff")
    result.assert_outcomes(passed=3, failed=1)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_that_fails FAILED",
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_after_failed PASSED",
        ]
    )

    result = test_path.runpytest("-v", "--ff", "--order-after-ff")
    result.assert_outcomes(passed=3, failed=1)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_that_fails FAILED",
            "test_failing.py::test_after_failed PASSED",
        ]
    )


def test_indulgent_ordering(test_path):
    test_path.makepyfile(
        test_failing=(
            """
            import pytest

            @pytest.mark.order("second")
            def test_me_second():
                assert True

            def test_me_third():
                assert True

            @pytest.mark.order("first")
            def test_me_first():
                assert True

            def test_me_fourth():
                assert True
            """
        )
    )
    result = test_path.runpytest("-v")
    result.assert_outcomes(passed=4)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_me_third PASSED",
            "test_failing.py::test_me_fourth PASSED",
        ]
    )

    result = test_path.runpytest("-v", "-p", "tests.plugin_reverse")
    result.assert_outcomes(passed=4)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_me_first PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_me_fourth PASSED",
            "test_failing.py::test_me_third PASSED",
        ]
    )

    result = test_path.runpytest(
        "-v",
        "-p",
        "tests.plugin_reverse",
        "--indulgent-ordering",
    )
    result.assert_outcomes(passed=4)
    result.stdout.fnmatch_lines(
        [
            "test_failing.py::test_me_fourth PASSED",
            "test_failing.py::test_me_third PASSED",
            "test_failing.py::test_me_second PASSED",
            "test_failing.py::test_me_first PASSED",
        ]
    )
