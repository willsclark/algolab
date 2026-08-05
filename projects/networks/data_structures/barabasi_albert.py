"""
A base module for generating a Barabasi-Albert Network
"""

import numpy as np

from data_structures.graph import Graph


def sample_unif(low: int, high: int, generator: np.random.Generator) -> int:

    return int(generator.integers(low=low, high=high, endpoint=True))


def gen_barabasi_albert(d: int, n: int, gen: np.random.Generator) -> Graph:
    """
    Generates a barabasi-albert graph using Alg 5

    Params:
        n, the number of vertices
        d, the minimum degree

    BA generates a network by adding
    X1, X2, X3, ..., Xn \propto degree(X_t), t \in [1, n].

    It generates it via "preferential," so that the initial vertices are
    more heavily favored. Namely, the probability a node X_{t+1} links to
    X_{t} is given by
            P[e(X_{t+1}, X_{t})] = deg(X_{t+1}) / SUM deg(X_{t})
    """

    # Let G_0 denote the initial graph

    M = [0] * (2 * n * d)

    for v in range(n):
        for i in range(d):
            high = 2 * (v * d + i)
            M[high] = v
            r = sample_unif(0, high, gen)
            M[high + 1] = M[r]

    edges = []

    for i in range(n * d):
        # E = E U {M[2i], M[2i + 1]}

        e: Graph.Edge = (M[2 * i], M[2 * i + 1])
        edges.append(e)

    return Graph(n, edges)
