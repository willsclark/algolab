"""Timing methodology.

Wall-clock timing is noisy: the OS scheduler, CPU frequency scaling, and the
garbage collector all inject variance that has nothing to do with the algorithm.
This module centralizes the mitigations so every study measures the same way:

  * a warmup call (so caches / branch predictors are hot),
  * ``perf_counter_ns`` for the highest-resolution monotonic clock,
  * the GC disabled during the measured region,
  * the *median* of several repeats (robust to occasional slow runs).
"""

from __future__ import annotations

import gc
import statistics
from dataclasses import dataclass
from time import perf_counter_ns
from typing import Any, Callable


@dataclass(frozen=True)
class Timing:
    """Summary of a repeated timing measurement, in seconds."""

    median: float
    minimum: float
    iqr: float  # inter-quartile range: a robust spread estimate
    repeats: int


def time_call(
    fn: Callable[..., Any],
    *args: Any,
    repeats: int = 5,
    warmup: int = 1,
) -> Timing:
    """Time ``fn(*args)`` ``repeats`` times and return a robust summary.

    The callable is invoked fresh each repeat; if it mutates its arguments the
    caller is responsible for passing copies.
    """
    for _ in range(warmup):
        fn(*args)

    samples_ns: list[int] = []
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(repeats):
            t0 = perf_counter_ns()
            fn(*args)
            samples_ns.append(perf_counter_ns() - t0)
    finally:
        if gc_was_enabled:
            gc.enable()

    samples = sorted(s / 1e9 for s in samples_ns)
    if len(samples) >= 4:
        q1, q3 = statistics.quantiles(samples, n=4)[0], statistics.quantiles(samples, n=4)[2]
        iqr = q3 - q1
    else:
        iqr = samples[-1] - samples[0]

    return Timing(
        median=statistics.median(samples),
        minimum=samples[0],
        iqr=iqr,
        repeats=repeats,
    )
