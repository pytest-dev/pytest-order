from unittest import mock

import pytest
from perf_tests.util import TimedSorter

pytest_plugins = ["pytester"]


@pytest.fixture
def fixture_path_relative(testdir):
    for i_mod in range(10):
        test_name = testdir.tmpdir.join("test_dep_perf{}.py".format(i_mod))
        test_contents = """
import pytest
"""
        for i in range(40):
            test_contents += """
@pytest.mark.dependency(depends=["test_{}"])
def test_{}():
    assert True
""".format(i + 50, i)
        for i in range(60):
            test_contents += """
@pytest.mark.dependency
def test_{}():
    assert True
""".format(i + 40)
        test_name.write(test_contents)
    yield testdir


@mock.patch("pytest_order.plugin.Sorter", TimedSorter)
def test_performance_dependency(fixture_path_relative):
    """Test performance of dependency markers that point to tests without
    an order mark (same as for test_relative does for after markers)."""
    TimedSorter.nr_marks = 400
    fixture_path_relative.runpytest("--quiet", "--order-dependencies")
    assert TimedSorter.elapsed < 0.15
