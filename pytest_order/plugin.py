# -*- coding: utf-8 -*-
from typing import List

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.python import Function

from .sorter import Sorter


def pytest_configure(config: Config) -> None:
    """
    Register the "order" marker and configure the plugin,
    depending on the CLI options.
    """

    provided_by_pytest_order = (
        "Provided by pytest-order. "
        "See also: https://pytest-dev.github.io/pytest-order/"
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
    if config.getoption("indulgent_ordering"):
        wrapper = pytest.hookimpl(tryfirst=True)
    else:
        wrapper = pytest.hookimpl(trylast=True)
    setattr(
        OrderingPlugin, "pytest_collection_modifyitems", wrapper(modify_items)
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
            "If there are gaps between ordinals, they are filled "
            "with unordered tests."
        ),
    )
    group.addoption(
        "--order-dependencies",
        action="store_true",
        dest="order_dependencies",
        help=(
            "If set, dependencies added by pytest-dependency will be ordered "
            "if needed."
        ),
    )


class OrderingPlugin:
    """
    Plugin implementation.

    By putting this in a class, we are able to dynamically register it after
    the CLI is parsed.
    """


def modify_items(
    session: Session, config: Config, items: List[Function]
) -> None:
    sorter = Sorter(config, items)
    items[:] = sorter.sort_items()
