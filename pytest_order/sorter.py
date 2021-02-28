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

    def sort_items(self):
        if self.settings.scope == SESSION:
            sorted_list = ScopeSorter(self.settings, self.items).sort_items()
        elif self.settings.scope == MODULE:
            module_groups = module_item_groups(self.items)
            sorted_list = []
            for module_items in module_groups.values():
                sorted_list.extend(ScopeSorter(self.settings,
                                               module_items).sort_items())
        else:  # class scope
            class_groups = class_item_groups(self.items)
            sorted_list = []
            for class_items in class_groups.values():
                sorted_list.extend(ScopeSorter(self.settings,
                                               class_items).sort_items())
        return [item.item for item in sorted_list]


def module_item_groups(items):
    module_items = OrderedDict()
    for item in items:
        module_items.setdefault(item.module_path, []).append(item)
    return module_items


def class_item_groups(items):
    class_items = OrderedDict()
    for item in items:
        delimiter_index = item.node_id.index("::")
        if "::" in item.node_id[delimiter_index + 2:]:
            delimiter_index = item.node_id.index("::", delimiter_index + 2)
        class_path = item.node_id[:delimiter_index]
        class_items.setdefault(class_path, []).append(item)
    return class_items


class ScopeSorter:
    """Sorts the items for the defined scope."""

    def __init__(self, settings, items):
        self.settings = settings
        self.items = items
        self.before_items = {}
        self.after_items = {}
        self.dep_items = {}

    def sort_items(self):
        if self.settings.group_scope < self.settings.scope:
            if self.settings.scope == SESSION:
                sorted_list = self.sort_in_session_scope()
            else:  # module scope / class group scope
                sorted_list = self.sort_in_module_scope()
        else:
            sorted_list = self.modify_items(self.items, SESSION).items

        self.show_unresolved_dep_items()
        return sorted_list

    def sort_in_session_scope(self):
        sorted_list = []
        module_items = module_item_groups(self.items)
        if self.settings.group_scope == CLASS:
            module_groups = self.sort_class_groups(module_items)
        else:
            module_groups = [
                self.modify_items(item, MODULE)
                for item in module_items.values()]
        sorter = GroupSorter(MODULE, module_groups, self.before_items,
                             self.after_items, self.dep_items)
        for group in sorter.sorted_groups()[1]:
            sorted_list.extend(group.items)
        return sorted_list

    def sort_in_module_scope(self):
        sorted_list = []
        class_items = class_item_groups(self.items)
        class_groups = [self.modify_items(item, CLASS)
                        for item in class_items.values()]
        sorter = GroupSorter(CLASS, class_groups, self.before_items,
                             self.after_items, self.dep_items)
        for group in sorter.sorted_groups()[1]:
            sorted_list.extend(group.items)
        return sorted_list

    def sort_class_groups(self, module_items):
        module_groups = []
        for module_item in module_items.values():
            class_items = class_item_groups(module_item)
            class_groups = [
                self.modify_items(item, CLASS)
                for item in class_items.values()]
            module_group = ItemGroup()
            sorter = GroupSorter(CLASS, class_groups, self.before_items,
                                 self.after_items, self.dep_items)
            group_order, class_groups = sorter.sorted_groups()
            module_group.extend(class_groups, group_order)
            module_groups.append(module_group)
        return module_groups

    def modify_items(self, items, scope):
        item_list = ItemList(items, self.settings, scope)
        for item in items:
            item_list.mark_binning(item)

        sorted_list = item_list.sort_numbered_items()
        item_list.update_rel_mark()

        still_left = 0
        length = item_list.number_of_rel_groups()
        while length and still_left != length:
            still_left = length
            item_list.handle_before_items(sorted_list)
            item_list.handle_after_items(sorted_list)
            still_left += item_list.handle_dep_items(sorted_list)
            length = item_list.number_of_rel_groups()
        if length:
            item_list.print_unhandled_items(
                self.before_items, self.after_items, self.dep_items)
        return ItemGroup(sorted_list, item_list.group_order(),
                         item_list.aliases)

    def show_unresolved_dep_items(self):
        if self.dep_items:
            sys.stdout.write(
                "\nWARNING: cannot resolve the dependency marker(s): ")
            sys.stdout.write(", ".join(item[0] for item in self.dep_items))
            sys.stdout.write(" - ignoring the markers.\n")
            sys.stdout.flush()


