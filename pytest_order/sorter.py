# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict
from warnings import warn

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


class Settings:
    valid_scopes = {
        "class": CLASS,
        "module": MODULE,
        "session": SESSION
    }

    def __init__(self, config):
        self.sparse_ordering = config.getoption("sparse_ordering")
        self.order_dependencies = config.getoption("order_dependencies")
        scope = config.getoption("order_scope")
        if scope in self.valid_scopes:
            self.scope = self.valid_scopes[scope]
        else:
            if scope is not None:
                warn("Unknown order scope '{}', ignoring it. "
                     "Valid scopes are 'session', 'module' and 'class'."
                     .format(scope))
            self.scope = SESSION
        scope_level = config.getoption("order_scope_level") or 0
        if scope_level != 0 and self.scope != SESSION:
            warn("order-scope-level cannot be used together with "
                 "--order-scope={}".format(scope))
            scope_level = 0
        self.scope_level = scope_level
        group_scope = config.getoption("order_group_scope")
        if group_scope in self.valid_scopes:
            self.group_scope = self.valid_scopes[group_scope]
        else:
            if group_scope is not None:
                warn("Unknown order group scope '{}', ignoring it. "
                     "Valid scopes are 'session', 'module' and 'class'."
                     .format(group_scope))
            self.group_scope = self.scope
        if self.group_scope > self.scope:
            warn("Group scope is larger than order scope, ignoring it.")
            self.group_scope = self.scope


