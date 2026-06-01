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
        Apply relative constraints to sorted_list.

        Three-phase strategy:
        1. Pre-screen impossible marks - constraints whose anchor is pinned by
           an absolute ordinal in a section opposite to where the unpinned
           mover can land are dropped with a warning, so they do not displace
           pinned items during the iterative pass.
        2. Iterative move_item passes - preserves the position of items not
           involved in constraints, matching the original algorithm.
        3. Topological fallback - reorders only items whose constraints the
           iterative pass could not satisfy (e.g. items with both absolute
           and relative markers).

        Returns True if all constraints were satisfied.
        """
        if not self.rel_marks and not self.dep_marks:
            return True

        self._drop_impossible_marks()
        if not self.rel_marks and not self.dep_marks:
            return True

        self._apply_iterative(sorted_list)
        if not self.rel_marks and not self.dep_marks:
            return True

        return self._apply_topological_fallback(sorted_list)

    def _drop_impossible_marks(self) -> None:
        pinned = {item for item in self.items if item.order is not None}
        impossible_rel = warn_ordinal_conflicts(self.rel_marks, pinned)
        self._remove_marks(self.rel_marks, self.all_rel_marks, impossible_rel)
        impossible_dep = warn_ordinal_conflicts(self.dep_marks, pinned)
        self._remove_marks(self.dep_marks, self.all_dep_marks, impossible_dep)

    @staticmethod
    def _remove_marks(
        marks: list["RelativeMark[Item]"],
        all_marks: list["RelativeMark[Item]"],
        to_remove: list["RelativeMark[Item]"],
    ) -> None:
        for mark in to_remove:
            mark.item_to_move.dec_rel_marks()
            marks.remove(mark)
            all_marks.remove(mark)

    def _apply_iterative(self, sorted_list: list[Item]) -> None:
        still_left = 0
        length = self.number_of_rel_groups()
        while length and still_left != length:
            still_left = length
            self.handle_rel_marks(sorted_list)
            self.handle_dep_marks(sorted_list)
            length = self.number_of_rel_groups()

    def _apply_topological_fallback(self, sorted_list: list[Item]) -> bool:
        items_with_rel_constraints = set()
        for mark in self.rel_marks + self.dep_marks:
            items_with_rel_constraints.add(mark.item_to_move)

        start_items = [item for item in sorted_list if item.order is not None and item.order >= 0]
        end_items = [item for item in sorted_list if item.order is not None and item.order < 0]
        middle_items = [item for item in sorted_list if item.order is None]

        has_start_constraints = any(item in items_with_rel_constraints for item in start_items)
        has_end_constraints = any(item in items_with_rel_constraints for item in end_items)

        if has_start_constraints:
            start_pinned: list[Item] = []
            middle_movable = start_items + middle_items
        else:
            start_pinned = start_items
            middle_movable = middle_items

        if has_end_constraints:
            end_pinned: list[Item] = []
            middle_movable += end_items
        else:
            end_pinned = end_items

        all_pinned = set(start_pinned + end_pinned)
        warn_ordinal_conflicts(self.rel_marks + self.dep_marks, all_pinned)

        sorted_middle, had_cycle = sort_by_topology(
            middle_movable, self.rel_marks, self.dep_marks
        )

        sorted_list[:] = start_pinned + sorted_middle + end_pinned

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
) -> list["RelativeMark[Item]"]:
    """Warn about relative constraints that reference a pinned anchor in a
    direction that cannot be satisfied given the absolute ordering section
    boundaries. Returns the list of such impossible marks."""
    impossible: list["RelativeMark[Item]"] = []
    for mark in marks:
        anchor, moving = mark.item, mark.item_to_move
        if anchor not in pinned or moving in pinned or anchor.order is None:
            continue
        if mark.move_after and anchor.order < 0:
            sys.stdout.write(
                f"\nWARNING: cannot place '{moving.item.name}' after"
                f" '{anchor.item.name}' - '{anchor.item.name}' has an ordinal"
                f" marker that places it after all relatively-ordered tests.\n"
            )
            impossible.append(mark)
        elif not mark.move_after and anchor.order >= 0:
            sys.stdout.write(
                f"\nWARNING: cannot place '{moving.item.name}' before"
                f" '{anchor.item.name}' - '{anchor.item.name}' has an ordinal"
                f" marker that places it before all relatively-ordered tests.\n"
            )
            impossible.append(mark)
    sys.stdout.flush()
    return impossible


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