from unittest import mock
from textwrap import dedent

import pytest
from perf_tests.util import TimedSorter

pytest_plugins = ["pytester"]


@pytest.fixture
def fixture_path_ordinal(testdir):
    for i_mod in range(10):
        test_name = testdir.tmpdir.join("test_performance{}.py".format(i_mod))
        test_contents = "import pytest\n"
        for i in range(100):
            test_contents += dedent(
                """
                @pytest.mark.order({})
                def test_{}():
                    assert True
                """
            ).format(50 - i, i)
        test_name.write(test_contents)
    yield testdir


@mock.patch("pytest_order.plugin.Sorter", TimedSorter)
def test_performance_ordinal(fixture_path_ordinal):
    TimedSorter.nr_marks = 1000
    fixture_path_ordinal.runpytest("--quiet")
    assert TimedSorter.elapsed < 0.02