class Sorter:
    """Sort all items according the given configuration."""

    def __init__(self, config, items):
        self.settings = Settings(config)
        self.items = [Item(item) for item in items]
        self.node_ids = OrderedDict()
        self.node_id_last = {}
        for item in self.items:
            self.node_ids[item.node_id] = item
            last_parts = item.node_id.split("/")[-1].split("::")
            # save last nodeid component to avoid to iterate over all
            # items for each label
            self.node_id_last.setdefault(
                last_parts[-1], []).append(item.node_id)
        self.rel_marks = []
        self.dep_marks = []

    def sort_items(self):
        """Do the actual sorting and return the sorted items."""
        self.collect_markers()
        if self.settings.scope == SESSION:
            if self.settings.scope_level > 0:
                dir_groups = directory_item_groups(
                    self.items, self.settings.scope_level)
                sorted_list = []
                for items in dir_groups.values():
                    sorter = ScopeSorter(self.settings, items,
                                         self.rel_marks, self.dep_marks)
                    sorted_list.extend(sorter.sort_items())
            else:
                sorter = ScopeSorter(self.settings, self.items,
                                     self.rel_marks, self.dep_marks,
                                     session_scope=True)
                sorted_list = sorter.sort_items()
        elif self.settings.scope == MODULE:
            module_groups = module_item_groups(self.items)
            sorted_list = []
            for module_items in module_groups.values():
                sorter = ScopeSorter(self.settings, module_items,
                                     self.rel_marks, self.dep_marks)
                sorted_list.extend(sorter.sort_items())
        else:  # class scope
            class_groups = class_item_groups(self.items)
            sorted_list = []
            for class_items in class_groups.values():
                sorter = ScopeSorter(self.settings, class_items,
                                     self.rel_marks, self.dep_marks)
                sorted_list.extend(sorter.sort_items())
        return [item.item for item in sorted_list]

    def mark_binning(self, item, dep_marks, aliases):
        """Collect relevant markers for the given item."""
        keys = item.item.keywords.keys()
        has_dependency = "dependency" in keys
        has_order = "order" in keys
        if has_dependency:
            self.handle_dependency_mark(item, has_order, dep_marks, aliases)
        if has_order:
            item.order = self.handle_order_mark(item)

    def handle_dependency_mark(self, item, has_order, dep_marks, aliases):
        # always order dependencies if an order mark is present
        # otherwise only if order-dependencies is set
        mark = item.item.get_closest_marker("dependency")
        if self.settings.order_dependencies or has_order:
            dependent_mark = mark.kwargs.get("depends")
            if dependent_mark:
                scope = scope_from_name(mark.kwargs.get("scope", "module"))
                prefix = scoped_node_id(item.node_id, scope)
                for name in dependent_mark:
                    dep_marks.setdefault(
                        (name, scope, prefix), []).append(item)
                    item.inc_rel_marks()
        # we always collect the names of the dependent items, because
        # we need them in both cases
        name_mark = mark.kwargs.get("name")
        # the default name in pytest-dependency is the nodeid or a part
        # of the nodeid, depending on the scope
        if not name_mark:
            name_mark = item.node_id
        aliases[name_mark] = item

    def handle_order_mark(self, item):
        mark = item.item.get_closest_marker("order")
        order = mark.args[0] if mark.args else mark.kwargs.get("index")
        if order is not None:
            if isinstance(order, int):
                order = int(order)
            elif order in orders_map:
                order = orders_map[order]
            else:
                warn("Unknown order attribute:'{}'".format(order))
                order = None
        item.order = order
        self.handle_relative_marks(item, mark)
        if order is not None:
            item.nr_rel_items = 0
        return order

    def item_from_label(self, label, item, is_cls_mark):
        label = self.node_id_from_label(label)
        item_id = item.node_id
        label_len = len(label)
        last_comp = label.split("/")[-1].split("::")[-1]
        try:
            node_ids = self.node_id_last[last_comp]
            for node_id in node_ids:
                if node_id.endswith(label):
                    id_start = node_id[:-label_len]
                    if is_cls_mark and id_start.count("::") == 2:
                        continue
                    if item_id.startswith(id_start):
                        return self.node_ids[node_id]
        except KeyError:
            return

    def items_from_class_label(self, label, item):
        items = []
        label = self.node_id_from_label(label)
        item_id = item.node_id
        label_len = len(label)
        for node_id in self.node_ids:
            if node_id.count("::") == 2:
                cls_index = node_id.rindex("::")
                if node_id[:cls_index].endswith(label):
                    id_start = node_id[:cls_index - label_len]
                    if item_id.startswith(id_start):
                        items.append(self.node_ids[node_id])
        return items

    @staticmethod
    def node_id_from_label(label):
        if "." in label:
            label_comp = label.split(".")
            label = ".py::".join(["/".join(label_comp[:-1]), label_comp[-1]])
        return label

    def handle_before_or_after_mark(self, item, mark, marker_name, is_after):
        def is_class_mark():
            return (
                    item.item.cls and
                    item.item.parent.get_closest_marker("order") == mark
            )

        def is_mark_for_class():
            return "::" not in marker_name and is_class_mark()

        is_cls_mark = is_class_mark()
        item_for_label = self.item_from_label(marker_name, item, is_cls_mark)
        if item_for_label:
            rel_mark = RelativeMark(item_for_label,
                                    item, move_after=is_after)
            if is_after or not is_cls_mark:
                self.rel_marks.append(rel_mark)
            else:
                self.rel_marks.insert(0, rel_mark)
            item.inc_rel_marks()
            return True
        else:
            if is_mark_for_class():
                items = self.items_from_class_label(marker_name, item)
                for item_for_label in items:
                    rel_mark = RelativeMark(item_for_label,
                                            item, move_after=is_after)
                    if is_after:
                        self.rel_marks.append(rel_mark)
                    else:
                        self.rel_marks.insert(0, rel_mark)
                    item.inc_rel_marks()
                return items
        return False

    def handle_relative_marks(self, item, mark):
        has_relative_marks = False
        before_marks = mark.kwargs.get("before", ())
        if before_marks and not isinstance(before_marks, (list, tuple)):
            before_marks = (before_marks,)
        for before_mark in before_marks:
            if self.handle_before_or_after_mark(
                    item, mark, before_mark, is_after=False):
                has_relative_marks = True
            else:
                self.warn_about_unknown_test(before_mark)
        after_marks = mark.kwargs.get("after", ())
        if after_marks and not isinstance(after_marks, (list, tuple)):
            after_marks = (after_marks,)
        for after_mark in after_marks:
            if self.handle_before_or_after_mark(
                    item, mark, after_mark, is_after=True):
                has_relative_marks = True
            else:
                self.warn_about_unknown_test(after_mark)
        return has_relative_marks

    @staticmethod
    def warn_about_unknown_test(rel_mark):
        sys.stdout.write("\nWARNING: cannot execute test relative to others:"
                         " {} - ignoring the marker.".format(rel_mark))

    def collect_markers(self):
        aliases = {}
        dep_marks = {}
        for item in self.items:
            self.mark_binning(item, dep_marks, aliases)
        self.resolve_dependency_markers(dep_marks, aliases)

    def resolve_dependency_markers(self, dep_marks, aliases):
        for (name, scope, prefix), items in dep_marks.items():
            if name in aliases:
                for item in items:
                    self.dep_marks.append(RelativeMark(aliases[name], item,
                                                       move_after=True))
            else:
                label = "::".join([prefix, name])
                if label in aliases:
                    for item in items:
                        self.dep_marks.append(
                            RelativeMark(aliases[label], item,
                                         move_after=True))
                else:
                    sys.stdout.write(
                        "\nWARNING: Cannot resolve the dependency marker '{}' "
                        "- ignoring it.".format(name))


