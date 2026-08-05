"""Network study: structure of Barabasi-Albert scale-free graphs.

The single "variant" is BA generation with attachment degree ``D``. Each trial
grows a graph of size ``n`` and measures two scalar properties — diameter and
clustering coefficient — which the framework fits against ``n`` (a small-world
network's diameter should grow like ``log n``). The degree distribution is a
different kind of object (a histogram, not a size-vs-metric curve), so it is
plotted separately rather than forced through the power-law machinery.

    uv run python studies/networks/run.py
"""

from __future__ import annotations

from pathlib import Path
from random import Random

import numpy as np
from barabasi_albert import gen_barabasi_albert
from graph_algorithms import (
    get_clustering_coefficient,
    get_degree_distribution,
    get_diameter,
)

import algolab as al

HERE = Path(__file__).resolve().parent
D = 5  # attachment degree
SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
N_TRIALS = 3
SEED = 1234
DEGREE_DIST_SIZES = [1000, 10000, 100000]


def generate(condition: str, size: int, rng: Random):
    # Bridge the framework's stdlib RNG to numpy's, preserving reproducibility.
    gen = np.random.default_rng(rng.getrandbits(64))
    return gen_barabasi_albert(D, size, gen)


def measure(_payload, graph) -> dict[str, float]:
    return {
        "diameter": float(get_diameter(graph)),
        "clustering": float(get_clustering_coefficient(graph)),
    }


def build_experiment() -> al.Experiment:
    return al.Experiment(
        name="networks",
        variants={"barabasi_albert": None},
        metrics=["diameter", "clustering"],
        run_trial=al.shared_input_trial(generate, measure),
        sizes=SIZES,
        conditions=["default"],
        n_trials=N_TRIALS,
        seed=SEED,
    )


def plot_degree_distribution() -> None:
    """Scatter P(degree) for a few large graphs — expected to be scale-free."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6))
    rng = Random(SEED)
    for n in DEGREE_DIST_SIZES:
        graph = generate("default", n, rng)
        dist = get_degree_distribution(graph)
        degrees = sorted(dist)
        counts = [dist[k] for k in degrees]
        ax.scatter(degrees, counts, s=20, label=f"n = {n}")

    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("degree k")
    ax.set_ylabel("number of vertices with degree k")
    ax.set_title("Barabasi-Albert degree distribution")
    ax.legend()
    fig.tight_layout()
    al.save_figure(fig, al.output_dir(HERE, "degree_dist") / "degree_dist.png")


def main() -> None:
    result = al.run_experiment(build_experiment())
    al.save_result(result, al.output_dir(HERE, "networks") / "networks.json")

    for metric in result.metrics:
        fig = al.plot_experiment(result, "barabasi_albert", metric, bootstrap=500)
        al.save_figure(fig, al.output_dir(HERE, metric) / f"{metric}.png")

    plot_degree_distribution()

    print(al.format_fit_table(al.fit_table(result, "diameter", bootstrap=1000)))
    print(al.format_fit_table(al.fit_table(result, "clustering", bootstrap=1000)))


if __name__ == "__main__":
    main()
