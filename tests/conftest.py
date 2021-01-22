import uuid

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def item_names_for(request, testdir):
    def _item_names_for(tests_content):
        items = testdir.getitems(tests_content)
        hook = request.config.hook
        hook.pytest_collection_modifyitems(session=items[0].session,
                                           config=request.config, items=items)
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
