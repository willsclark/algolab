import json

import numpy as np

import data_structures as ds
from algorithms import get_clustering_coefficient, get_degree_distribution, get_diameter
from data_structures.graph import Graph
from network_stats import NetworkStats, Property, TrialGroup
from output_manager import OutputManager, create_out_dir
from plot import plot_degree_distributions, plot_scalar_vs_n

# Re-exports for test compatibility
__all__ = [
    "Graph",
    "get_diameter",
    "get_clustering_coefficient",
    "get_degree_distribution",
]

SEEDS = [123, 321, 213]
N_deg = [1000, 10000, 100000]
N_const = [
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
    2048,
    4096,
    8192,
    16384,
    32768,
    65536,
    131072,
]

D = 5

SCALAR_PROPERTIES = {
    Property.DIAMETER: get_diameter,
    Property.CLUSTERING: get_clustering_coefficient,
}


def construct_network(d: int, n: int, gen: np.random.Generator) -> ds.Graph:
    return ds.gen_barabasi_albert(d, n, gen)


def compute_scalar_stats() -> dict[Property, dict[int, TrialGroup]]:
    all_benchmarks: dict[Property, dict[int, TrialGroup]] = {}
    for prop, fn in SCALAR_PROPERTIES.items():
        benchmarks: dict[int, TrialGroup] = {}
        for n in N_const:
            results: dict[int, float] = {}
            for seed in SEEDS:
                gen = np.random.default_rng(seed)
                G = construct_network(D, n, gen)
                results[seed] = float(fn(G))
            benchmarks[n] = TrialGroup(results=results)

        stats = NetworkStats(property=prop, benchmarks=benchmarks)
        out_dir = create_out_dir(prop.value)
        OutputManager(out_dir).save_stats(stats)
        all_benchmarks[prop] = benchmarks
    return all_benchmarks


def compute_degree_dist_stats() -> dict[int, dict[int, int]]:
    out_dir = create_out_dir(Property.DEGREE_DIST.value)
    raw: dict[int, dict[int, dict[int, int]]] = {}
    first_seed_dists: dict[int, dict[int, int]] = {}

    for n in N_deg:
        raw[n] = {}
        for seed in SEEDS:
            gen = np.random.default_rng(seed)
            G = construct_network(D, n, gen)
            dist = get_degree_distribution(G)
            raw[n][seed] = {int(k): int(v) for k, v in dist.items()}
        first_seed_dists[n] = raw[n][SEEDS[0]]

    stats_path = out_dir / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(raw, f, indent=4)

    return first_seed_dists


def main() -> None:
    print("Computing scalar statistics (diameter and clustering coefficient)...")
    benchmarks = compute_scalar_stats()
    plot_scalar_vs_n(benchmarks)

    print("\nComputing degree distribution statistics...")
    dists = compute_degree_dist_stats()
    plot_degree_distributions(dists)

    print("\nDone. Figures saved to output/")


if __name__ == "__main__":
    main()
