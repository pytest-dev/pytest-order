import sys
from typing import Optional, Generic, TypeVar
from collections import defaultdict

from pytest import Function, UsageError

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
        Reorder sorted_list to satisfy all relative (before/after and
        dependency) constraints.

        The incoming sorted_list already reflects the absolute ordinal markers,
        which act only as a baseline preference: relative markers always take
        preference, so an ordinal position is relaxed whenever it conflicts with
        a relative constraint (see "Combination of absolute and relative
        ordering" in the docs).

        Two phases:
        1. Iterative move_item passes satisfy the constraints that can be met by
           moving a single item, preserving the position of items not involved
           in any constraint and the established tie-breaking.
        2. A stable topological sort over the full constraint set re-validates
           the result. It leaves an already-valid baseline unchanged, but
           resolves constraints the iterative pass cannot keep on its own
           (transitive chains, or a marker relative to an ordinal-pinned anchor
           that a later move re-breaks).

        Only a genuine constraint cycle cannot be satisfied; in that case the
        caller reports the offending markers.

        Returns True if all constraints were satisfied (no cycle).
        """
        if not self.rel_marks and not self.dep_marks:
            return True

        rel_marks = list(self.rel_marks)
        dep_marks = list(self.dep_marks)
        self._apply_iterative(sorted_list)

        ordered, had_cycle = self._sort_by_topology(sorted_list, rel_marks, dep_marks)
        sorted_list[:] = ordered
        return not had_cycle

    def _apply_iterative(self, sorted_list: list[Item]) -> None:
        still_left = 0
        length = self.number_of_rel_groups()
        while length and still_left != length:
            still_left = length
            self.handle_rel_marks(sorted_list)
            self.handle_dep_marks(sorted_list)
            length = self.number_of_rel_groups()

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

    def print_unhandled_items(self) -> None:
        failed_items = [mark.item for mark in self.rel_marks] + [
            mark.item for mark in self.dep_marks
        ]
        msg = " ".join([item.node_id for item in failed_items])
        sys.stdout.write("\nWARNING: cannot execute test relative to others: ")
        sys.stdout.write(msg)
        if self.settings.fail_all_on_failed_ordering:
            raise UsageError(
                f"pytest-order: cannot execute test relative to others: {msg}"
            )
        if self.settings.error_on_failed_ordering:
            sys.stdout.write(" - ignoring the marker.\n")
        else:
            sys.stdout.write(".\n")
        sys.stdout.flush()
        if self.settings.error_on_failed_ordering:
            for item in failed_items:
                item.item.fixturenames.insert(0, "fail_after_cannot_order")

    def group_order(self) -> Optional[int]:
        if self.start_items:
            return self.start_items[0][0]
        elif self.end_items:
            return self.end_items[-1][0]
        return None

    def _sort_by_topology(
        self,
        items: list["Item"],
        rel_marks: list["RelativeMark[Item]"],
        dep_marks: list["RelativeMark[Item]"],
    ) -> tuple[list["Item"], bool]:
        """
        Order items so that all relative constraints are satisfied while staying as
        close as possible to the incoming order (the absolute-ordinal baseline).

        Relative constraints take preference over the baseline: each item is emitted
        right after the items it must follow, so a conflicting ordinal position is
        relaxed; items that no constraint orders keep their baseline order. The
        incoming order already encodes the absolute ordinals, so no extra ordinal
        edges are needed.

        Returns (ordered_items, had_cycle). On a constraint cycle the offending edge
        is dropped, all items are still emitted, and had_cycle is True.
        """
        item_set = set(items)
        position = {item: i for i, item in enumerate(items)}
        predecessors = _build_predecessors(rel_marks + dep_marks, item_set)
        for item in items:
            predecessors[item].sort(key=lambda p: position[p])

        result: list[Item] = []
        placed: set[Item] = set()
        on_path: set[Item] = set()
        had_cycle = False

        # Iterative post-order DFS: emit unplaced predecessors before each item.
        for start in items:
            if start in placed:
                continue
            stack: list[tuple[Item, int]] = [(start, 0)]
            on_path.add(start)
            while stack:
                item, next_pred = stack[-1]
                preds = predecessors[item]
                while next_pred < len(preds) and preds[next_pred] in placed:
                    next_pred += 1
                if next_pred < len(preds):
                    pred = preds[next_pred]
                    stack[-1] = (item, next_pred + 1)
                    if pred in on_path:
                        had_cycle = True
                    else:
                        stack.append((pred, 0))
                        on_path.add(pred)
                    continue
                stack.pop()
                on_path.discard(item)
                placed.add(item)
                result.append(item)

        return result, had_cycle


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


def _build_predecessors(
    marks: list["RelativeMark[Item]"],
    item_set: set["Item"],
) -> "defaultdict[Item, list[Item]]":
    """Map each item to the items that must run before it, derived from the
    relative marks. A mark either places item_to_move after item (move_after)
    or before it."""
    predecessors: defaultdict[Item, list[Item]] = defaultdict(list)
    for mark in marks:
        before, after = (
            (mark.item, mark.item_to_move)
            if mark.move_after
            else (mark.item_to_move, mark.item)
        )
        if before in item_set and after in item_set and before is not after:
            predecessors[after].append(before)
    return predecessors
