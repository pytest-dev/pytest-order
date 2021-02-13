# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict
from warnings import warn

import pytest

from ._version import __version__  # noqa: F401

# replace by Enum class after Python 2 support is gone
CLASS = 1
MODULE = 2
SESSION = 3

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


class Settings:
    sparse_ordering = False
    order_dependencies = False
    scope = SESSION
    group_scope = SESSION

    valid_scopes = {
        "class": CLASS,
        "module": MODULE,
        "session": SESSION
    }

    @classmethod
    def initialize(cls, config):
        cls.sparse_ordering = config.getoption("sparse_ordering")
        cls.order_dependencies = config.getoption("order_dependencies")
        scope = config.getoption("order_scope")
        if scope in cls.valid_scopes:
            cls.scope = cls.valid_scopes[scope]
        else:
            if scope is not None:
                warn("Unknown order scope '{}', ignoring it. "
                     "Valid scopes are 'session', 'module' and 'class'."
                     .format(scope))
            cls.scope = SESSION
        group_scope = config.getoption("order_group_scope")
        if group_scope in cls.valid_scopes:
            cls.group_scope = cls.valid_scopes[group_scope]
        else:
            if group_scope is not None:
                warn("Unknown order group scope '{}', ignoring it. "
                     "Valid scopes are 'session', 'module' and 'class'."
                     .format(group_scope))
            cls.group_scope = cls.scope
        if cls.group_scope > cls.scope:
            warn("Group scope is larger than order scope, ignoring it.")
            cls.group_scope = cls.scope


def full_name(item, name=None):
    if name and "." in name:
        # assumed to be sufficiently qualified
        return name
    path = (item.nodeid.replace(".py::", ".")
            .replace("/", ".").replace("::()", ""))
    if name is None:
        return path
    if "::" in path and "::" not in name:
        return path[:path.rindex("::") + 2] + name
    return path[:path.rindex(".") + 1] + name


def mark_binning(item, keys, start, end, before, after, dep, unordered, alias):
    handled = False
    order = None
    if "dependency" in keys:
        # always order dependencies if an order mark is present
        # otherwise only if order-dependencies is set
        mark = item.get_closest_marker("dependency")
        if Settings.order_dependencies or "order" in keys:
            dependent_mark = mark.kwargs.get("depends")
            if dependent_mark:
                scope = mark.kwargs.get("scope", "module")
                for name in dependent_mark:
                    dep.setdefault((name, scope), []).append(item)
                    handled = True
        # we always collect the names of the dependent items, because
        # we need them in both cases
        name_mark = mark.kwargs.get("name")
        # the default name in pytest-dependency the nodeid or a part
        # of the nodeid, depending on the scope
        if not name_mark:
            # in pytest < 4 the nodeid has an unwanted ::() part
            name_mark = item.nodeid.replace("::()", "")
        alias[name_mark] = full_name(item)

    if "order" in keys:
        mark = item.get_closest_marker("order")
        order = mark.args[0] if mark.args else mark.kwargs.get("index")
        before_mark = mark.kwargs.get("before")
        after_mark = mark.kwargs.get("after")
        if order is not None:
            if isinstance(order, int):
                order = int(order)
            elif order in orders_map:
                order = orders_map[order]
            else:
                warn("Unknown order attribute:'{}'".format(order))
                item.is_rel_mark = handled
                unordered.append(item)
                if not handled:
                    return False
                return True
            if order < 0:
                end.setdefault(order, []).append(item)
            else:
                start.setdefault(order, []).append(item)
        if before_mark:
            before.setdefault(full_name(item, before_mark), []).append(item)
        if after_mark:
            after.setdefault(
                full_name(item, after_mark), []).append(item)
        handled = True
    item.is_rel_mark = handled and order is None
    if not handled or order is None:
        unordered.append(item)
        return False
    return True


def insert_before(name, items, sort):
    if name:
        for pos, item in enumerate(sort):
            if not item.is_rel_mark and full_name(item).endswith(name):
                for item_to_insert in items:
                    index = sort.index(item_to_insert)
                    if index > pos:
                        del sort[index]
                        item_to_insert.is_rel_mark = False
                        sort.insert(pos, item_to_insert)
                return True
    return False