def module_item_groups(items):
    """Split items into groups per module."""
    module_items = OrderedDict()
    for item in items:
        module_items.setdefault(item.module_path, []).append(item)
    return module_items


def directory_item_groups(items, level):
    """Split items into groups per directory at the given level.
    The level is relative to the root directory, which is at level 0.
    """
    module_items = OrderedDict()
    for item in items:
        module_items.setdefault(item.parent_path(level), []).append(item)
    return module_items


def class_item_groups(items):
    """Split items into groups per class. Items outside a class
    are sorted into a group per module.
    """
    class_items = OrderedDict()
    for item in items:
        delimiter_index = item.node_id.index("::")
        if "::" in item.node_id[delimiter_index + 2:]:
            delimiter_index = item.node_id.index("::", delimiter_index + 2)
        class_path = item.node_id[:delimiter_index]
        class_items.setdefault(class_path, []).append(item)
    return class_items


def filter_marks(marks, all_items):
    result = []
    for mark in marks:
        if mark.item in all_items and mark.item_to_move in all_items:
            result.append(mark)
        else:
            mark.item_to_move.dec_rel_marks()
    return result


class ScopeSorter:
    """Sorts the items for the defined scope."""

    def __init__(self, settings, items, rel_marks, dep_marks,
                 session_scope=False):
        self.settings = settings
        self.items = items
        # no need to filter items in session scope
        if session_scope:
            self.rel_marks = rel_marks
            self.dep_marks = dep_marks
        else:
            self.rel_marks = filter_marks(rel_marks, self.items)
            self.dep_marks = filter_marks(dep_marks, self.items)

    def sort_items(self):
        if self.settings.group_scope < self.settings.scope:
            if self.settings.scope == SESSION:
                sorted_list = self.sort_in_session_scope()
            else:  # module scope / class group scope
                sorted_list = self.sort_in_module_scope()
        else:
            sorted_list = self.sort_items_in_scope(self.items, SESSION).items

        return sorted_list

    def sort_in_session_scope(self):
        sorted_list = []
        module_items = module_item_groups(self.items)
        if self.settings.group_scope == CLASS:
            module_groups = self.sort_class_groups(module_items)
        else:
            module_groups = [
                self.sort_items_in_scope(item, MODULE)
                for item in module_items.values()]
        sorter = GroupSorter(MODULE, module_groups,
                             self.rel_marks, self.dep_marks)
        for group in sorter.sorted_groups()[1]:
            sorted_list.extend(group.items)
        return sorted_list

    def sort_in_module_scope(self):
        sorted_list = []
        class_items = class_item_groups(self.items)
        class_groups = [self.sort_items_in_scope(item, CLASS)
                        for item in class_items.values()]
        sorter = GroupSorter(CLASS, class_groups,
                             self.rel_marks, self.dep_marks)
        for group in sorter.sorted_groups()[1]:
            sorted_list.extend(group.items)
        return sorted_list

    def sort_class_groups(self, module_items):
        module_groups = []
        for module_item in module_items.values():
            class_items = class_item_groups(module_item)
            class_groups = [
                self.sort_items_in_scope(item, CLASS)
                for item in class_items.values()]
            module_group = ItemGroup()
            sorter = GroupSorter(CLASS, class_groups,
                                 self.rel_marks, self.dep_marks)
            group_order, class_groups = sorter.sorted_groups()
            module_group.extend(class_groups, group_order)
            module_groups.append(module_group)
        return module_groups

    def sort_items_in_scope(self, items, scope):
        item_list = ItemList(items, self.settings, scope,
                             self.rel_marks, self.dep_marks)
        for item in items:
            item_list.collect_markers(item)

        sorted_list = item_list.sort_numbered_items()

        still_left = 0
        length = item_list.number_of_rel_groups()
        while length and still_left != length:
            still_left = length
            item_list.handle_rel_marks(sorted_list)
            item_list.handle_dep_marks(sorted_list)
            length = item_list.number_of_rel_groups()
        if length:
            item_list.print_unhandled_items()
        return ItemGroup(sorted_list, item_list.group_order())


