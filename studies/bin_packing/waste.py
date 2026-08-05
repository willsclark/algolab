"""The bin-packing cost metric.

An algorithm packs items of size in (0, 1] into unit-capacity bins. *Waste* is
the total empty space left across the bins it opened: ``bins_used - total_item_size``.
Fewer, fuller bins means less waste, so lower is better.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProblemInstance:
    """One packing problem: the items plus the mutable output buffers the
    algorithms fill in (``assignments[i]`` = bin of item i; ``free_space[j]`` =
    remaining capacity of bin j).
    """

    items: list[float]
    assignments: list[int]
    free_space: list[float]

    @classmethod
    def of(cls, items: list[float]) -> "ProblemInstance":
        return cls(items=list(items), assignments=[0] * len(items), free_space=[])


def waste(bins_used: int, total_size: float) -> float:
    assert bins_used >= total_size
    return bins_used - total_size
