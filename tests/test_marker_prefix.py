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


@pytest.fixture
def marker_test(test_path, marker_test_file):
    test_path.makepyfile(test_marker=marker_test_file)
    yield test_path


def test_no_ordering(marker_test_file, item_names_for):
    assert item_names_for(marker_test_file) == ["test_a", "test_b", "test_c"]


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


def test_mix_marker_prefix_with_order_marks(test_path):
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
