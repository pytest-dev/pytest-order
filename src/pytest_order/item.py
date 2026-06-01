import sys
from typing import Optional, Generic, TypeVar
from collections import defaultdict, deque

from _pytest.python import Function

from .settings import Scope, Settings


_ItemType = TypeVar("_ItemType", "Item", "ItemGroup")


class Item:
    """Represents a single test item."""

    def __init__(self, item: Function, collection_index: int = 0) -> None:
        self.item: Function = item
        self.nr_rel_items: int = 0
        self.order: Optional[int] = None
        self._node_id: Optional[str] = None
        self.collection_index: int = collection_index

    def inc_rel_marks(self) -> None:
        if self.order is None:
            self.nr_rel_items += 1

    def dec_rel_marks(self) -> None:
        if self.order is None:
            self.nr_rel_items -= 1

    @property
    def module_path(self) -> str:
        return self.item.nodeid[: self.node_id.index("::")]

    def parent_path(self, level) -> str:
        return "/".join(self.module_path.split("/")[:level])

    @property
    def node_id(self) -> str:
        if self._node_id is None:
            # in pytest < 4 the nodeid has an unwanted ::() part
            self._node_id = self.item.nodeid.replace("::()", "")
        return self._node_id


class ItemList:
    """Handles a group of items with the same scope."""

    def __init__(
        self,
        items: list[Item],
        settings: Settings,
        scope: Scope,
        rel_marks: list["RelativeMark[Item]"],
        dep_marks: list["RelativeMark[Item]"],
    ) -> None:
        self.items = items
        self.settings = settings
        self.scope = scope
        self.start_items: list[tuple[int, list[Item]]] = []
        self.end_items: list[tuple[int, list[Item]]] = []
        self.unordered_items: list[Item] = []
        self._start_items: dict[int, list[Item]] = {}
        self._end_items: dict[int, list[Item]] = {}
        self.all_rel_marks = rel_marks
        self.all_dep_marks = dep_marks
        self.rel_marks = filter_marks(rel_marks, items)
        self.dep_marks = filter_marks(dep_marks, items)

    def collect_markers(self, item: Item) -> None:
        self.handle_order_mark(item)
        if item.nr_rel_items or item.order is None:
            self.unordered_items.append(item)

    def handle_order_mark(self, item: Item) -> None:
        if item.order is not None:
            if item.order < 0:
                self._end_items.setdefault(item.order, []).append(item)
            else:
                self._start_items.setdefault(item.order, []).append(item)

    def sort_numbered_items(self) -> list[Item]:
        self.start_items = sorted(self._start_items.items())
        self.end_items = sorted(self._end_items.items())
        sorted_list = []
        index = 0
        for order, items in self.start_items:
            if self.settings.sparse_ordering:
                while order > index and self.unordered_items:
                    sorted_list.append(self.unordered_items.pop(0))
                    index += 1
            sorted_list += items
            index += len(items)
        mid_index = len(sorted_list)
        index = -1
        for order, items in reversed(self.end_items):
            if self.settings.sparse_ordering:
                while order < index and self.unordered_items:
                    sorted_list.insert(mid_index, self.unordered_items.pop())
                    index -= 1
            sorted_list[mid_index:mid_index] = items
            index -= len(items)
        sorted_list[mid_index:mid_index] = self.unordered_items
        return sorted_list

    def apply_relative_constraints(self, sorted_list: list[Item]) -> bool:
        """
        Topologically sort items according to relative constraints.
        Items with relative constraints are moved to the middle section, even if
        they have absolute ordinals. If any start/end item has relative constraints,
        ALL items in that section become movable to preserve ordinal order.
        Returns True if all constraints were satisfied.
        """
        if not self.rel_marks and not self.dep_marks:
            return True
        # Collect items that HAVE relative constraints (item_to_move, not just anchors)
        # Note: in RelativeMark, 'item' is the anchor, 'item_to_move' is the item with the marker
        items_with_rel_constraints = set()
        for mark in self.rel_marks + self.dep_marks:
            items_with_rel_constraints.add(mark.item_to_move)

        # Check if any start/end items have relative constraints
        start_items = [item for item in sorted_list if item.order is not None and item.order >= 0]
        end_items = [item for item in sorted_list if item.order is not None and item.order < 0]
        middle_items = [item for item in sorted_list if item.order is None]

        has_start_constraints = any(item in items_with_rel_constraints for item in start_items)
        has_end_constraints = any(item in items_with_rel_constraints for item in end_items)

        # If any item in a section has relative constraints, make the whole section movable
        if has_start_constraints:
            start_pinned = []
            middle_movable = start_items + middle_items
        else:
            start_pinned = start_items
            middle_movable = middle_items

        if has_end_constraints:
            end_pinned = []
            middle_movable += end_items
        else:
            end_pinned = end_items

        # Warn about constraints that reference pinned items in impossible ways
        all_pinned = set(start_pinned + end_pinned)
        warn_ordinal_conflicts(self.rel_marks + self.dep_marks, all_pinned)

        # Topologically sort the middle section
        sorted_middle, had_cycle = sort_by_topology(
            middle_movable, self.rel_marks, self.dep_marks
        )

        # Rebuild: start section + sorted middle + end section
        sorted_list[:] = start_pinned + sorted_middle + end_pinned

        # Clear resolved marks so the caller doesn't warn about them.
        if not had_cycle:
            self.rel_marks.clear()
            self.dep_marks.clear()
        return not had_cycle

    def print_unhandled_items(self) -> None:
        failed_items = [mark.item for mark in self.rel_marks] + [
            mark.item for mark in self.dep_marks
        ]
        msg = " ".join([item.node_id for item in failed_items])
        sys.stdout.write("\nWARNING: cannot execute test relative to others: ")
        sys.stdout.write(msg)
        if self.settings.error_on_failed_ordering:
            sys.stdout.write(" - ignoring the marker.\n")
        else:
            sys.stdout.write(".\n")
        sys.stdout.flush()
        if self.settings.error_on_failed_ordering:
            for item in failed_items:
                item.item.fixturenames.insert(0, "fail_after_cannot_order")

    def number_of_rel_groups(self) -> int:
        return len(self.rel_marks) + len(self.dep_marks)

    def handle_rel_marks(self, sorted_list: list[Item]) -> None:
        self.handle_relative_marks(self.rel_marks, sorted_list, self.all_rel_marks)

    def handle_dep_marks(self, sorted_list: list[Item]) -> None:
        self.handle_relative_marks(self.dep_marks, sorted_list, self.all_dep_marks)

    @staticmethod
    def handle_relative_marks(
        marks: list["RelativeMark[Item]"],
        sorted_list: list[Item],
        all_marks: list["RelativeMark[Item]"],
    ) -> None:
        for mark in reversed(marks):
            if move_item(mark, sorted_list):
                marks.remove(mark)
                all_marks.remove(mark)

    def group_order(self) -> Optional[int]:
        if self.start_items:
            return self.start_items[0][0]
        elif self.end_items:
            return self.end_items[-1][0]
        return None


