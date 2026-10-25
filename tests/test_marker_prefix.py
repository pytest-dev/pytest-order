import pytest


@pytest.fixture(scope="module")
def marker_test_file():
    yield (
        """
        import pytest

        @pytest.mark.my3
        def test_a():
            pass

        @pytest.mark.my1
        def test_b():
            pass

        @pytest.mark.my2
        def test_c():
            pass
        """
    )


@pytest.fixture(scope="module")
def conftest_file():
    yield (
        """
        def pytest_configure(config):
            config.addinivalue_line("markers", "my1: used in marker prefix test")
            config.addinivalue_line("markers", "my2: used in marker prefix test")
            config.addinivalue_line("markers", "my3: used in marker prefix test")
        """
    )


@pytest.fixture
def marker_test(test_path, marker_test_file, conftest_file):
    test_path.makepyfile(conftest=conftest_file)
    test_path.makepyfile(test_marker=marker_test_file)
    yield test_path


def test_no_ordering(marker_test):
    result = marker_test.runpytest("-v")
    result.assert_outcomes(passed=3, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_a PASSED",
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_c PASSED",
        ]
    )


def test_order_with_marker_prefix(marker_test):
    result = marker_test.runpytest("-v", "--order-marker-prefix=my")
    result.assert_outcomes(passed=3, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_c PASSED",
            "test_marker.py::test_a PASSED",
        ]
    )


def test_order_with_marker_prefix_filtered(marker_test):
    result = marker_test.runpytest("-v", "--order-marker-prefix=my", "-m", "my2 or my3")
    result.assert_outcomes(passed=2, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_c PASSED",
            "test_marker.py::test_a PASSED",
        ]
    )


def test_no_ordering_with_incorrect_marker_prefix(marker_test):
    result = marker_test.runpytest("-v", "--order-marker-prefix=mi")
    result.assert_outcomes(passed=3, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_a PASSED",
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_c PASSED",
        ]
    )


def test_no_ordering_with_shorter_marker_prefix(marker_test):
    result = marker_test.runpytest("-v", "--order-marker-prefix=m")
    result.assert_outcomes(passed=3, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_a PASSED",
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_c PASSED",
        ]
    )


def test_marker_prefix_does_not_interfere_with_order_marks(test_path):
    test_path.makepyfile(
        test_marker=(
            """
            import pytest

            @pytest.mark.order(3)
            def test_a():
                pass

            @pytest.mark.order(1)
            def test_b():
                pass

            @pytest.mark.order(2)
            def test_c():
                pass
            """
        )
    )
    result = test_path.runpytest("-v", "--order-marker-prefix=m")
    result.assert_outcomes(passed=3, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_c PASSED",
            "test_marker.py::test_a PASSED",
        ]
    )


def test_mix_marker_prefix_with_order_marks(test_path, conftest_file):
    test_path.makepyfile(conftest=conftest_file)
    test_path.makepyfile(
        test_marker=(
            """
            import pytest

            @pytest.mark.order(3)
            def test_a():
                pass

            @pytest.mark.my1
            def test_b():
                pass

            @pytest.mark.my2
            def test_c():
                pass
            """
        )
    )
    result = test_path.runpytest("-v", "--order-marker-prefix=my")
    result.assert_outcomes(passed=3, skipped=0)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_c PASSED",
            "test_marker.py::test_a PASSED",
        ]
    )


@pytest.mark.parametrize(
    "suffix, expected",
    [
        ("11", ["test_b", "test_a"]),
        ("12", ["test_b", "test_a"]),
        ("", ["test_b", "test_a"]),
        ("1special", ["test_b", "test_a"]),
        ("other", ["test_b", "test_a"]),
        ("0", ["test_a", "test_b"]),
    ],
)
def test_marker_prefix_uses_complete_numeric_suffix(test_path, suffix, expected):
    test_path.makeini(
        f"""
        [pytest]
        console_output_style = classic
        markers =
            my{suffix}: custom order
            my2: custom order
        """
    )
    test_path.makepyfile(
        test_marker=f"""
        import pytest

        @getattr(pytest.mark, "my{suffix}")
        def test_a():
            pass

        @pytest.mark.my2
        def test_b():
            pass
        """
    )
    result = test_path.runpytest("-v", "--order-marker-prefix=my")
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines([f"test_marker.py::{name} PASSED" for name in expected])


def test_marker_prefix_supports_negative_indices(test_path):
    test_path.makeini(
        """
        [pytest]
        console_output_style = classic
        markers =
            my-1: custom order
            my-2: custom order
            my2: custom order
        """
    )
    test_path.makepyfile(
        test_marker="""
        import pytest

        @getattr(pytest.mark, "my-1")
        def test_a():
            pass

        @getattr(pytest.mark, "my-2")
        def test_b():
            pass

        def test_c():
            pass

        @pytest.mark.my2
        def test_d():
            pass
        """
    )
    result = test_path.runpytest("-v", "--order-marker-prefix=my")
    result.assert_outcomes(passed=4)
    result.stdout.fnmatch_lines(
        [
            "test_marker.py::test_d PASSED",
            "test_marker.py::test_c PASSED",
            "test_marker.py::test_b PASSED",
            "test_marker.py::test_a PASSED",
        ]
    )


@pytest.mark.parametrize("suffix", ["", "0", "11", "1special", "-1"])
def test_explicit_order_overrides_marker_prefix(test_path, suffix):
    test_path.makeini(
        f"""
        [pytest]
        console_output_style = classic
        markers =
            my{suffix}: custom order
            my2: custom order
        """
    )
    test_path.makepyfile(
        test_marker=f"""
        import pytest

        @pytest.mark.order(3)
        @getattr(pytest.mark, "my{suffix}")
        def test_a():
            pass

        @pytest.mark.my2
        def test_b():
            pass
        """
    )
    result = test_path.runpytest("-v", "--order-marker-prefix=my")
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines(
        ["test_marker.py::test_b PASSED", "test_marker.py::test_a PASSED"]
    )