def scope_from_name(name):
    if name == "module":
        return MODULE
    if name == "class":
        return CLASS
    return SESSION


def scoped_node_id(node_id, scope):
    if scope == MODULE:
        return node_id[:node_id.index("::")]
    if scope == CLASS:
        return node_id[:node_id.rindex("::")]
    return ""


def move_item(mark, sorted_items):
    if (mark.item not in sorted_items or
            mark.item_to_move not in sorted_items or
            mark.item.nr_rel_items):
        return False
    pos_item = sorted_items.index(mark.item)
    pos_item_to_move = sorted_items.index(mark.item_to_move)
    if mark.item_to_move.order is not None and mark.item.order is None:
        # if the item to be moved has already been ordered numerically,
        # and the other item is not ordered, we move that one instead
        mark.move_after = not mark.move_after
        mark.item, mark.item_to_move = mark.item_to_move, mark.item
        pos_item, pos_item_to_move = pos_item_to_move, pos_item
    mark.item_to_move.dec_rel_marks()
    if mark.move_after:
        if pos_item_to_move < pos_item + 1:
            del sorted_items[pos_item_to_move]
            sorted_items.insert(pos_item, mark.item_to_move)
    else:
        if pos_item_to_move > pos_item:
            del sorted_items[pos_item_to_move]
            pos_item -= 1
            sorted_items.insert(pos_item + 1, mark.item_to_move)
    return True


class GroupSorter:
    def __init__(self, scope, groups, rel_marks, dep_marks):
        self.scope = scope
        self.groups = groups
        self.rel_marks = self.collect_group_marks(rel_marks)
        self.dep_marks = self.collect_group_marks(dep_marks)

    def collect_group_marks(self, marks):
        group_marks = []
        for mark in marks:
            group = self.group_for_item(mark.item)
            group_to_move = self.group_for_item(mark.item_to_move)
            if group is not None and group_to_move is not None:
                group_marks.append(
                    RelativeMark(group, group_to_move, mark.move_after))
                group_to_move.inc_rel_marks()
        return group_marks

    def group_for_item(self, item):
        return next((group for group in self.groups if item in group.items),
                    None)

    def sorted_groups(self):
        group_order = self.sort_by_ordinal_markers()
        length = len(self.rel_marks) + len(self.dep_marks)
        if length == 0:
            return group_order, self.groups

        # handle relative markers the same way single items are handled
        still_left = 0
        while length and still_left != length:
            still_left = length
            self.handle_rel_marks(self.rel_marks)
            self.handle_rel_marks(self.dep_marks)
        return group_order, self.groups

    def sort_by_ordinal_markers(self):
        start_groups = []
        middle_groups = []
        end_groups = []
        for group in self.groups:
            if group.order is None:
                middle_groups.append(group)
            elif group.order >= 0:
                start_groups.append(group)
            else:
                end_groups.append(group)
        start_groups = sorted(start_groups, key=lambda g: g.order)
        end_groups = sorted(end_groups, key=lambda g: g.order)
        self.groups = start_groups + middle_groups + end_groups
        if start_groups:
            group_order = start_groups[0].order
        elif end_groups:
            group_order = end_groups[-1].order
        else:
            group_order = None
        return group_order

    def handle_rel_marks(self, marks):
        for mark in reversed(marks):
            if move_item(mark, self.groups):
                marks.remove(mark)


