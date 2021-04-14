from unittest import mock
from textwrap import dedent

import pytest
from perf_tests.util import TimedSorter

pytest_plugins = ["pytester"]


@pytest.fixture
def fixture_path_relative(testdir):
    for i_mod in range(10):
        test_name = testdir.tmpdir.join(
            "test_relative_perf{}.py".format(i_mod)
        )
        test_contents = "import pytest\n"
        for i in range(40):
            test_contents += dedent(
                """
                @pytest.mark.order(after="test_{}")
                def test_{}():
                    assert True
                """
            ).format(i + 50, i)
        for i in range(60):
            test_contents += dedent(
                """
                def test_{}():
                    assert True
                """
            ).format(i + 40)
        test_name.write(test_contents)
    yield testdir


@mock.patch("pytest_order.plugin.Sorter", TimedSorter)
def test_performance_relative(fixture_path_relative):
    """Test performance of after markers that point to tests without
    an order mark (the usual case)."""
    TimedSorter.nr_marks = 400
    fixture_path_relative.runpytest("--quiet")
    assert TimedSorter.elapsed < 0.15
