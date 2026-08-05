"""Skip-list sort: insert every element into a skip list, then read it off
in order. Comparisons are summed across insertions as the work metric.
"""

from __future__ import annotations

from datastructures.skiplist import SkipList
from sorts.utils import SortingResult


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
