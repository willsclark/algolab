from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, computed_field


def _waste(bins_used: int, total_size: int) -> int:
    """
    Returns the waste, W(A) of an algorithm
    """
    assert total_size >= bins_used
    return total_size - bins_used


class BinPackingAlgo(Enum):
    NF = "next_fit"
    BF = "best_fit"
    BFD = "best_fit_decreasing"
    FF = "first_fit"
    FFD = "first_fit_decreasing"


@dataclass
class ProblemInstance:
    items: list[float]
    assignments: list[int]
    free_space: list[float]


class _TrialGroup(BaseModel):
    type Waste = int
    trials: dict[int, Waste]

    @computed_field
    @property
    def average(self) -> Waste:
        if not self.trials:
            return 0.0
        count = len(self.trials)
        waste = sum(w for w in self.trials.values())
        return waste / count


class BPStats(BaseModel):
    """
    A BaseModel for storing the waste created
    by each algorithm
    """

    algorithm: BinPackingAlgo
    benchmarks: dict[int, _TrialGroup]