def insert_after(name, items, sort):
    if name:
        for pos, item in reversed(list(enumerate(sort))):
            if full_name(item).endswith(name):
                if item.is_rel_mark:
                    return False
                for item_to_insert in reversed(items):
                    index = sort.index(item_to_insert)
                    if index < pos + 1:
                        del sort[index]
                        pos -= 1
                        item_to_insert.is_rel_mark = False
                        sort.insert(pos + 1, item_to_insert)
                return True
    return False


def insert_before_group(label, scope, items, groups):
    label = scoped_label(label, scope)
    sorted_labels = [group[0] for group in groups]
    item_labels = [scoped_label_from_item(item, scope) for item in items]
    for pos, (group_label, group) in enumerate(groups):
        if group_label.endswith(label):
            for item_label in item_labels:
                if item_label in sorted_labels:
                    index = sorted_labels.index(item_label)
                    if index > pos:
                        moved_group = groups[index]
                        del groups[index]
                        groups.insert(pos, moved_group)
            return True
    return False


def insert_after_group(label, scope, items, groups):
    if label:
        label = scoped_label(label, scope)
        sorted_labels = [group[0] for group in groups]
        item_labels = [scoped_label_from_item(item, scope) for item in items]
        for pos, (group_label, group) in reversed(list(enumerate(groups))):
            if group_label.endswith(label):
                for item_label in reversed(item_labels):
                    if item_label in sorted_labels:
                        index = sorted_labels.index(item_label)
                        if index < pos + 1:
                            moved_group = groups[index]
                            del groups[index]
                            del sorted_labels[index]
                            pos -= 1
                            groups.insert(pos + 1, moved_group)
                            sorted_labels.insert(pos + 1, moved_group[0])
                return True
        return False


def insert_after_dep_group(group_index, items, groups):
    if group_index is not None:
        found = True
        for item in reversed(items):
            for index, group in reversed(list(enumerate(groups))):
                if item in group[1][0]:
                    if index < group_index:
                        moved_group = groups[index]
                        del groups[index]
                        group_index -= 1
                        groups.insert(group_index + 1, moved_group)
                else:
                    found = False
        return found
    return False


def sorted_groups(groups, scope, before_items, after_items, dep_items):
    start_groups = []
    middle_groups = []
    end_groups = []
    # first handle ordinal markers
    for group in groups:
        if group[0] is None:
            middle_groups.append((group[1], group[2]))
        elif group[0] >= 0:
            start_groups.append(group)
        else:
            end_groups.append(group)

    start_groups = sorted(start_groups)
    end_groups = sorted(end_groups)
    groups_sorted = [(group[1], group[2]) for group in start_groups]
    groups_sorted.extend(middle_groups)
    groups_sorted.extend([(group[1], group[2]) for group in end_groups])
    if start_groups:
        group_order = start_groups[0][0]
    elif end_groups:
        group_order = end_groups[-1][0]
    else:
        group_order = None

    length = len(before_items) + len(after_items) + len(dep_items)
    if length == 0:
        return group_order, groups_sorted

    # handle relative markers the same way single items are handled
    # add the group specific label to the sorted groups
    groups = [(scoped_label_from_item(group[0][0], scope), group)
              for group in groups_sorted]
    still_left = 0
    while length and still_left != length:
        still_left = length
        remove_labels = []
        for label, before in before_items.items():
            if insert_before_group(label, scope, before, groups):
                remove_labels.append(label)
        for label in remove_labels:
            del before_items[label]

        remove_labels = []
        for label, after in after_items.items():
            if insert_after_group(label, scope, after, groups):
                remove_labels.append(label)
        for label in remove_labels:
            del after_items[label]

        remove_labels = []
        for (label, dep_scope), after in dep_items.items():
            group_index = group_index_from_label(
                groups, label, dep_scope)
            if insert_after_dep_group(group_index, after, groups):
                remove_labels.append((label, dep_scope))
        for (label, dep_scope) in remove_labels:
            del dep_items[(label, dep_scope)]

    # remove the label from the groups
    groups_sorted = [group[1] for group in groups]
    return group_order, groups_sorted


