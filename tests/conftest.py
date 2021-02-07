import uuid

import pytest

import pytest_order

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
    mocker.patch("pytest_order.Settings.initialize")
    yield


@pytest.fixture
def order_dependencies(ignore_settings):
    pytest_order.Settings.order_dependencies = True
    yield
    pytest_order.Settings.order_dependencies = False
