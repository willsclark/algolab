from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, computed_field


def waste(bins_used: int, total_size: float) -> float:
    assert bins_used >= total_size
    return bins_used - total_size


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


class TrialGroup(BaseModel):
    type TrialNum = int
    type Waste = float
    trials: dict[TrialNum, Waste]

    @computed_field
    @property
    def average(self) -> float:
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

    type InputSize = int
    algorithm: BinPackingAlgo
    benchmarks: dict[InputSize, TrialGroup]
