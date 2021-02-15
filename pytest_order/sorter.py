# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict
from warnings import warn

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
    def __init__(self, config, items):
        self.settings = Settings(config)
        self.items = items

    def sort_items(self):
        if self.settings.scope == SESSION:
            sorted_list = GroupSorter(self.settings, self.items).sort_items()
        elif self.settings.scope == MODULE:
            module_groups = module_item_groups(self.items)
            sorted_list = []
            for module_items in module_groups.values():
                sorted_list.extend(GroupSorter(self.settings,
                                               module_items).sort_items())
        else:  # class scope
            class_groups = class_item_groups(self.items)
            sorted_list = []
            for class_items in class_groups.values():
                sorted_list.extend(GroupSorter(self.settings,
                                               class_items).sort_items())
        return sorted_list


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


class GroupSorter:
    def __init__(self, settings, items):
        self.settings = settings
        self.items = items

    def sort_items(self):
        before_items = {}
        after_items = {}
        dep_items = {}
        if self.settings.group_scope < self.settings.scope:
            sorted_list = []
            if self.settings.scope == SESSION:
                module_items = module_item_groups(self.items)
                module_groups = []
                if self.settings.group_scope == CLASS:
                    for module_item in module_items.values():
                        class_items = class_item_groups(module_item)
                        class_groups = [
                            self.do_modify_items(item, CLASS, before_items,
                                                 after_items, dep_items)
                            for item in class_items.values()]
                        module_group = [[], {}]
                        group_order, class_groups = self.sorted_groups(
                            class_groups, CLASS,
                            before_items, after_items, dep_items
                        )
                        for group in class_groups:
                            module_group[0].extend(group[0])
                            module_group[1].update(group[1])
                        module_groups.append((group_order, module_group[0],
                                              module_group[1]))
                else:
                    module_groups = [
                        self.do_modify_items(item, MODULE, before_items,
                                             after_items, dep_items)
                        for item in module_items.values()]
                for group in self.sorted_groups(
                        module_groups, MODULE,
                        before_items, after_items, dep_items)[1]:
                    sorted_list.extend(group[0])
            else:  # module scope / class group scope
                class_items = class_item_groups(self.items)
                class_groups = [self.do_modify_items(item, CLASS, before_items,
                                                     after_items, dep_items)
                                for item in class_items.values()]
                for group in self.sorted_groups(
                        class_groups, CLASS,
                        before_items, after_items, dep_items)[1]:
                    sorted_list.extend(group[0])
        else:
            sorted_list = self.do_modify_items(
                self.items, SESSION, before_items, after_items, dep_items)[1]

        self.show_unresolved_dep_items(dep_items)
        return sorted_list

    def do_modify_items(self, items, scope, out_before_items, out_after_items,
                        out_dep_items):
        start_item = {}
        end_item = {}
        unordered_list = []
        before_items = {}
        after_items = {}
        dep_items = {}
        alias_names = {}

        for item in items:
            self.mark_binning(item, item.keywords.keys(), start_item, end_item,
                              before_items, after_items, dep_items,
                              unordered_list, alias_names)

        start_item = sorted(start_item.items())
        end_item = sorted(end_item.items())

        sorted_list = self.sort_numbered_items(
            start_item, end_item, unordered_list)

        still_left = 0
        length = len(before_items) + len(after_items) + len(dep_items)
        for rel_items in (before_items, after_items):
            for label, entry in rel_items.items():
                if self.needed_for_group_sort(label, entry[0], scope):
                    for item in rel_items[label]:
                        item.is_rel_mark = False

        while length and still_left != length:
            still_left = length
            remove_labels = []
            for label, before in before_items.items():
                if self.insert_before(label, before, sorted_list):
                    remove_labels.append(label)
            for label in remove_labels:
                del before_items[label]

            remove_labels = []
            for label, after in after_items.items():
                if self.insert_after(label, after, sorted_list):
                    remove_labels.append(label)
            for label in remove_labels:
                del after_items[label]

            remove_labels = []
            for (label, dep_scope), after in dep_items.items():
                name = self.label_from_alias(alias_names, label, dep_scope)
                if name is None:
                    for item in after:
                        if item.is_rel_mark:
                            item.is_rel_mark = False
                            # the label is related to another group,
                            # so the item can now be handled
                            still_left += 1
                elif self.insert_after(name, after, sorted_list):
                    remove_labels.append((label, dep_scope))
            for (label, dep_scope) in remove_labels:
                del dep_items[(label, dep_scope)]

            length = len(before_items) + len(after_items) + len(dep_items)
        if length:
            msg = ""
            msg += self.handle_unhandled_items(
                before_items, out_before_items, scope)
            msg += self.handle_unhandled_items(
                after_items, out_after_items, scope)
            msg += self.handle_unhandled_dep_items(
                dep_items, out_dep_items)
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

    @staticmethod
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

    def mark_binning(self, item, keys, start, end, before, after, dep,
                     unordered, alias):
        handled = False
        order = None
        if "dependency" in keys:
            # always order dependencies if an order mark is present
            # otherwise only if order-dependencies is set
            mark = item.get_closest_marker("dependency")
            if self.settings.order_dependencies or "order" in keys:
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
            alias[name_mark] = self.full_name(item)

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
                before.setdefault(
                    self.full_name(item, before_mark), []).append(item)
            if after_mark:
                after.setdefault(
                    self.full_name(item, after_mark), []).append(item)
            handled = True
        item.is_rel_mark = handled and order is None
        if not handled or order is None:
            unordered.append(item)
            return False
        return True

    def insert_before(self, name, items, sort):
        if name:
            for pos, item in enumerate(sort):
                if not item.is_rel_mark and self.full_name(item).endswith(
                        name):
                    for item_to_insert in items:
                        index = sort.index(item_to_insert)
                        if index > pos:
                            del sort[index]
                            item_to_insert.is_rel_mark = False
                            sort.insert(pos, item_to_insert)
                    return True
        return False

    def insert_after(self, name, items, sort):
        if name:
            for pos, item in reversed(list(enumerate(sort))):
                if self.full_name(item).endswith(name):
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

    def insert_before_group(self, label, scope, items, groups):
        label = self.scoped_label(label, scope)
        sorted_labels = [group[0] for group in groups]
        item_labels = [self.scoped_label_from_item(item, scope) for item in
                       items]
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

    def insert_after_group(self, label, scope, items, groups):
        if label:
            label = self.scoped_label(label, scope)
            sorted_labels = [group[0] for group in groups]
            item_labels = [self.scoped_label_from_item(item, scope) for item in
                           items]
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

    @staticmethod
    def insert_after_dep_group(group_index, items, groups):
        if group_index is not None:
            found = True
            for item in reversed(items):
                found_item = False
                for index, group in reversed(list(enumerate(groups))):
                    if item in group[1][0]:
                        found_item = True
                        if index < group_index:
                            moved_group = groups[index]
                            del groups[index]
                            group_index -= 1
                            groups.insert(group_index + 1, moved_group)
                found = found and found_item
            return found
        return False

    def sorted_groups(self, groups, scope, before_items, after_items,
                      dep_items):
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
        groups = [(self.scoped_label_from_item(group[0][0], scope), group)
                  for group in groups_sorted]
        still_left = 0
        while length and still_left != length:
            still_left = length
            remove_labels = []
            for label, before in before_items.items():
                if self.insert_before_group(label, scope, before, groups):
                    remove_labels.append(label)
            for label in remove_labels:
                del before_items[label]

            remove_labels = []
            for label, after in after_items.items():
                if self.insert_after_group(label, scope, after, groups):
                    remove_labels.append(label)
            for label in remove_labels:
                del after_items[label]

            remove_labels = []
            for (label, dep_scope), after in dep_items.items():
                group_index = self.group_index_from_label(
                    groups, label, dep_scope)
                if self.insert_after_dep_group(group_index, after, groups):
                    remove_labels.append((label, dep_scope))
            for (label, dep_scope) in remove_labels:
                del dep_items[(label, dep_scope)]

        # remove the label from the groups
        groups_sorted = [group[1] for group in groups]
        return group_order, groups_sorted

    @staticmethod
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

    def scoped_label_from_item(self, item, scope):
        label = (item.nodeid.replace(".py::", ".")
                 .replace("/", ".").replace("::()", ""))
        return self.scoped_label(label, scope)

    def needed_for_group_sort(self, label, item, scope):
        if self.settings.group_scope >= self.settings.scope:
            return False

        name = self.scoped_label(label, scope)
        itemid = self.scoped_label_from_item(item, scope)
        needed = name != itemid
        if not needed and scope == CLASS and self.settings.scope == SESSION:
            return self.needed_for_group_sort(label, item, MODULE)
        return needed

    def group_index_from_label(self, groups, label, scope):
        for index, group in enumerate(groups):
            if self.label_from_alias(group[1][1], label, scope):
                return index

    @staticmethod
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

    def handle_unhandled_items(self, items, out_items, scope):
        msg = ""
        for label, entries in items.items():
            msg += self.handle_unhandled_item(entries, label, out_items, scope)
        return msg

    @staticmethod
    def handle_unhandled_dep_items(items, out_items):
        msg = ""
        for (label, dep_scope), entries in items.items():
            out_items.setdefault((label, dep_scope), []).extend(entries)
        return msg

    def handle_unhandled_item(self, entries, label, out_items, scope):
        msg = ""
        for entry in entries:
            if not self.needed_for_group_sort(label, entry, scope):
                msg = label + " "
            else:
                new_label = self.scoped_label(label, scope)
                out_items.setdefault(new_label, []).append(entry)
        return msg

    @staticmethod
    def show_unresolved_dep_items(dep_items):
        if dep_items:
            sys.stdout.write(
                "\nWARNING: cannot resolve the dependency marker(s): ")
            sys.stdout.write(", ".join(item[0] for item in dep_items))
            sys.stdout.write(" - ignoring the markers.\n")
            sys.stdout.flush()

    def sort_numbered_items(self, start_item, end_item, unordered_list):
        sorted_list = []
        index = 0
        for entries in start_item:
            if self.settings.sparse_ordering:
                while entries[0] > index and unordered_list:
                    sorted_list.append(unordered_list.pop(0))
                    index += 1
            sorted_list += entries[1]
            index += len(entries[1])
        mid_index = len(sorted_list)
        index = -1
        for entries in reversed(end_item):
            if self.settings.sparse_ordering:
                while entries[0] < index and unordered_list:
                    sorted_list.insert(mid_index, unordered_list.pop())
                    index -= 1
            sorted_list[mid_index:mid_index] = entries[1]
            index -= len(entries[1])
        sorted_list[mid_index:mid_index] = unordered_list
        return sorted_list
