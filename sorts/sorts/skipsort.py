"""A base module for implementing skip-list sort"""

from __future__ import annotations
import random
import math
from sorts.utils import SortingResult

PLUS_INF = math.inf
MINUS_INF = -math.inf
RNG = random.Random(123)


class Node:
    def __init__(
        self,
        element: int | float,
        before: Node | None = None,
        after: Node | None = None,
        above: Node | None = None,
        below: Node | None = None,
    ) -> None:

        self._before = before
        self._after = after
        self._above = above
        self._below = below
        self._element = element

    @property
    def before(self) -> Node | None:
        return self._before

    @before.setter
    def before(self, x: Node | None) -> None:
        self._before = x

    @property
    def after(self) -> Node | None:
        return self._after

    @after.setter
    def after(self, node: Node | None) -> None:
        self._after = node

    @property
    def above(self) -> Node | None:
        return self._above

    @above.setter
    def above(self, node: Node | None) -> None:
        self._above = node

    @property
    def below(self) -> Node | None:
        return self._below

    @below.setter
    def below(self, node: Node | None) -> None:
        self._below = node

    @property
    def element(self) -> int | float:
        return self._element


class LinkedList:

    def __init__(self) -> None:

        left: Node = Node(element=MINUS_INF)
        right: Node = Node(element=PLUS_INF)
        left.after = right
        right.before = left
        self._left = left
        self._right = right

    @property
    def left(self) -> Node | None:
        return self._left

    @property
    def right(self) -> Node | None:
        return self._right

    def insert(self, prev: Node, x: Node) -> None:
        """Inserts element x after x_i-1"""
        next = prev.after
        x.before = prev
        x.after = next
        prev.after = x
        next.before = x


class SkipList:

    def __init__(self):
        """
        S = [S_0, S_1, ..., S_h]
        h bounded by clg n
        """
        self._levels: list[LinkedList] = [LinkedList()]
        self._rng = RNG if RNG is not None else random.Random()

    @property
    def L0(self) -> LinkedList:
        return self._levels[0]

    def _flip(self) -> bool:
        return self._rng.getrandbits(1) == 1

    def _add_level(self) -> None:
        """Add a new empty level on top, linking sentinels to the level below."""
        old_top = self._levels[-1]
        new_level = LinkedList()

        new_level._left.below = old_top._left
        old_top._left.above = new_level._left
        new_level._right.below = old_top._right
        old_top._right.above = new_level._right
        self._levels.append(new_level)

    def _up_down_search(self, x: int | float) -> tuple[Node, int]:
        """
        Up Down Search starts at the bottom left node, then climbs
        upwards and right as far a possible -- prefering up -- then descends.

        Returns: (u, cmps) where u := pred(x), cmps := # comparisons
        """

        cmps = 0

        # start at bottom left Sentinel
        # u = S_0[0] = -INF
        u: Node = self._levels[0].left

        # Climb Upwards
        while True:
            above = u.above
            # Try to go up
            if above is not None:
                cmps += 1
                if above.after.element <= x:
                    u = above.after
                    continue

            cmps += 1
            # Try to go right
            if u.after.element <= x:
                u = u.after
                continue

            # Can't go up or right
            break

        # Climb Down
        while u.below is not None:
            u = u.below
            while u.after.element <= x:
                cmps += 1
                u = u.after

            cmps += 1
        return u, cmps

    def insert(self, x: int | float) -> int:
        """Returns # comparisons and inserts
        x into Skip list

        Uses (1/2) as probability for growing towers

        """

        pred, cmps = self._up_down_search(x)
        node = Node(element=x)
        self._levels[0].insert(pred, node)
        curr = node

        # GROW TOWER
        lvl = 0
        while self._flip():
            lvl += 1
            if lvl >= len(self._levels):
                self._add_level()

            # Walk left to find a node with an above pointer (meaning that its in the next level)
            while pred.above is None:
                pred = pred.before

            # Go up to that pred (place to insert on upper level)
            pred = pred.above
            promoted = Node(element=x)
            self._levels[lvl].insert(pred, promoted)
            promoted.below = curr
            curr.above = promoted
            curr = promoted

        return cmps


def skip_sort(S: list[int | float]) -> SortingResult:

    sl = SkipList()

    total_cmps = 0
    for x_i in S:
        total_cmps += sl.insert(x_i)

    sorted_list = []
    node = sl.L0.left.after  # Start AFTER -INF

    while node.after is not None:  # Stop before +INF
        sorted_list.append(node.element)
        node = node.after

    return SortingResult(comparisons=total_cmps, sorted_list=sorted_list)