class Item:
    def __init__(self, item):
        self.item = item
        self.nr_rel_items = 0
        self.order = None
        self._node_id = None

    def inc_rel_marks(self):
        if self.order is None:
            self.nr_rel_items += 1

    def dec_rel_marks(self):
        if self.order is None:
            self.nr_rel_items -= 1

    @property
    def module_path(self):
        return self.item.nodeid[:self.node_id.index("::")]

    def parent_path(self, level):
        return "/".join(self.module_path.split("/")[:level])

    @property
    def node_id(self):
        if self._node_id is None:
            # in pytest < 4 the nodeid has an unwanted ::() part
            self._node_id = self.item.nodeid.replace("::()", "")
        return self._node_id

    @property
    def label(self):
        return self.node_id.replace(".py::", ".").replace("/", ".")


class ItemList:
    """Handles a group of items with the same scope."""

    def __init__(self, items, settings, scope, rel_marks, dep_marks):
        self.items = items
        self.settings = settings
        self.scope = scope
        self.start_items = []
        self.end_items = []
        self.unordered_items = []
        self._start_items = {}
        self._end_items = {}
        self.all_rel_marks = rel_marks
        self.all_dep_marks = dep_marks
        self.rel_marks = filter_marks(rel_marks, items)
        self.dep_marks = filter_marks(dep_marks, items)

    def collect_markers(self, item):
        if item.order is not None:
            self.handle_order_mark(item)
        if item.nr_rel_items or item.order is None:
            self.unordered_items.append(item)

    def handle_order_mark(self, item):
        if item.order < 0:
            self._end_items.setdefault(item.order, []).append(item)
        else:
            self._start_items.setdefault(item.order, []).append(item)

    def sort_numbered_items(self):
        self.start_items = sorted(self._start_items.items())
        self.end_items = sorted(self._end_items.items())
        sorted_list = []
        index = 0
        for entries in self.start_items:
            if self.settings.sparse_ordering:
                while entries[0] > index and self.unordered_items:
                    sorted_list.append(self.unordered_items.pop(0))
                    index += 1
            sorted_list += entries[1]
            index += len(entries[1])
        mid_index = len(sorted_list)
        index = -1
        for entries in reversed(self.end_items):
            if self.settings.sparse_ordering:
                while entries[0] < index and self.unordered_items:
                    sorted_list.insert(mid_index, self.unordered_items.pop())
                    index -= 1
            sorted_list[mid_index:mid_index] = entries[1]
            index -= len(entries[1])
        sorted_list[mid_index:mid_index] = self.unordered_items
        return sorted_list

    def print_unhandled_items(self):
        msg = " ".join([mark.item.label for mark in self.rel_marks] +
                       [mark.item.label for mark in self.dep_marks])
        if msg:
            sys.stdout.write(
                "\nWARNING: cannot execute test relative to others: ")
            sys.stdout.write(msg)
            sys.stdout.write("- ignoring the marker.\n")
            sys.stdout.flush()

    def number_of_rel_groups(self):
        return len(self.rel_marks) + len(self.dep_marks)

    def handle_rel_marks(self, sorted_list):
        self.handle_relative_marks(self.rel_marks, sorted_list,
                                   self.all_rel_marks)

    def handle_dep_marks(self, sorted_list):
        self.handle_relative_marks(self.dep_marks, sorted_list,
                                   self.all_dep_marks)

    @staticmethod
    def handle_relative_marks(marks, sorted_list, all_marks):
        for mark in reversed(marks):
            if move_item(mark, sorted_list):
                marks.remove(mark)
                all_marks.remove(mark)

    def group_order(self):
        if self.start_items:
            return self.start_items[0][0]
        if self.end_items:
            return self.end_items[-1][0]


class ItemGroup:
    """Holds a group of sorted items with the same group order scope.
    Used for sorting groups similar to Item for sorting items.
    """

    def __init__(self, items=None, order=None):
        self.items = items or []
        self.order = order
        self.nr_rel_items = 0

    def inc_rel_marks(self):
        if self.order is None:
            self.nr_rel_items += 1

    def dec_rel_marks(self):
        if self.order is None:
            self.nr_rel_items -= 1

    def extend(self, groups, order):
        for group in groups:
            self.items.extend(group.items)
        self.order = order


class RelativeMark:
    """Represents a marker for an item or an item group.
    Holds two related items or groups and their relationship.
    """

    def __init__(self, item, item_to_move, move_after):
        self.item = item
        self.item_to_move = item_to_move
        self.move_after = move_after
