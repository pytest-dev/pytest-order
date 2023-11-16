import pytest
from pytest_order.settings import Scope

pytest_plugins = ["pytester"]


@pytest.fixture
def item_names_for(testdir):
    def _item_names_for(tests_content):
        def name(item):
            if item.cls:
                return item.cls.__name__ + "::" + item.name
            return item.name

        items = testdir.getitems(tests_content)
        hook = items[0].config.hook
        hook.pytest_collection_modifyitems(
            session=items[0].session, config=items[0].config, items=items
        )

        return [name(item) for item in items]

    return _item_names_for


@pytest.fixture
def test_path(testdir):
    testdir.tmpdir.join("pytest.ini").write("[pytest]\nconsole_output_style = classic")
    yield testdir


@pytest.fixture
def ignore_settings(mocker):
    settings = mocker.patch("pytest_order.sorter.Settings")
    settings.return_value.sparse_ordering = False
    settings.return_value.order_dependencies = False
    settings.return_value.scope = Scope.SESSION
    settings.return_value.group_scope = Scope.SESSION
    settings.return_value.scope_level = 0
    settings.return_value.marker_prefix = None
    yield settings


@pytest.fixture
def order_dependencies(ignore_settings):
    ignore_settings.return_value.order_dependencies = True
    yield
