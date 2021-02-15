# -*- coding: utf-8 -*-

import pytest

from pytest_order.sorter import Sorter
from ._version import __version__  # noqa: F401


def pytest_configure(config):
    """Register the "order" marker and configure the plugin depending
     on the CLI options"""

    provided_by_pytest_order = (
        "Provided by pytest-order. "
        "See also: https://mrbean-bremen.github.io/pytest-order/"
    )

    config_line = (
            "order: specify ordering information for when tests should run "
            "in relation to one another. " + provided_by_pytest_order
    )
    config.addinivalue_line("markers", config_line)

    if config.getoption("indulgent_ordering"):
        # We need to dynamically add this `tryfirst` decorator to the plugin:
        # only when the CLI option is present should the decorator be added.
        # Thus, we manually run the decorator on the class function and
        # manually replace it.
        # Python 2.7 didn't allow arbitrary attributes on methods, so we have
        # to keep the function as a function and then add it to the class as a
        # pseudo method.  Since the class is purely for structuring and `self`
        # is never referenced, this seems reasonable.
        OrderingPlugin.pytest_collection_modifyitems = pytest.hookimpl(
            function=modify_items, tryfirst=True)
    else:
        OrderingPlugin.pytest_collection_modifyitems = pytest.hookimpl(
            function=modify_items, trylast=True)
    config.pluginmanager.register(OrderingPlugin(), "orderingplugin")


def pytest_addoption(parser):
    """Set up CLI option for pytest"""
    group = parser.getgroup("ordering")
    group.addoption("--indulgent-ordering", action="store_true",
                    dest="indulgent_ordering",
                    help="Request that the sort order provided by "
                         "pytest-order be applied before other sorting, "
                         "allowing the other sorting to have priority")
    group.addoption("--order-scope", action="store",
                    dest="order_scope",
                    help="Defines the scope used for ordering. Possible values"
                         "are 'session' (default), 'module', and 'class'."
                         "Ordering is only done inside a scope.")
    group.addoption("--order-group-scope", action="store",
                    dest="order_group_scope",
                    help="Defines the scope used for order groups. Possible "
                         "values are 'session' (default), 'module', "
                         "and 'class'. Ordering is first done inside a group, "
                         "then between groups.")
    group.addoption("--sparse-ordering", action="store_true",
                    dest="sparse_ordering",
                    help="If there are gaps between ordinals they are filled "
                         "with unordered tests.")
    group.addoption("--order-dependencies", action="store_true",
                    dest="order_dependencies",
                    help="If set, dependencies added by pytest-dependency will"
                         "be ordered if needed.")


class OrderingPlugin(object):
    """
    Plugin implementation

    By putting this in a class, we are able to dynamically register it after
    the CLI is parsed.
    """


def modify_items(session, config, items):
    sorter = Sorter(config, items)
    items[:] = sorter.sort_items()
