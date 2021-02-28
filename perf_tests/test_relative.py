import os
import shutil
from unittest import mock

import pytest

import pytest_order
from perf_tests.util import TimedSorter
from tests.utils import write_test


@pytest.fixture
def fixture_path_relative(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("relative_perf"))
    for module_index in range(10):
        testname = os.path.join(
            fixture_path, "test_relative_perf{}.py".format(module_index))
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
        write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@mock.patch("pytest_order.Sorter", TimedSorter)
def test_performance_relative(fixture_path_relative):
    args = [fixture_path_relative]
    pytest.main(args, [pytest_order])
    assert TimedSorter.elapsed < 1.2
