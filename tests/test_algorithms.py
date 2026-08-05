"""Correctness tests for the algorithms each study benchmarks.

The studies measure *how fast* these run; here we check they are *right*.
"""

from __future__ import annotations

import algorithms as bp  # studies/bin_packing/algorithms
import sorts  # studies/sorts/sorts
from graph_algorithms import get_clustering_coefficient, get_diameter
from hypothesis import given
from hypothesis import strategies as st

from datastructures import Graph

ALL_SORTS = [
    sorts.insertion_sort,
    sorts.tim_sort,
    sorts.skip_sort,
    sorts.shell_sort1,
    sorts.shell_sort2,
    sorts.shell_sort3,
    sorts.shell_sort4,
    sorts.shell_sort5,
]
BIN_PACKERS = [
    bp.best_fit,
    bp.best_fit_decreasing,
    bp.first_fit,
    bp.first_fit_decreasing,
    bp.next_fit,
]


@given(st.lists(st.integers(min_value=-500, max_value=500), max_size=200))
def test_every_sort_returns_a_sorted_permutation(items):
    for sort_fn in ALL_SORTS:
        result = sort_fn(list(items))
        ordered = list(result[1])  # (comparisons, sorted_list) for all sorts
        assert ordered == sorted(items), f"{sort_fn.__name__} did not sort"


@given(st.lists(st.floats(min_value=0.01, max_value=0.65), max_size=200))
def test_bin_packers_produce_valid_packings(items):
    for pack in BIN_PACKERS:
        work = list(items)
        assignments = [0] * len(work)
        free_space: list[float] = []
        pack(work, assignments, free_space)

        if not items:
            continue
        # Every item lands in a real bin.
        assert all(0 <= b < len(free_space) for b in assignments)
        # No bin exceeds unit capacity (reconstruct load from assignments).
        loads = [0.0] * len(free_space)
        for size, b in zip(work, assignments):
            loads[b] += size
        assert all(load <= 1.0 + 1e-6 for load in loads), f"{pack.__name__} overfilled a bin"


def test_graph_algorithms_on_a_path():
    # Path 0-1-2-3: diameter 3, clustering 0 (no triangles).
    graph = Graph(4, [(0, 1), (1, 2), (2, 3)])
    assert get_diameter(graph) == 3
    assert get_clustering_coefficient(graph) == 0.0
