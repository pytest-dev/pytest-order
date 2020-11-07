# -*- coding: utf-8 -*-
import os
import re
import sys
from collections import OrderedDict
from warnings import warn

import pytest

from ._version import __version__  # noqa: F401

orders_map = {
    "first": 0,
    "second": 1,
    "third": 2,
    "fourth": 3,
    "fifth": 4,
    "sixth": 5,
    "seventh": 6,
    "eighth": 7,
    "last": -1,
    "second_to_last": -2,
    "third_to_last": -3,
    "fourth_to_last": -4,
    "fifth_to_last": -5,
    "sixth_to_last": -6,
    "seventh_to_last": -7,
    "eighth_to_last": -8
}


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
        # Python 2.7 didn"t allow arbitrary attributes on methods, so we have
        # to keep the function as a function and then add it to the class as a
        # pseudomethod.  Since the class is purely for structuring and `self`
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
                         "are 'session' (default), 'module', and 'class'")
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


class Settings:
    sparse_ordering = False
    order_dependencies = False
    scope = "session"

    @classmethod
    def initialize(cls, config):
        cls.sparse_ordering = config.getoption("sparse_ordering")
        cls.order_dependencies = config.getoption("order_dependencies")
        scope = config.getoption("order_scope")
        if scope in ("session", "module", "class"):
            cls.scope = scope
        else:
            if scope is not None:
                warn("Unknown order scope '{}', ignoring it. "
                     "Valid scopes are 'session', 'module' and 'class'."
                     .format(scope))
            cls.scope = "session"


def get_filename(item):
    name = item.location[0]
    if os.sep in name:
        name = item.location[0].rsplit(os.sep, 1)[1]
    return name[:-3]


def mark_binning(item, keys, start, end, before, after, unordered, alias):
    if ("dependency" in keys and
            (Settings.order_dependencies or "order" in keys)):
        # always order dependencies if an order mark is present
        # otherwise only if order-dependencies is set
        mark = item.get_closest_marker("dependency")
        prefix = get_filename(item) + "."
        dependent_mark = mark.kwargs.get("depends")
        if dependent_mark:
            for name in dependent_mark:
                if "." not in name:
                    name = prefix + name
                after.setdefault(name, []).append(item)
        name_mark = mark.kwargs.get("name")
        if name_mark:
            alias[prefix + name_mark] = prefix + item.name

    if "order" in keys:
        mark = item.get_closest_marker("order")
        order = mark.args[0] if mark.args else None
        before_mark = mark.kwargs.get("before")
        after_mark = mark.kwargs.get("after")
        if order is not None:
            if isinstance(order, int):
                order = int(order)
            elif order in orders_map:
                order = orders_map[order]
            else:
                warn("Unknown order attribute:'{}'".format(order))
                unordered.append(item)
                return False
            if order < 0:
                end.setdefault(order, []).append(item)
            else:
                start.setdefault(order, []).append(item)
        elif before_mark:
            if "." not in before_mark:
                prefix = get_filename(item)
                before_mark = prefix + "." + before_mark
            before.setdefault(before_mark, []).append(item)
        elif after_mark:
            if "." not in after_mark:
                prefix = get_filename(item)
                after_mark = prefix + "." + after_mark

            after.setdefault(after_mark, []).append(item)
        return True
    unordered.append(item)
    return False


def insert_before(name, items, sort):
    regex_name = re.escape(name) + r"(:?\.\w+)?$"
    for pos, item in enumerate(sort):
        prefix = get_filename(item)
        item_name = prefix + "." + item.location[2]
        if re.match(regex_name, item_name):
            if pos == 0:
                sort[:] = items + sort
            else:
                sort[pos:1] = items
            return True
    return False


def insert_after(name, items, sort):
    regex_name = re.escape(name) + r"(:?\.\w+)?$"
    for pos, item in reversed(list(enumerate(sort))):
        prefix = get_filename(item)
        item_name = prefix + "." + item.location[2]
        if re.match(regex_name, item_name):
            sort[pos + 1:1] = items
            return True

    return False


def do_modify_items(items):
    before_item = {}
    after_item = {}
    start_item = {}
    end_item = {}
    unordered_list = []
    alias_names = {}

    for item in items:
        mark_binning(item, item.keywords.keys(), start_item, end_item,
                     before_item, after_item, unordered_list, alias_names)

    start_item = sorted(start_item.items())
    end_item = sorted(end_item.items())

    sorted_list = sort_numbered_items(start_item, end_item, unordered_list)

    still_left = 0
    length = len(before_item) + len(after_item)

    while still_left != length:
        still_left = length
        remove_labels = []
        for label, before in before_item.items():
            if insert_before(label, before, sorted_list):
                remove_labels.append(label)
        for label in remove_labels:
            del before_item[label]

        remove_labels = []
        for label, after in after_item.items():
            name = alias_names[label] if label in alias_names else label
            if insert_after(name, after, sorted_list):
                remove_labels.append(label)
        for label in remove_labels:
            del after_item[label]

        length = len(before_item) + len(after_item)
    if length:
        sys.stdout.write("WARNING: can not execute test relative to others: ")
        for label, entry in before_item.items():
            sys.stdout.write(label + " ")
            sorted_list += entry
        for label, entry in after_item.items():
            sys.stdout.write(label + " ")
            sorted_list += entry
        sys.stdout.flush()
        print("enqueue them behind the others")

    return sorted_list


def sort_numbered_items(start_item, end_item, unordered_list):
    sorted_list = []
    index = 0
    for entries in start_item:
        if Settings.sparse_ordering:
            while entries[0] > index and unordered_list:
                sorted_list.append(unordered_list.pop(0))
                index += 1
        sorted_list += entries[1]
        index += len(entries[1])
    mid_index = len(sorted_list)
    index = -1
    for entries in reversed(end_item):
        if Settings.sparse_ordering:
            while entries[0] < index and unordered_list:
                sorted_list.insert(mid_index, unordered_list.pop())
                index -= 1
        sorted_list[mid_index:mid_index] = entries[1]
        index -= len(entries[1])
    sorted_list[mid_index:mid_index] = unordered_list
    return sorted_list


def modify_items(session, config, items):
    Settings.initialize(config)
    if Settings.scope == "session":
        sorted_list = do_modify_items(items)
    elif Settings.scope == "module":
        module_items = OrderedDict()
        for item in items:
            module_path = item.nodeid[:item.nodeid.index("::")]
            module_items.setdefault(module_path, []).append(item)
        sorted_list = []
        for module_item_list in module_items.values():
            sorted_list.extend(do_modify_items(module_item_list))
    else:  # class scope
        class_items = OrderedDict()
        for item in items:
            delim_index = item.nodeid.index("::")
            if "::" in item.nodeid[delim_index + 2:]:
                delim_index = item.nodeid.index("::", delim_index + 2)
            class_path = item.nodeid[:delim_index]
            class_items.setdefault(class_path, []).append(item)
        sorted_list = []
        for class_item_list in class_items.values():
            sorted_list.extend(do_modify_items(class_item_list))

    items[:] = sorted_list
