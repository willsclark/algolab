"""A skip list: a probabilistic, sorted, multi-level linked list.

Each element sits in a tower whose height is drawn from a geometric
distribution (repeated fair coin flips), giving expected ``O(log n)`` search
and insertion with high probability. Search climbs up-and-right then descends,
counting comparisons so callers (e.g. skip-list sort) can measure work done.
"""

from __future__ import annotations

import math
import random

PLUS_INF = math.inf
MINUS_INF = -math.inf

# A fixed stream keeps tower heights — and thus results — reproducible.
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
        """Insert node x immediately after node prev."""
        next = prev.after
        x.before = prev
        x.after = next
        prev.after = x
        next.before = x


class SkipList:
    def __init__(self) -> None:
        """S = [S_0, S_1, ..., S_h]; height h is bounded by c*lg(n)."""
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
        """Climb up-and-right (preferring up) from the bottom-left sentinel,
        then descend. Returns ``(pred(x), comparisons)``.
        """
        cmps = 0
        u: Node = self._levels[0].left  # bottom-left sentinel (-INF)

        # Climb upwards
        while True:
            above = u.above
            if above is not None:
                cmps += 1
                if above.after.element <= x:
                    u = above.after
                    continue

            cmps += 1
            if u.after.element <= x:
                u = u.after
                continue

            break  # can't go up or right

        # Climb down
        while u.below is not None:
            u = u.below
            while u.after.element <= x:
                cmps += 1
                u = u.after
            cmps += 1
        return u, cmps

    def insert(self, x: int | float) -> int:
        """Insert x, growing its tower on fair coin flips. Returns comparisons."""
        pred, cmps = self._up_down_search(x)
        node = Node(element=x)
        self._levels[0].insert(pred, node)
        curr = node

        lvl = 0
        while self._flip():
            lvl += 1
            if lvl >= len(self._levels):
                self._add_level()

            # walk left to a node that has an above pointer (exists on the next level)
            while pred.above is None:
                pred = pred.before

            pred = pred.above
            promoted = Node(element=x)
            self._levels[lvl].insert(pred, promoted)
            promoted.below = curr
            curr.above = promoted
            curr = promoted

        return cmps
