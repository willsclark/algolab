"""Defining and running experiments."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from random import Random
from typing import Any, Callable

from algolab.results import Cell, ExperimentResult

# (variant_payload, condition, size, rng) -> {metric_name: value}
RunTrial = Callable[[Any, str, int, Random], dict[str, float]]

_DEFAULT_CONDITION = "default"


class Registry:
    """A name → callable table, populated by decorator.

    Lets a study collect its algorithms declaratively::

        sorts = Registry()

        @sorts.register()
        def insertion_sort(arr): ...

    then pass ``sorts.items()`` as an experiment's variants.
    """

    def __init__(self) -> None:
        self._items: dict[str, Callable] = {}

    def register(self, name: str | None = None) -> Callable[[Callable], Callable]:
        def decorator(fn: Callable) -> Callable:
            self._items[name or fn.__name__] = fn
            return fn

        return decorator

    def items(self) -> dict[str, Callable]:
        return dict(self._items)


@dataclass
class Experiment:
    """A complete, runnable experiment specification."""

    name: str
    variants: dict[str, Any]  # name -> payload passed to run_trial
    metrics: list[str]  # metric names each trial must return
    run_trial: RunTrial
    sizes: list[int]
    conditions: list[str] = field(default_factory=lambda: [_DEFAULT_CONDITION])
    n_trials: int = 30
    seed: int = 1234


def _derive_seed(master: int, condition: str, size: int, trial: int) -> int:
    """A stable 64-bit seed for one trial, independent of platform and variant."""
    key = f"{master}|{condition}|{size}|{trial}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big")


def _check_metrics(measured: dict[str, float], expected: list[str]) -> dict[str, float]:
    if set(measured) != set(expected):
        msg = f"run_trial returned metrics {sorted(measured)}, expected {sorted(expected)}"
        raise ValueError(msg)
    return measured


def run_experiment(exp: Experiment) -> ExperimentResult:
    """Run every trial and collect an :class:`ExperimentResult`."""
    cells: dict[str, dict[str, dict[int, Cell]]] = {}
    for variant, payload in exp.variants.items():
        cells[variant] = {}
        for condition in exp.conditions:
            cells[variant][condition] = {}
            for size in exp.sizes:
                trials = []
                for trial in range(exp.n_trials):
                    rng = Random(_derive_seed(exp.seed, condition, size, trial))
                    measured = exp.run_trial(payload, condition, size, rng)
                    trials.append(_check_metrics(measured, exp.metrics))
                cells[variant][condition][size] = Cell(trials=trials)

    return ExperimentResult(
        name=exp.name,
        sizes=exp.sizes,
        conditions=exp.conditions,
        variants=list(exp.variants),
        metrics=exp.metrics,
        n_trials=exp.n_trials,
        seed=exp.seed,
        cells=cells,
    )


def shared_input_trial(
    generate: Callable[[str, int, Random], Any],
    measure: Callable[[Any, Any], dict[str, float]],
) -> RunTrial:
    """Compose a ``run_trial`` for the common "one input, many variants" case.

    ``generate(condition, size, rng)`` builds a fresh input; ``measure(payload,
    input)`` runs the variant on it and returns metrics. Because the input is
    regenerated per trial from a variant-independent seed, every variant is
    measured on identical inputs and mutation is harmless.
    """

    def run_trial(payload: Any, condition: str, size: int, rng: Random) -> dict[str, float]:
        return measure(payload, generate(condition, size, rng))

    return run_trial