def modify_item_groups(items):
    before_items = {}
    after_items = {}
    dep_items = {}
    if Settings.group_scope < Settings.scope:
        sorted_list = []
        if Settings.scope == SESSION:
            module_items = module_item_groups(items)
            module_groups = []
            if Settings.group_scope == CLASS:
                for module_item in module_items.values():
                    class_items = class_item_groups(module_item)
                    class_groups = [do_modify_items(item, CLASS, before_items,
                                                    after_items, dep_items)
                                    for item in class_items.values()]
                    module_group = [[], {}]
                    group_order, class_groups = sorted_groups(
                        class_groups, CLASS,
                        before_items, after_items, dep_items
                    )
                    for group in class_groups:
                        module_group[0].extend(group[0])
                        module_group[1].update(group[1])
                    module_groups.append((group_order, module_group[0],
                                          module_group[1]))
            else:
                module_groups = [do_modify_items(item, MODULE, before_items,
                                                 after_items, dep_items)
                                 for item in module_items.values()]
            for group in sorted_groups(
                    module_groups, MODULE,
                    before_items, after_items, dep_items)[1]:
                sorted_list.extend(group[0])
        else:  # module scope / class group scope
            class_items = class_item_groups(items)
            class_groups = [do_modify_items(item, CLASS, before_items,
                                            after_items, dep_items)
                            for item in class_items.values()]
            for group in sorted_groups(
                    class_groups, CLASS,
                    before_items, after_items, dep_items)[1]:
                sorted_list.extend(group[0])
    else:
        sorted_list = do_modify_items(
            items, SESSION, before_items, after_items, dep_items)[1]

    show_unresolved_dep_items(dep_items)
    return sorted_list


def scoped_label(label, scope):
    if scope == MODULE:
        if "." not in label:
            return label
        return label[:label.rindex(".")]
    if scope == CLASS:
        if "::" not in label:
            return label
        return label.split("::")[0]
    return label


def scoped_label_from_item(item, scope):
    label = (item.nodeid.replace(".py::", ".")
             .replace("/", ".").replace("::()", ""))
    return scoped_label(label, scope)


def needed_for_group_sort(label, item, scope):
    if Settings.group_scope >= Settings.scope:
        return False

    name = scoped_label(label, scope)
    itemid = scoped_label_from_item(item, scope)
    needed = name != itemid
    if not needed and scope == CLASS and Settings.scope == SESSION:
        return needed_for_group_sort(label, item, MODULE)
    return needed


def do_modify_items(items, scope, out_before_items, out_after_items,
                    out_dep_items):
    start_item = {}
    end_item = {}
    unordered_list = []
    before_items = {}
    after_items = {}
    dep_items = {}
    alias_names = {}

    for item in items:
        mark_binning(item, item.keywords.keys(), start_item, end_item,
                     before_items, after_items, dep_items,
                     unordered_list, alias_names)

    start_item = sorted(start_item.items())
    end_item = sorted(end_item.items())

    sorted_list = sort_numbered_items(start_item, end_item, unordered_list)

    still_left = 0
    length = len(before_items) + len(after_items) + len(dep_items)
    for rel_items in (before_items, after_items):
        for label, entry in rel_items.items():
            if needed_for_group_sort(label, entry[0], scope):
                for item in rel_items[label]:
                    item.is_rel_mark = False

    while length and still_left != length:
        still_left = length
        remove_labels = []
        for label, before in before_items.items():
            if insert_before(label, before, sorted_list):
                remove_labels.append(label)
        for label in remove_labels:
            del before_items[label]

        remove_labels = []
        for label, after in after_items.items():
            if insert_after(label, after, sorted_list):
                remove_labels.append(label)
        for label in remove_labels:
            del after_items[label]

        remove_labels = []
        for (label, dep_scope), after in dep_items.items():
            name = label_from_alias(alias_names, label, dep_scope)
            if name is None:
                for item in after:
                    if item.is_rel_mark:
                        item.is_rel_mark = False
                        # the label is related to another group,
                        # so the item can now be handled
                        still_left += 1
            elif insert_after(name, after, sorted_list):
                remove_labels.append((label, dep_scope))
        for (label, dep_scope) in remove_labels:
            del dep_items[(label, dep_scope)]

        length = len(before_items) + len(after_items) + len(dep_items)
    if length:
        msg = ""
        msg += handle_unhandled_items(before_items, out_before_items, scope)
        msg += handle_unhandled_items(after_items, out_after_items, scope)
        msg += handle_unhandled_dep_items(
            dep_items, out_dep_items, scope, alias_names)
        if msg:
            sys.stdout.write(
                "\nWARNING: cannot execute test relative to others: ")
            sys.stdout.write(msg)
            sys.stdout.write("- ignoring the marker.\n")
            sys.stdout.flush()

    if start_item:
        group_order = start_item[0][0]
    elif end_item:
        group_order = end_item[-1][0]
    else:
        group_order = None

    return group_order, sorted_list, alias_names


