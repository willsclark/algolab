"""The unified result schema shared by every study.

An experiment measures one or more *metrics* (time, comparisons, waste,
clustering coefficient, ...) for each combination of:

  * *variant*   — the thing under study (a sort function, a fit heuristic, ...),
  * *condition* — the input regime (a permutation type, an item distribution;
                  ``"default"`` when a study has only one), and
  * *size*      — the input size ``n``.

Every (variant, condition, size) cell holds the raw per-trial measurements plus
lazily-computed per-metric aggregates. This one schema serializes to JSON for
all three studies, so ``storage``, ``plot``, ``fit``, and ``analysis`` never
need to know which study produced the data.
"""

from __future__ import annotations

import statistics
from typing import Iterable

from pydantic import BaseModel, computed_field

# Which aggregate statistic a caller wants when reducing trials to one number.
_STAT_ATTR = {
    "mean": "mean",
    "median": "median",
    "min": "minimum",
    "max": "maximum",
}


class Aggregate(BaseModel):
    """Summary of one metric across the trials in a single cell."""

    mean: float
    median: float
    std: float
    minimum: float
    maximum: float
    n: int

    @classmethod
    def from_values(cls, values: Iterable[float]) -> "Aggregate":
        vals = list(values)
        if not vals:
            return cls(mean=0.0, median=0.0, std=0.0, minimum=0.0, maximum=0.0, n=0)
        return cls(
            mean=statistics.fmean(vals),
            median=statistics.median(vals),
            std=statistics.pstdev(vals) if len(vals) > 1 else 0.0,
            minimum=min(vals),
            maximum=max(vals),
            n=len(vals),
        )


class Cell(BaseModel):
    """All trials for one (variant, condition, size), with lazy aggregates."""

    trials: list[dict[str, float]]

    @computed_field
    @property
    def aggregate(self) -> dict[str, Aggregate]:
        metrics = self.trials[0].keys() if self.trials else []
        return {
            metric: Aggregate.from_values(t[metric] for t in self.trials)
            for metric in metrics
        }


class ExperimentResult(BaseModel):
    """The complete output of one experiment: metadata plus a cell grid.

    ``cells`` is indexed ``[variant][condition][size]``. Use :meth:`series` to
    pull a size-vs-metric curve ready for fitting or plotting.
    """

    name: str
    sizes: list[int]
    conditions: list[str]
    variants: list[str]
    metrics: list[str]
    n_trials: int
    seed: int
    cells: dict[str, dict[str, dict[int, Cell]]]

    def series(
        self,
        variant: str,
        condition: str,
        metric: str,
        stat: str = "median",
    ) -> tuple[list[int], list[float]]:
        """Return ``(sizes, values)`` for one variant/condition/metric curve.

        ``stat`` selects which aggregate to read: ``mean|median|min|max``.
        """
        if stat not in _STAT_ATTR:
            msg = f"unknown stat {stat!r}; choose one of {sorted(_STAT_ATTR)}"
            raise ValueError(msg)
        attr = _STAT_ATTR[stat]

        sizes: list[int] = []
        values: list[float] = []
        by_size = self.cells[variant][condition]
        for size in self.sizes:
            cell = by_size.get(size)
            if cell is None or metric not in cell.aggregate:
                continue
            sizes.append(size)
            values.append(getattr(cell.aggregate[metric], attr))
        return sizes, values