def scope_from_name(name):
    if name == "module":
        return MODULE
    if name == "class":
        return CLASS
    return SESSION


def label_from_alias(alias_names, label, scope, prefix):
    name = alias_names.get(label)
    if name or scope == SESSION:
        return name
    prefixed_label = prefix + "::" + label
    if prefixed_label in alias_names:
        return alias_names[prefixed_label]
    for alias in alias_names:
        if "::" in alias:
            name = alias.split("::", 1)[1]
            if scope == CLASS and "::" in name:
                name = name.split("::")[1]
        else:
            name = alias
        if name == label:
            return alias_names[alias]


def scoped_label(label, scope):
    if scope == MODULE:
        if "." not in label:
            return label
        return label[:label.rindex(".")]
    if scope == CLASS:
        if "::" not in label:
            return label
        return label[:label.index("::")]
    return label


def scoped_node_id(node_id, scope):
    if scope == MODULE:
        return node_id[:node_id.index("::")]
    if scope == CLASS:
        return node_id[:node_id.rindex("::")]
    return ""


class GroupSorter:
    def __init__(self, scope, groups, before_items, after_items, dep_items):
        self.scope = scope
        self.groups = groups
        self.before_items = before_items
        self.after_items = after_items
        self.dep_items = dep_items

    def sorted_groups(self):
        group_order = self.sort_by_ordinal_markers()
        length = len(self.before_items) + len(self.after_items) + len(
            self.dep_items)
        if length == 0:
            return group_order, self.groups

        # handle relative markers the same way single items are handled
        # add the group specific label to the sorted groups
        for group in self.groups:
            group.label = group.items[0].scoped_label(self.scope)

        still_left = 0
        while length and still_left != length:
            still_left = length
            self.handle_before_items()
            self.handle_after_items()
            self.handle_dep_items()
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

    @staticmethod
    def handle_rel_items(items, handler):
        remove_labels = []
        for label, item in items.items():
            if label and handler(label, item):
                remove_labels.append(label)
        for label in remove_labels:
            del items[label]

    def handle_before_items(self):
        self.handle_rel_items(self.before_items, self.insert_before_group)

    def handle_after_items(self):
        self.handle_rel_items(self.after_items, self.insert_after_group)

    def handle_dep_items(self):
        remove_labels = []
        for (label, dep_scope, prefix), after in self.dep_items.items():
            group_index = self.group_index_from_label(
                label, dep_scope, prefix)
            if self.insert_after_dep_group(group_index, after):
                remove_labels.append((label, dep_scope, prefix))
        for (label, dep_scope, prefix) in remove_labels:
            del self.dep_items[(label, dep_scope, prefix)]

    def insert_before_group(self, label, items):
        label = scoped_label(label, self.scope)
        sorted_labels = [group.label for group in self.groups]
        item_labels = [item.scoped_label(self.scope) for item in items]
        for pos, group in enumerate(self.groups):
            if group.label.endswith(label):
                for item_label in item_labels:
                    if item_label in sorted_labels:
                        index = sorted_labels.index(item_label)
                        if index > pos:
                            moved_group = self.groups[index]
                            del self.groups[index]
                            self.groups.insert(pos, moved_group)
                return True
        return False

    def insert_after_group(self, label, items):
        label = scoped_label(label, self.scope)
        sorted_labels = [group.label for group in self.groups]
        item_labels = [item.scoped_label(self.scope) for item in items]
        for pos, group in reversed(list(enumerate(self.groups))):
            if group.label.endswith(label):
                for item_label in reversed(item_labels):
                    if item_label in sorted_labels:
                        index = sorted_labels.index(item_label)
                        if index < pos + 1:
                            moved_group = self.groups[index]
                            del self.groups[index]
                            del sorted_labels[index]
                            pos -= 1
                            self.groups.insert(pos + 1, moved_group)
                            sorted_labels.insert(pos + 1, moved_group.label)
                return True
        return False

    def insert_after_dep_group(self, group_index, items):
        if group_index is not None:
            found = True
            for item in reversed(items):
                found_item = False
                for index, group in reversed(list(enumerate(self.groups))):
                    if item in group.items:
                        found_item = True
                        if index < group_index:
                            moved_group = self.groups[index]
                            del self.groups[index]
                            group_index -= 1
                            self.groups.insert(group_index + 1, moved_group)
                found = found and found_item
            return found
        return False

    def group_index_from_label(self, label, scope, prefix):
        for index, group in enumerate(self.groups):
            if label_from_alias(group.aliases, label, scope, prefix):
                return index


