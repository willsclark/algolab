from copy import deepcopy
from pathlib import Path
from typing import Callable

import numpy as np

import src.analysis as analysis
import src.bin_packing as bp
from plot import createfig, load_stats

type Waste = int

type InputSize = int
type BPItems = list[int]

SEED = 1234
INPUT_SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
NUM_SEQUENCES = 5
RNG = np.random.default_rng(seed=SEED)

ALGOS: list[Callable] = [
    bp.best_fit,
    bp.best_fit_decreasing,
    bp.first_fit,
    bp.first_fit_decreasing,
    bp.next_fit,
]


def run_trial(
    input: analysis.ProblemInstance,
    algorithm: Callable,
) -> Waste:
    """ """

    trial_copy = deepcopy(input)
    algorithm(trial_copy.items, trial_copy.assignments, trial_copy.free_space)

    bins_used = len(trial_copy.free_space)
    total_size = sum(input.items)
    waste = analysis.waste(bins_used, total_size)

    return waste


def benchmark_sort(
    algorithm: Callable, inputs: dict[InputSize, list[BPItems]]
) -> analysis.BPStats:
    benchmarks: dict[InputSize, analysis.TrialGroup] = {}

    # BPItems = ['i' vals b/t 0, 0.65]
    for input_size, sequences in inputs.items():
        trials = {}
        for trial_num, unif_sequence in enumerate(sequences, start=1):
            instance: analysis.ProblemInstance = analysis.ProblemInstance(
                items=unif_sequence,
                assignments=[0] * len(unif_sequence),
                free_space=list(),
            )
            trials[trial_num] = run_trial(instance, algorithm)
        benchmarks[input_size] = analysis.TrialGroup(trials=trials)
    return analysis.BPStats(algorithm=algorithm.__name__, benchmarks=benchmarks)

    return analysis.BPStats(algorithm=algorithm.__name__, benchmarks=benchmarks)


def generate_uniform_inputs(size: int, number: int) -> list[list[float]]:
    """
    Generates [number] lists of [size] values between 0 and 0.65.
    """
    ret = []

    for _ in range(number):
        # 2. Call the uniform method on the instance
        items = RNG.uniform(low=0.0, high=0.65, size=size).tolist()
        ret.append(items)

    return ret


def store_stats():

    inputs: dict[InputSize, list[BPItems]] = {}

    for i in INPUT_SIZES:
        inputs[i] = generate_uniform_inputs(i, NUM_SEQUENCES)

    for bp_algo in ALGOS:
        stats = benchmark_sort(bp_algo, inputs)
        out_dir = analysis.create_out_dir(bp_algo.__name__)
        om = analysis.OutputManager(out_dir)
        om.save_stats(stats)


def graph_from_output():
    for algo in ALGOS:
        stats_dir = analysis.create_out_dir(algo.__name__)

        stats: analysis.BPStats = load_stats(Path(stats_dir / "stats.json"))
        fig = createfig(stats)
        om = analysis.OutputManager(out_dir=stats_dir)
        om.save_graph(fig)


def main() -> None:
    # store_stats()
    graph_from_output()


if __name__ == "__main__":
    main()
