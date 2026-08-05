"""Bin-packing study: waste of five approximation heuristics.

Variants are the fit heuristics; there is a single input regime (item sizes
drawn uniformly from (0, 0.65]); the metric is waste. Best/first-fit use a
zip-zip tree from ``datastructures`` to find a bin in O(log n).

    uv run python studies/bin_packing/run.py
"""

from __future__ import annotations

from pathlib import Path
from random import Random

import algorithms as bp
from waste import ProblemInstance, waste

import algolab as al

HERE = Path(__file__).resolve().parent
SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
N_TRIALS = 5
SEED = 1234
MAX_ITEM_SIZE = 0.65

VARIANTS = {
    fn.__name__: fn
    for fn in (
        bp.best_fit,
        bp.best_fit_decreasing,
        bp.first_fit,
        bp.first_fit_decreasing,
        bp.next_fit,
    )
}


def generate(condition: str, size: int, rng: Random) -> list[float]:
    return [rng.uniform(0.0, MAX_ITEM_SIZE) for _ in range(size)]


def measure(algorithm, items: list[float]) -> dict[str, float]:
    instance = ProblemInstance.of(items)
    algorithm(instance.items, instance.assignments, instance.free_space)
    bins_used = len(instance.free_space)
    return {"waste": waste(bins_used, sum(items))}


def build_experiment() -> al.Experiment:
    return al.Experiment(
        name="bin_packing",
        variants=VARIANTS,
        metrics=["waste"],
        run_trial=al.shared_input_trial(generate, measure),
        sizes=SIZES,
        conditions=["uniform"],
        n_trials=N_TRIALS,
        seed=SEED,
    )


def main() -> None:
    result = al.run_experiment(build_experiment())

    al.save_result(result, al.output_dir(HERE, "bin_packing") / "bin_packing.json")
    for variant in result.variants:
        fig = al.plot_experiment(result, variant, "waste", bootstrap=500)
        al.save_figure(fig, al.output_dir(HERE, variant) / "waste.png")

    print(al.format_fit_table(al.fit_table(result, "waste", bootstrap=1000)))


if __name__ == "__main__":
    main()