def group_index_from_label(groups, label, scope):
    for index, group in enumerate(groups):
        if label_from_alias(group[1][1], label, scope):
            return index


def label_from_alias(alias_names, label, scope):
    name = alias_names.get(label)
    if name or scope in ("session", "package"):
        return name
    for alias in alias_names:
        if "::" in alias:
            name = alias.split("::", 1)[1]
            if scope == "class" and "::" in name:
                name = name.split("::")[1]
        else:
            name = alias
        if name == label:
            return alias_names[alias]


def handle_unhandled_items(items, out_items, scope):
    msg = ""
    for label, entries in items.items():
        msg += handle_unhandled_item(entries, label, out_items, scope)
    return msg


def handle_unhandled_dep_items(items, out_items, scope, alias_names):
    msg = ""
    for (label, dep_scope), entries in items.items():
        name = label_from_alias(alias_names, label, dep_scope)
        if name is not None:
            msg += handle_unhandled_item(entries, name, out_items, scope)
        else:
            new_label = label  # scoped_label(label, scope)
            out_items.setdefault((new_label, dep_scope), []).extend(entries)
    return msg


def handle_unhandled_item(entries, label, out_items, scope):
    msg = ""
    for entry in entries:
        if not needed_for_group_sort(label, entry, scope):
            msg = label + " "
        else:
            new_label = scoped_label(label, scope)
            out_items.setdefault(new_label, []).append(entry)
    return msg


def show_unresolved_dep_items(dep_items):
    if dep_items:
        sys.stdout.write(
            "\nWARNING: cannot resolve the dependency marker(s): ")
        sys.stdout.write(", ".join(item[0] for item in dep_items))
        sys.stdout.write(" - ignoring the markers.\n")
        sys.stdout.flush()


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
    if Settings.scope == SESSION:
        sorted_list = modify_item_groups(items)
    elif Settings.scope == MODULE:
        module_items = module_item_groups(items)
        sorted_list = []
        for module_item_list in module_items.values():
            sorted_list.extend(modify_item_groups(module_item_list))
    else:  # class scope
        class_items = class_item_groups(items)
        sorted_list = []
        for class_item_list in class_items.values():
            sorted_list.extend(modify_item_groups(class_item_list))

    items[:] = sorted_list


def module_item_groups(items):
    module_items = OrderedDict()
    for item in items:
        module_path = item.nodeid[:item.nodeid.index("::")]
        module_items.setdefault(module_path, []).append(item)
    return module_items


def class_item_groups(items):
    class_items = OrderedDict()
    for item in items:
        delim_index = item.nodeid.index("::")
        if "::" in item.nodeid[delim_index + 2:]:
            delim_index = item.nodeid.index("::", delim_index + 2)
        class_path = item.nodeid[:delim_index]
        class_items.setdefault(class_path, []).append(item)
    return class_items
