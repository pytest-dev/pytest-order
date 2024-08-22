from unittest import mock
from textwrap import dedent

import pytest
from perf_tests.util import TimedSorter

pytest_plugins = ["pytester"]


@pytest.fixture
def fixture_path_relative_dense(testdir):
    for i_mod in range(10):
        test_name = testdir.tmpdir.join(f"test_relative_dense_perf{i_mod}.py")
        test_contents = "import pytest\n"
        for i in range(90):
            test_contents += dedent(
                f"""
                @pytest.mark.order(after="test_{i + 10}")
                def test_{i}():
                    assert True
                """
            )
        for i in range(10):
            test_contents += dedent(
                f"""
                def test_{i + 90}():
                    assert True
                """
            )
        test_name.write(test_contents)
    yield testdir


@mock.patch("pytest_order.plugin.Sorter", TimedSorter)
def test_performance_relative(fixture_path_relative_dense):
    """Test performance of after markers that mostly point to tests with
    another order mark, so items are evaluated multiple times."""
    TimedSorter.nr_marks = 900
    fixture_path_relative_dense.runpytest("--quiet")
    assert TimedSorter.elapsed < 0.15
