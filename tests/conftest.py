import os
import shutil
import uuid
from random import randint

import pytest

from pytest_order.sorter import SESSION
from tests.utils import write_test

pytest_plugins = ["pytester"]


@pytest.fixture
def item_names_for(testdir):
    def _item_names_for(tests_content):
        items = testdir.getitems(tests_content)
        hook = items[0].config.hook
        hook.pytest_collection_modifyitems(session=items[0].session,
                                           config=items[0].config, items=items)
        return [item.name for item in items]

    return _item_names_for


@pytest.fixture
def test_path(tmpdir):
    path = tmpdir.join("{}.py".format(str(uuid.uuid4())))
    yield str(path)
    path.remove()


@pytest.fixture
def ignore_settings(mocker):
    settings = mocker.patch("pytest_order.sorter.Settings")
    settings.return_value.sparse_ordering = False
    settings.return_value.order_dependencies = False
    settings.return_value.scope = SESSION
    settings.return_value.group_scope = SESSION
    yield settings


@pytest.fixture
def order_dependencies(ignore_settings):
    ignore_settings.return_value.order_dependencies = True
    yield


@pytest.fixture
def get_nodeid(tmpdir_factory):
    """Fixture to get the nodeid from tests created using tmpdir_factory.
    At least under Windows, the nodeid for the same tests differs depending on
    the pytest version and the environment. We need the real nodeid as it is
    used in pytest-dependency session-scoped markers in order to create tests
    passing under different systems.
    """
    fixture_path = str(tmpdir_factory.mktemp("nodeid_path"))
    testname = os.path.join(fixture_path, "test_nodeid.py")
    test_contents = """
import pytest

@pytest.fixture
def nodeid(request):
    yield request.node.nodeid

def test_node(nodeid):
    print("NODEID=!!!{}!!!".format(nodeid))
"""
    write_test(testname, test_contents)

    yield fixture_path
    shutil.rmtree(fixture_path, ignore_errors=True)


def pytest_collection_modifyitems(config, items):
    for item in items:
        if item.name.startswith("test_performance"):
            item.add_marker(pytest.mark.order(randint(-100, 100)))
