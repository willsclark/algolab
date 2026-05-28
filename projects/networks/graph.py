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
        n = self._num_nodes
        output_list = list()

        # d_v for each vertex in G = num of neighbors not in output list, L

        D = []
        for v in self.vertices:
            D.append(self.get_vertex_degree(v))

        N_v = list(n)

        k = 0

        for i in range(n):
            pass

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
