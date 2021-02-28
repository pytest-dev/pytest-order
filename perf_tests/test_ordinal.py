import os
import shutil
from unittest import mock

import pytest
import pytest_order
from perf_tests.util import TimedSorter
from tests.utils import write_test


@pytest.fixture
def fixture_path_ordinal(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("ordinal_perf"))
    for module_index in range(10):
        testname = os.path.join(
            fixture_path, "test_performance{}.py".format(module_index))
        test_contents = """
import pytest
"""
        for i in range(100):
            test_contents += """
@pytest.mark.order({})
def test_{}():
    assert True
""".format(50 - i, i)
        write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@mock.patch("pytest_order.Sorter", TimedSorter)
def test_performance_ordinal(fixture_path_ordinal):
    args = [fixture_path_ordinal]
    TimedSorter.nr_marks = 1000
    pytest.main(args, [pytest_order])
    assert TimedSorter.elapsed < 0.02
