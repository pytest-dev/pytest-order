from collections.abc import Generator, Callable

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.mark import Mark
from _pytest.python import Function

from .sorter import Sorter


def pytest_configure(config: Config) -> None:
    """
    Register the "order" marker and configure the plugin,
    depending on the CLI options.
    """

    provided_by_pytest_order = (
        "Provided by pytest-order. See also: https://pytest-order.readthedocs.io/"
    )

    config_line = (
        "order: specify ordering information for when tests should run "
        "in relation to one another. " + provided_by_pytest_order
    )
    config.addinivalue_line("markers", config_line)
    # We need to dynamically add this `tryfirst` decorator to the plugin:
    # only when the CLI option is present should the decorator be added.
    # Thus, we manually run the decorator on the class function and
    # manually replace it.
    hook_function: Callable[
        [Session, Config, list[Function]], None | Generator[None]
    ] = modify_items
    if config.getoption("indulgent_ordering"):
        # try to run before other plugins
        wrapper = pytest.hookimpl(tryfirst=True)
    elif config.getoption("order_after_ff"):
        # run after the LFPlugin plugin, handling --failed-first and --failed-last
        wrapper = pytest.hookimpl(hookwrapper=True, tryfirst=True)
        hook_function = modify_items_gen
    else:
        # try to run after other plugins
        wrapper = pytest.hookimpl(trylast=True)
    OrderingPlugin.pytest_collection_modifyitems = wrapper(  # type:ignore[attr-defined]
        hook_function
    )
    config.pluginmanager.register(OrderingPlugin(), "orderingplugin")


def pytest_addoption(parser: Parser) -> None:
    """Set up CLI option for pytest"""
    group = parser.getgroup("order")
    group.addoption(
        "--indulgent-ordering",
        action="store_true",
        dest="indulgent_ordering",
        help=(
            "Request that the sort order provided by pytest-order be applied "
            "before other sorting, allowing the other sorting to have priority"
        ),
    )
    group.addoption(
        "--order-scope",
        action="store",
        dest="order_scope",
        help=(
            "Defines the scope used for ordering. Possible values are: "
            "'session' (default), 'module', and 'class'. "
            "Ordering is only done inside a scope."
        ),
    )
    group.addoption(
        "--order-scope-level",
        action="store",
        type=int,
        dest="order_scope_level",
        help=(
            "Defines that the given directory level is used as order scope. "
            "Cannot be used with --order-scope. The value is a number "
            "that defines the hierarchical index of the directories used as "
            "order scope, starting with 0 at session scope."
        ),
    )
    group.addoption(
        "--order-group-scope",
        action="store",
        dest="order_group_scope",
        help=(
            "Defines the scope used for order groups. Possible values are: "
            " 'session' (default), 'module', and 'class'. "
            "Ordering is first done inside a group, then between groups."
        ),
    )
    group.addoption(
        "--sparse-ordering",
        action="store_true",
        dest="sparse_ordering",
        help=(
            "If there are gaps between ordinals, they are filled with unordered tests."
        ),
    )
    group.addoption(
        "--order-dependencies",
        action="store_true",
        dest="order_dependencies",
        help=(
            "If set, dependencies added by pytest-dependency will be ordered if needed."
        ),
    )
    group.addoption(
        "--order-marker-prefix",
        action="store",
        dest="order_marker_prefix",
        help=(
            "If set, markers starting with the given prefix followed by a number "
            "are handled like order markers with an index."
        ),
    )
    group.addoption(
        "--error-on-failed-ordering",
        action="store_true",
        dest="error_on_failed_ordering",
        help=(
            "If set, tests with relative markers that could not be ordered "
            "will error instead of generating only a warning."
        ),
    )
    group.addoption(
        "--order-after-ff",
        action="store_true",
        dest="order_after_ff",
        help="If set, the plugin will run after the --failed-first and similar option hooks.",
    )


def _get_mark_description(mark: Mark):
    if mark.kwargs:
        return ", ".join([f"{k}={v}" for k, v in mark.kwargs.items()])
    elif mark.args:
        return f"index={mark.args[0]}"
    return mark


def pytest_generate_tests(metafunc):
    """
    Handle multiple pytest.mark.order decorators.

    Make parametrized tests with corresponding order marks.
    """
    if getattr(metafunc, "function", False):
        if getattr(metafunc.function, "pytestmark", False):
            # Get list of order marks
            marks = metafunc.function.pytestmark
            order_marks = [mark for mark in marks if mark.name == "order"]
            if len(order_marks) > 1:
                # Remove all order marks
                metafunc.function.pytestmark = [
                    mark for mark in marks if mark.name != "order"
                ]
                # Prepare arguments for parametrization with order marks
                args = [
                    pytest.param(_get_mark_description(mark), marks=[mark])
                    for mark in order_marks
                ]
                if "order" not in metafunc.fixturenames:
                    metafunc.fixturenames.append("order")
                metafunc.parametrize("order", args)


@pytest.fixture
def fail_after_cannot_order():
    pytest.fail("The test could not be ordered")


class OrderingPlugin:
    """
    Plugin implementation.

    By putting this in a class, we are able to dynamically register it after
    the CLI is parsed.
    """


def modify_items(session: Session, config: Config, items: list[Function]) -> None:
    sorter = Sorter(config, items)
    items[:] = sorter.sort_items()


def modify_items_gen(
    session: Session, config: Config, items: list[Function]
) -> Generator[None]:
    yield
    sorter = Sorter(config, items)
    items[:] = sorter.sort_items()
