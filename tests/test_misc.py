import re

import pytest

import pytest_order


def test_version_exists():
    assert hasattr(pytest_order, "__version__")


def test_version_valid():
    # check for PEP 440 conform version
    assert re.match(
        r"\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d)?(\.dev\d)?$",
        pytest_order.__version__,
    )


def test_markers_registered(capsys):
    pytest.main(["--markers"])
    out, err = capsys.readouterr()
    assert "@pytest.mark.order" in out
    # only order is supported as marker
    assert out.count("Provided by pytest-order.") == 1


def tests_working_without_dependency(test_path):
    """Make sure no other plugins are needed in settings."""
    test_path.makepyfile(
        test_a=(
            """
            import pytest

            def test_a(): pass

            @pytest.mark.order(0)
            def test_b(): pass
            """
        )
    )
    result = test_path.runpytest(
        "-v", "-p", "no:xdist", "-p", "no:dependency", "-p", "no:mock"
    )
    result.stdout.fnmatch_lines(
        [
            "test_a.py::test_b PASSED",
            "test_a.py::test_a PASSED",
        ]
    )
