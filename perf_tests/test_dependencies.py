import os
import shutil
from unittest import mock

import pytest

import pytest_order
from perf_tests.util import TimedSorter
from tests.utils import write_test


@pytest.fixture
def fixture_path_relative(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("dep_perf_sparse"))
    for module_index in range(10):
        testname = os.path.join(
            fixture_path, "test_dep_perf{}.py".format(module_index))
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
        write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@mock.patch("pytest_order.Sorter", TimedSorter)
def test_performance_dependency(fixture_path_relative):
    """Test performance of dependency markers that point to tests without
    an order mark (same as for test_relative does for after markers)."""
    args = ["--order-dependencies", fixture_path_relative]
    TimedSorter.nr_marks = 400
    pytest.main(args, [pytest_order])
    assert TimedSorter.elapsed < 0.4