class Item:
    def __init__(self, item):
        self.item = item
        self.is_rel_mark = False
        # cache properties that are called often for the same item
        self._node_id = None
        self._label = None
        self._full_names = {}

    @property
    def module_path(self):
        return self.item.nodeid[:self.node_id.index("::")]

    @property
    def node_id(self):
        if self._node_id is None:
            # in pytest < 4 the nodeid has an unwanted ::() part
            self._node_id = self.item.nodeid.replace("::()", "")
        return self._node_id

    @property
    def label(self):
        if self._label is None:
            self._label = self.node_id.replace(".py::", ".").replace("/", ".")
        return self._label

    def calc_full_name(self, name):
        if name and "." in name:
            # assumed to be sufficiently qualified
            return name
        path = self.label
        if name is None:
            return path
        if "::" in path and "::" not in name:
            return path[:path.rindex("::") + 2] + name
        return path[:path.rindex(".") + 1] + name

    def full_name(self, name=None):
        try:
            return self._full_names[name]
        except KeyError:
            self._full_names[name] = self.calc_full_name(name)
            return self._full_names[name]

    def scoped_label(self, scope):
        return scoped_label(self.label, scope)


class ItemList:
    def __init__(self, items, settings, scope):
        self.items = items
        self.settings = settings
        self.scope = scope
        self.start_items = []
        self.end_items = []
        self.unordered_items = []
        self._start_items = {}
        self._end_items = {}
        self.before_items = {}
        self.after_items = {}
        self.dep_items = {}
        self.aliases = {}

    def mark_binning(self, item):
        order = None
        keys = item.item.keywords.keys()
        has_dependency = "dependency" in keys
        has_order = "order" in keys
        if has_dependency:
            self.handle_dependency_mark(item, has_order)
        if has_order:
            order = self.handle_order_mark(item)
        if item.is_rel_mark or order is None:
            self.unordered_items.append(item)

    def handle_dependency_mark(self, item, has_order):
        # always order dependencies if an order mark is present
        # otherwise only if order-dependencies is set
        mark = item.item.get_closest_marker("dependency")
        if self.settings.order_dependencies or has_order:
            dependent_mark = mark.kwargs.get("depends")
            if dependent_mark:
                scope = scope_from_name(mark.kwargs.get("scope", "module"))
                prefix = scoped_node_id(item.node_id, scope)
                for name in dependent_mark:
                    self.dep_items.setdefault(
                        (name, scope, prefix), []).append(item)
                    item.is_rel_mark = True
        # we always collect the names of the dependent items, because
        # we need them in both cases
        name_mark = mark.kwargs.get("name")
        # the default name in pytest-dependency is the nodeid or a part
        # of the nodeid, depending on the scope
        if not name_mark:
            name_mark = item.node_id
        self.aliases[name_mark] = item.full_name()

    def handle_order_mark(self, item):
        mark = item.item.get_closest_marker("order")
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
                order = None
            if order is not None:
                if order < 0:
                    self._end_items.setdefault(order, []).append(item)
                else:
                    self._start_items.setdefault(order, []).append(item)
        if before_mark:
            self.before_items.setdefault(
                item.full_name(before_mark), []).append(item)
        if after_mark:
            self.after_items.setdefault(
                item.full_name(after_mark), []).append(item)
        if order is not None:
            item.is_rel_mark = False
        elif before_mark or after_mark:
            item.is_rel_mark = True
        return order

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

    def update_rel_mark(self):
        for rel_items in (self.before_items, self.after_items):
            for label, entry in rel_items.items():
                if self.needed_for_group_sort(label, entry[0], self.scope):
                    for item in rel_items[label]:
                        item.is_rel_mark = False

    def needed_for_group_sort(self, label, item, scope):
        if self.settings.group_scope >= self.settings.scope:
            return False

        name = scoped_label(label, scope)
        item_id = item.scoped_label(scope)
        needed = name != item_id
        if (not needed and scope == CLASS and
                self.settings.scope == SESSION):
            return self.needed_for_group_sort(label, item, MODULE)
        return needed

    def handle_unhandled_item(self, entries, label, out_items, scope):
        msg = ""
        for entry in entries:
            if not self.needed_for_group_sort(label, entry, scope):
                msg = label + " "
            else:
                new_label = scoped_label(label, scope)
                out_items.setdefault(new_label, []).append(entry)
        return msg

    def print_unhandled_items(self, before_items, after_items, dep_items):
        msg = ""
        msg += self.handle_unhandled_items(
            self.before_items, before_items, self.scope)
        msg += self.handle_unhandled_items(
            self.after_items, after_items, self.scope)
        msg += self.handle_unhandled_dep_items(dep_items)
        if msg:
            sys.stdout.write(
                "\nWARNING: cannot execute test relative to others: ")
            sys.stdout.write(msg)
            sys.stdout.write("- ignoring the marker.\n")
            sys.stdout.flush()

    def handle_unhandled_items(self, items, out_items, scope):
        msg = ""
        for label, entries in items.items():
            msg += self.handle_unhandled_item(entries, label, out_items, scope)
        return msg

    def handle_unhandled_dep_items(self, out_items):
        msg = ""
        for (label, dep_scope, prefix), entries in self.dep_items.items():
            out_items.setdefault(
                (label, dep_scope, prefix), []).extend(entries)
        return msg

    def number_of_rel_groups(self):
        return len(self.before_items) + len(self.after_items) + len(
            self.dep_items)

    @staticmethod
    def handle_rel_items(items, handler, sorted_list):
        remove_labels = []
        for label, item in items.items():
            if label and handler(label, item, sorted_list):
                remove_labels.append(label)
        for label in remove_labels:
            del items[label]

    def handle_before_items(self, sorted_list):
        self.handle_rel_items(
            self.before_items, self.insert_before, sorted_list)

    def handle_after_items(self, sorted_list):
        self.handle_rel_items(
            self.after_items, self.insert_after, sorted_list)

    def handle_dep_items(self, sorted_list):
        remove_labels = []
        nr_unhandled = 0
        for (label, dep_scope, prefix), after in self.dep_items.items():
            name = label_from_alias(self.aliases, label, dep_scope, prefix)
            if name is None:
                for item in after:
                    if item.is_rel_mark:
                        # the label is related to another group,
                        # so the item can now be handled
                        item.is_rel_mark = False
                        nr_unhandled += 1
            elif self.insert_after(name, after, sorted_list):
                remove_labels.append((label, dep_scope, prefix))
        for (label, dep_scope, prefix) in remove_labels:
            del self.dep_items[(label, dep_scope, prefix)]
        return nr_unhandled

    def group_order(self):
        if self.start_items:
            return self.start_items[0][0]
        if self.end_items:
            return self.end_items[-1][0]

    @staticmethod
    def insert_before(name, items, sort):
        for pos, item in enumerate(sort):
            if not item.is_rel_mark and item.full_name().endswith(name):
                for item_to_insert in items:
                    index = sort.index(item_to_insert)
                    if index > pos:
                        del sort[index]
                        item_to_insert.is_rel_mark = False
                        sort.insert(pos, item_to_insert)
                return True
        return False

    @staticmethod
    def insert_after(name, items, sort):
        for pos, item in zip(range(len(sort) - 1, -1, -1), reversed(sort)):
            if item.full_name().endswith(name):
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


class ItemGroup:
    def __init__(self, items=None, order=None, aliases=None):
        self.items = items or []
        self.order = order
        self.aliases = aliases or {}
        self.label = ""

    def extend(self, groups, order):
        for group in groups:
            self.items.extend(group.items)
            self.aliases.update(group.aliases)
        self.order = order
