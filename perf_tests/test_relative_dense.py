from unittest import mock

import pytest
from perf_tests.util import TimedSorter

pytest_plugins = ["pytester"]


@pytest.fixture
def fixture_path_relative_dense(testdir):
    for i_mod in range(10):
        test_name = testdir.tmpdir.join(
            "test_relative_dense_perf{}.py".format(i_mod))
        test_contents = """
import pytest
"""
        for i in range(90):
            test_contents += """
@pytest.mark.order(after="test_{}")
def test_{}():
    assert True
""".format(i + 10, i)
        for i in range(10):
            test_contents += """
def test_{}():
    assert True
""".format(i + 90)
        test_name.write(test_contents)
    yield testdir


@mock.patch("pytest_order.plugin.Sorter", TimedSorter)
def test_performance_relative(fixture_path_relative_dense):
    """Test performance of after markers that mostly point to tests with
    another order mark, so items are evaluated multiple times."""
    TimedSorter.nr_marks = 900
    fixture_path_relative_dense.runpytest("--quiet")
    assert TimedSorter.elapsed < 0.15
