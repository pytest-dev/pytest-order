import os
import shutil
import time

import pytest

import pytest_order
from tests.utils import write_test


@pytest.fixture
def fixture_path_baseline(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("baseline"))
    for module_index in range(10):
        testname = os.path.join(
            fixture_path, "test_baseline{}.py".format(module_index))
        test_contents = """
import pytest
"""
        for i in range(100):
            test_contents += """
def test_{}():
    assert True
""".format(i)
        write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


@pytest.fixture
def fixture_path_relative(tmpdir_factory):
    fixture_path = str(tmpdir_factory.mktemp("relative_perf"))
    for module_index in range(10):
        testname = os.path.join(
            fixture_path, "test_relative_perf{}.py".format(module_index))
        test_contents = """
import pytest
"""
        for i in range(100):
            test_contents += """
@pytest.mark.order(after="test_{}")
def test_{}():
    assert True
""".format(i + 10 % 100, i)
        write_test(testname, test_contents)
    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


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


class TestPerformance:
    base_time = None

    @pytest.mark.order(0)
    def test_baseline_times(self, fixture_path_baseline):
        start_time = time.time()
        args = [fixture_path_baseline]
        pytest.main(args, [pytest_order])
        self.__class__.base_time = time.time() - start_time

    def test_performance_ordinal(self, fixture_path_ordinal):
        start_time = time.time()
        args = [fixture_path_ordinal]
        pytest.main(args, [pytest_order])
        overhead_time = time.time() - start_time - self.__class__.base_time
        print("Overhead per test: {:.3f} ms".format(overhead_time))
        assert overhead_time < 0.4

    def test_performance_relative(self, fixture_path_relative):
        start_time = time.time()
        args = ["--quiet", fixture_path_relative]
        pytest.main(args, [pytest_order])
        overhead_time = time.time() - start_time - self.__class__.base_time
        print("Overhead per test: {:.3f} ms".format(overhead_time))
        assert overhead_time < 0.8
