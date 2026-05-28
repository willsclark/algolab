# explanations for these functions are provided in requirements.py

from collections import deque

from graph import Graph


def _bfs(graph: Graph, root: Graph.Node) -> tuple[Graph.Node, int]:
    """
    BFS from 'root': returns (farthest node, distance to it)
    """
    visited = {root}
    queue = deque([(root, 0)])
    farthest_node = root
    max_dist = 0

    while queue:
        node, dist = queue.popleft()
        if dist > max_dist:
            max_dist = dist
            farthest_node = node

        for neighbor in graph.get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return farthest_node, max_dist


def get_diameter(graph: Graph) -> int:
    """
    Hueristic 2:
            1) Let r be a random vertex and set D_max = 0

            2) Perform a BFS from r

            3) Select the farthest node, w, in this BFS.
                    - If the distance from r to w is larger than D_max, set D_max to this
                    distance, let r = w, and repeat the above two steps
    """
    r = graph.get_random_vertex()

    d_max = 0

    while True:
        w, dist = _bfs(graph, r)
        if dist > d_max:
            d_max = dist
            r = w
        else:
            break

    return d_max


def __num_2_edge_paths(graph: Graph) -> int:
    total = 0
    for v in graph.vertices:
        d = graph.get_vertex_degree(v)
        total += (d * (d - 1)) // 2
    return total


def __num_triangles(graph: Graph):
    count = 0
    vertices = list(graph.vertices)
    n = len(vertices)

    for i in range(n):
        u = vertices[i]
        for j in range(i + 1, n):
            v = vertices[j]
            if not graph.has_edge(u, v):
                continue
            for k in range(j + 1, n):
                w = vertices[k]
                if graph.has_edge(v, w) and graph.has_edge(u, w):
                    count += 1

    return count


def get_clustering_coefficient(graph: Graph) -> float:

    return (3 * __num_triangles(graph)) / __num_2_edge_paths(graph)


def get_degree_distribution(graph: Graph) -> dict[int, int]:
    histogram: dict[int, int] = {}

    for v in graph.vertices:
        d = graph.get_vertex_degree(v)
        histogram[d] = histogram.get(d, 0) + 1
    return histogram


#     raise NotImplementedError
#
#     """Degree Distribution Algorithm
#
# 	I) Compute the degree, deg(v), of each vertex v.
# 		- If G is represented as an adjacency list, count the number of
# 		elements in v's list
# 	II) Create a Histogram count array, H, of size n, and initialize each
# 		H[i] = 0
# 	III) For each vertex, v, increment H[Deg(v)]
# 	IV) Plot the values of H from 0 to n-1 on a regular and log-log scale
# 	V) If the values on the log-log plot form a straight line, determine its slope to
# 	find the exponent of the power law degree distribution
#
# 	"""
