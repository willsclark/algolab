import time
from pathlib import Path
from typing import Callable

import sorts
from models import AlgoData, AlgoStats, Benchmark, PermutationType, Sort, TrialGroup
from permutation import Permutation
from plot import Metric, load_stats, plot_sort_vs_perms
from storage import OutputManager, create_out_dir

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
SEED = 1234
INTERVALS = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
N_TRIALS = 30
SORTS: list[Callable] = [
    sorts.insertion_sort,
    sorts.tim_sort,
    sorts.skip_sort,
    sorts.shell_sort1,
    sorts.shell_sort2,
    sorts.shell_sort3,
    sorts.shell_sort4,
    sorts.shell_sort5,
]

# map permutation type -> generator method name on Permutation
PERM_GENERATORS = {
    PermutationType.UNIFORM: "unif",
    PermutationType.NEAR_SORTED: "almost_sorted",
    PermutationType.TWO_ALTERNATING: "two_alternating",
}


def run_trial(sort_fn: Callable, seq: list[int]) -> AlgoData:
    arr = seq.copy()
    t0 = time.perf_counter()
    comparisons = sort_fn(arr)[0]
    elapsed = time.perf_counter() - t0
    return AlgoData(time=elapsed, comparisons=comparisons)


def benchmark_sort(
    sort_fn: Callable,
    inputs: dict[PermutationType, dict[int, list[list[int]]]],
) -> AlgoStats:
    benchmarks: dict[PermutationType, Benchmark] = {}
    for perm_type, per_size in inputs.items():
        interval_groups: dict[int, TrialGroup] = {}
        for n, trial_lists in per_size.items():
            trials = {t: run_trial(sort_fn, seq) for t, seq in enumerate(trial_lists)}
            interval_groups[n] = TrialGroup(trials=trials)
        benchmarks[perm_type] = Benchmark(benchmark=interval_groups)
    return AlgoStats(sort=Sort(sort_fn.__name__), benchmarks=benchmarks)


def main() -> None:
    pi = Permutation(SEED)

    # Pre-generate all inputs so every sort sees the same ones
    inputs: dict[PermutationType, dict[int, list[list[int]]]] = {}
    for perm_type, method_name in PERM_GENERATORS.items():
        gen = getattr(pi, method_name)
        inputs[perm_type] = {n: [gen(n) for _ in range(N_TRIALS)] for n in INTERVALS}

    for sort_fn in SORTS:
        stats = benchmark_sort(sort_fn, inputs)
        out_dir = create_out_dir(sort_fn.__name__)
        om = OutputManager(out_dir)
        om.save_stats(stats)


def graph() -> None:
    """Creates graphs from the output/algo/stats.json"""

    for sort_fn in SORTS:
        sort_fn_stats_path = OUTPUT_DIR / sort_fn.__name__ / "stats.json"

        stats: AlgoStats = load_stats(sort_fn_stats_path)
        fig = plot_sort_vs_perms(stats, metric=Metric.CMPS)
        om = OutputManager(out_dir=OUTPUT_DIR / sort_fn.__name__)
        om.save_graph(fig)


if __name__ == "__main__":
    graph()
