"""Property-based tests for the reusable data structures.

Each structure has an invariant that must hold for *any* sequence of
operations, which is exactly what Hypothesis is good at stress-testing.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from datastructures import Graph, SkipList, ZipZipTree


def _skiplist_to_list(sl: SkipList) -> list:
    out = []
    node = sl.L0.left.after
    while node.after is not None:  # stop before the +inf sentinel
        out.append(node.element)
        node = node.after
    return out


@given(st.lists(st.integers(min_value=-1000, max_value=1000)))
def test_skiplist_sorts_and_preserves_multiset(items):
    sl = SkipList()
    for x in items:
        sl.insert(x)
    result = _skiplist_to_list(sl)
    assert result == sorted(items)  # sorted order
    assert sorted(result) == sorted(items)  # nothing added or dropped


def _inorder_keys(tree: ZipZipTree) -> list:
    keys, stack, node = [], [], tree._root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        keys.append(node.key)
        node = node.right
    return keys


@given(st.lists(st.integers(min_value=-10_000, max_value=10_000), unique=True))
def test_zipziptree_is_a_bst_and_finds_values(keys):
    tree = ZipZipTree(capacity=max(len(keys), 2))
    for key in keys:
        tree.insert(key, key * 10)

    # BST invariant: an in-order walk yields the keys in sorted order.
    assert _inorder_keys(tree) == sorted(keys)
    # Every inserted key is retrievable with its value.
    for key in keys:
        assert tree.find(key) == key * 10


@given(
    st.integers(min_value=1, max_value=30),
    st.lists(st.tuples(st.integers(0, 29), st.integers(0, 29))),
)
def test_graph_degree_sum_is_twice_edges(num_nodes, raw_edges):
    # Keep only simple edges (no self-loops, no duplicates) among valid nodes.
    edges = set()
    for u, v in raw_edges:
        if u != v and u < num_nodes and v < num_nodes:
            edges.add((min(u, v), max(u, v)))
    graph = Graph(num_nodes, list(edges))

    degree_sum = sum(graph.get_vertex_degree(v) for v in graph.vertices)
    assert degree_sum == 2 * len(edges)  # handshaking lemma
    for u, v in edges:
        assert graph.has_edge(u, v) and graph.has_edge(v, u)  # undirected
