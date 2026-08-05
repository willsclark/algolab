"""Sorting study: empirical complexity of comparison sorts.

Variants are the sort functions; conditions are input distributions; the
metrics are wall-clock time and comparison count. Everything below the
``Experiment`` is provided by algolab.

    uv run python studies/sorts/run.py          # benchmark, plot, print fits
"""

from __future__ import annotations

from pathlib import Path
from random import Random

import sorts
from permutation import Permutation

import algolab as al

HERE = Path(__file__).resolve().parent
SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
N_TRIALS = 30
SEED = 1234

VARIANTS = {
    fn.__name__: fn
    for fn in (
        sorts.insertion_sort,
        sorts.tim_sort,
        sorts.skip_sort,
        sorts.shell_sort1,
        sorts.shell_sort2,
        sorts.shell_sort3,
        sorts.shell_sort4,
        sorts.shell_sort5,
    )
}

# condition name -> Permutation method that generates that distribution
CONDITIONS = {
    "uniform": "unif",
    "near_sorted": "almost_sorted",
    "two_alternating": "two_alternating",
}


def generate(condition: str, size: int, rng: Random) -> list[int]:
    return getattr(Permutation(rng), CONDITIONS[condition])(size)


def measure(sort_fn, arr: list[int]) -> dict[str, float]:
    comparisons = sort_fn(list(arr))[0]
    timing = al.time_call(lambda a: sort_fn(list(a)), arr, repeats=3, warmup=1)
    return {"time": timing.median, "comparisons": float(comparisons)}


def build_experiment() -> al.Experiment:
    return al.Experiment(
        name="sorting",
        variants=VARIANTS,
        metrics=["time", "comparisons"],
        run_trial=al.shared_input_trial(generate, measure),
        sizes=SIZES,
        conditions=list(CONDITIONS),
        n_trials=N_TRIALS,
        seed=SEED,
    )


def main() -> None:
    result = al.run_experiment(build_experiment())

    al.save_result(result, al.output_dir(HERE, "sorting") / "sorting.json")
    for variant in result.variants:
        fig = al.plot_experiment(result, variant, "comparisons", bootstrap=500)
        al.save_figure(fig, al.output_dir(HERE, variant) / "comparisons.png")

    print(al.format_fit_table(al.fit_table(result, "comparisons", bootstrap=1000)))


if __name__ == "__main__":
    main()
