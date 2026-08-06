# algolab

[![CI](https://github.com/willsclark/algolab/actions/workflows/ci.yml/badge.svg)](https://github.com/willsclark/algolab/actions/workflows/ci.yml)

**A small framework for empirical algorithm analysis — and three studies built on it.**

Theory tells you an algorithm is `O(n log n)`; algolab tells you what the exponent
_actually is_ on your machine, with a confidence interval. Each study registers its
algorithms, input generators, and metrics; the framework runs the trials, aggregates
them, fits an empirical power law `T(n) = c · n^k` with bootstrap confidence intervals,
and plots and stores the results.

## Headline results

Every exponent below is estimated empirically — measured, fit in log-log space, and
bracketed by a 95% bootstrap confidence interval — then checked against theory.

| Study           | Finding                                                          | Empirical exponent     |
| --------------- | ---------------------------------------------------------------- | ---------------------- |
| **Sorting**     | Insertion sort is quadratic on random input…                     | comparisons ~ `n^1.99` |
|                 | …but near-linear when the input is nearly sorted                 | `n^1.13`               |
|                 | Timsort collapses to linear on a two-run input                   | `n^1.00` [1.00, 1.00]  |
| **Bin packing** | Next-fit wastes space linearly in `n`                            | waste ~ `n^1.00`       |
|                 | First/best-fit do far better                                     | `n^0.67`               |
|                 | Sorting first (FFD/BFD) makes waste nearly flat                  | `n^0.01`               |
| **Networks**    | Barabási–Albert graphs are small-world (diameter grows ~`log n`) | ≈ flat                 |
|                 | …and their clustering vanishes as they grow                      | `n^-0.72`              |

## Quickstart

```bash
uv sync                                   # install
uv run python studies/sorts/run.py        # benchmark + fit + save figures/JSON
uv run python studies/bin_packing/run.py
uv run python studies/networks/run.py
```

Each run prints a fit table and writes results (`*.json`) and log-log plots under the
study's `output/`.

## How a study is defined

A study is just a `run_trial` plus a config — everything else is framework:

```python
import algolab as al

exp = al.Experiment(
    name="sorting",
    variants={"insertion_sort": insertion_sort, "tim_sort": tim_sort, ...},
    metrics=["time", "comparisons"],
    run_trial=al.shared_input_trial(generate, measure),
    sizes=[16, 32, 64, ..., 16384],
    conditions=["uniform", "near_sorted", "two_alternating"],
    n_trials=30,
    seed=1234,
)

result = al.run_experiment(exp)                       # variant × condition × size × trials
print(al.format_fit_table(al.fit_table(result, "comparisons", bootstrap=1000)))
al.plot_experiment(result, "insertion_sort", "comparisons")
```

**Reproducibility and fairness come for free.** Each trial's RNG is derived
deterministically from `(seed, condition, size, trial)` — _not_ the variant — so every
algorithm is measured on identical inputs, and a re-run reproduces every number exactly.

## The framework (`src/algolab/`)

| Module          | Responsibility                                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `experiment.py` | `Experiment` spec, `run_experiment` (the trial loop), `Registry`, deterministic seeding                                                            |
| `results.py`    | Unified result schema (`ExperimentResult` → `Cell` → `Aggregate`); metrics are a generic `dict[str, float]`, so all three studies share one schema |
| `measure.py`    | Timing methodology — warmup, `perf_counter_ns`, GC disabled, median + IQR over repeats                                                             |
| `fit.py`        | Power-law estimation with bootstrap confidence intervals on the exponent                                                                           |
| `analysis.py`   | `fit_table` / `format_fit_table` — the payoff layer                                                                                                |
| `plot.py`       | Log-log plotting with fitted-curve overlays                                                                                                        |
| `storage.py`    | JSON round-trip persistence and figure saving                                                                                                      |

Reusable data structures live in `datastructures/` — a `SkipList` (skip-list sort), a
`ZipZipTree` (best/first-fit bin packing), and a `Graph` (the network study) — each tested
in isolation.

## Layout

```
src/algolab/       # the framework
datastructures/    # SkipList, ZipZipTree, Graph
studies/
  sorts/           run.py + permutation.py + sorts/
  bin_packing/     run.py + waste.py + algorithms/
  networks/        run.py + barabasi_albert.py + graph_algorithms.py
tests/             # framework, data-structure (property-based), and algorithm tests
```

## Testing & reproducibility

```bash
uv run pytest      # framework guarantees, property-based invariants, algorithm correctness
uv run ruff check .
```

Property-based tests (via [Hypothesis](https://hypothesis.readthedocs.io/)) check the
invariants that must hold for _any_ input — a skip list always yields a sorted permutation,
a zip-zip tree always satisfies the BST property, a graph always obeys the handshaking
lemma. CI runs lint + tests on every push.

## Writeups

Each study has a LaTeX report under its directory `report/master.pdf`
analyzing the results in depth.