class ItemGroup:
    """
    Holds a group of sorted items with the same group order scope.
    Used for sorting groups similar to Item for sorting items.
    """

    def __init__(
        self, items: Optional[list[Item]] = None, order: Optional[int] = None
    ) -> None:
        self.items: list[Item] = items or []
        self.order = order
        self.nr_rel_items = 0

    def inc_rel_marks(self) -> None:
        if self.order is None:
            self.nr_rel_items += 1

    def dec_rel_marks(self) -> None:
        if self.order is None:
            self.nr_rel_items -= 1

    def extend(self, groups: list["ItemGroup"], order: Optional[int]) -> None:
        for group in groups:
            self.items.extend(group.items)
        self.order = order


class RelativeMark(Generic[_ItemType]):
    """
    Represents a marker for an item or an item group.
    Holds two related items or groups and their relationship.
    """

    def __init__(
        self,
        item: _ItemType,
        item_to_move: _ItemType,
        move_after: bool,
    ) -> None:
        self.item: _ItemType = item
        self.item_to_move: _ItemType = item_to_move
        self.move_after: bool = move_after


def filter_marks(
    marks: list[RelativeMark[_ItemType]], all_items: list[Item]
) -> list[RelativeMark[_ItemType]]:
    result = []
    for mark in marks:
        if mark.item in all_items and mark.item_to_move in all_items:
            result.append(mark)
        else:
            mark.item_to_move.dec_rel_marks()
    return result


