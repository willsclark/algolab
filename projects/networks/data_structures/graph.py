# explanations for member functions are provided in requirements.py
# each file that uses a graph should import it from this file.
from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field


class Graph:
    type Node = int
    type Edge = tuple[Node, Node]
    type AdjacencySet = dict[Node, VertexMap]

    @dataclass(frozen=False)
    class VertexMap:
        adjacencies: set[Graph.Node] = field(default_factory=set)
        edges: set[Graph.Edge] = field(default_factory=set)

    def __init__(self, num_nodes: int, edges: Iterable[Edge]):
        """
        Edges are passed in as (u, v)

        """
        self._num_nodes = num_nodes
        self._edges = list(edges)
        self._adj_set = self._build_adjacency_set()

    def _build_adjacency_set(self) -> AdjacencySet:
        """
        Constructs an adjacency set. We define this to be (for a sample graph ABCD)

        A: Adjacencies {C}, Edges {(A, C)}
        B: Adjacencies {}, Edges {}
        ...

        This gives us O(1) "is adjacent" and O(deg(v)) neighbros
        """
        adj_set: dict[Graph.Node, Graph.VertexMap] = defaultdict(Graph.VertexMap)

        for edge in self._edges:
            u, v = edge
            adj_set[u].adjacencies.add(v)
            adj_set[u].edges.add(edge)

            # Undirected?
            adj_set[v].adjacencies.add(u)
            adj_set[v].edges.add(edge)
        return adj_set

    @property
    def vertices(self) -> list[Node]:
        """Returns all the non-zero vertices"""
        return self._adj_set.keys()

    @property
    def degeneracy_ordering(self) -> list[Node]:

        # 1) Initialize an output list, L to be empth
        L = []
        in_L = set()

        n = len(self.vertices)

        # 2) Compute a number, d_v, for each v in G. Initially degrees of v
        d = {v: len(self._adj_set[v].edges) for v in self.vertices}

        # Step 3: D[i] = set of vertices with d_v == i (not yet in L)
        D = defaultdict(set)
        for v in self.vertices:
            D[d[v]].add(v)

        # Step 4: N_v = neighbors of v that appear before v in L
        N = {v: [] for v in self.vertices}

        k = 0

        for _ in range(n):
            # Find smallest i such that D[i] is nonempty
            i = 0
            while not D[i]:
                i += 1

            # Update degeneracy
            k = max(k, i)

            # Pick any vertex from D[i], add to front of L
            v = next(iter(D[i]))
            D[i].remove(v)
            L.insert(0, v)
            in_L.add(v)

            # For each neighbor w of v not already in L
            for w in self.get_neighbors(v):
                if w not in in_L:
                    # Subtract one from d_w and move w in D
                    D[d[w]].discard(w)
                    d[w] -= 1
                    D[d[w]].add(w)
                    N[v].append(w)

        return L, N

    def get_num_nodes(self) -> int:
        return self._num_nodes

    def get_num_edges(self) -> int:
        return len(self._edges)

    def get_neighbors(self, node: Node) -> Iterable[Node]:
        return self._adj_set[node].adjacencies

    def get_random_vertex(self) -> Node:
        return random.choice(list(self._adj_set.keys()))

    def get_vertex_degree(self, node) -> int:
        return len(self._adj_set[node].adjacencies)

    def has_edge(self, u: Node, v: Node) -> bool:
        return v in self._adj_set[u].adjacencies

    # feel free to define new methods in addition to the above
    # fill in the definitions of each required member function (above),
    # and for any additional member functions you define