def move_item(mark: RelativeMark[_ItemType], sorted_items: list[_ItemType]) -> bool:
    if (
        mark.item not in sorted_items
        or mark.item_to_move not in sorted_items
        or mark.item.nr_rel_items
    ):
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


def warn_ordinal_conflicts(
    marks: list["RelativeMark[Item]"],
    pinned: set["Item"],
) -> None:
    """Warn when a relative constraint references a pinned item in a way that
    can never be satisfied given the absolute ordering section boundaries."""
    for mark in marks:
        anchor, moving = mark.item, mark.item_to_move
        if anchor not in pinned or moving in pinned:
            continue
        if mark.move_after and anchor.order is not None and anchor.order < 0:
            sys.stdout.write(
                f"\nWARNING: cannot place '{moving.item.name}' after"
                f" '{anchor.item.name}' - '{anchor.item.name}' has an ordinal"
                f" marker that places it after all relatively-ordered tests.\n"
            )
        elif not mark.move_after and anchor.order is not None and anchor.order >= 0:
            sys.stdout.write(
                f"\nWARNING: cannot place '{moving.item.name}' before"
                f" '{anchor.item.name}' - '{anchor.item.name}' has an ordinal"
                f" marker that places it before all relatively-ordered tests.\n"
            )
    sys.stdout.flush()


def sort_by_topology(
    items: list["Item"],
    rel_marks: list["RelativeMark[Item]"],
    dep_marks: list["RelativeMark[Item]"],
) -> tuple[list["Item"], bool]:
    """
    Topologically sort items using relative constraints and ordinal markers.
    Returns (sorted_items, had_cycle).
    Among items with no constraints between them, ordinal order (if present) is preserved.
    """
    item_set = set(items)
    item_position = {item: i for i, item in enumerate(items)}
    successors: dict[Item, list[Item]] = defaultdict(list)
    in_degree: dict[Item, int] = {item: 0 for item in items}

    # Add edges for explicit relative constraints
    for mark in rel_marks + dep_marks:
        # Normalise to a single "A before B" edge.
        a, b = (mark.item, mark.item_to_move) if mark.move_after \
               else (mark.item_to_move, mark.item)
        if a not in item_set or b not in item_set or a is b:
            continue
        successors[a].append(b)
        in_degree[b] += 1

    # Add implicit edges for ordinal ordering
    # If two items both have ordinals, the one with smaller ordinal should come first
    # BUT don't add an edge that would contradict an explicit relative constraint
    ordinal_items = [(item, item.order) for item in items if item.order is not None]
    ordinal_items.sort(key=lambda x: x[1])  # Sort by ordinal value
    for i in range(len(ordinal_items) - 1):
        a, _ = ordinal_items[i]
        b, _ = ordinal_items[i + 1]
        # Only add edge a→b if there's no path from b to a (which would create a cycle)
        # For simplicity, just check if b→a is an explicit edge
        if a not in successors[b] and b not in successors[a]:
            successors[a].append(b)
            in_degree[b] += 1

    # Kahn's algorithm; break ties by input position for stability.
    ready = deque(sorted(
        (item for item in items if in_degree[item] == 0),
        key=lambda x: item_position[x],
    ))
    result: list[Item] = []
    while ready:
        item = ready.popleft()
        result.append(item)
        for successor in sorted(successors[item], key=lambda x: item_position[x]):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                # Keep ready sorted by input position.
                pos = next(
                    (i for i, r in enumerate(ready) if item_position[r] > item_position[successor]),
                    len(ready),
                )
                ready.insert(pos, successor)

    had_cycle = len(result) < len(items)
    if had_cycle:
        # Append cyclic items in input order; the caller will warn.
        result.extend(
            sorted((item for item in items if in_degree[item] > 0), key=lambda x: item_position[x])
        )
    return result, had_cycle