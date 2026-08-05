from enum import Enum

from pydantic import BaseModel, computed_field


class Sort(str, Enum):
    SKIP = "skip_sort"
    TIM = "tim_sort"
    INSERTION = "insertion_sort"
    SHELL_1 = "shell_sort1"
    SHELL_2 = "shell_sort2"
    SHELL_3 = "shell_sort3"
    SHELL_4 = "shell_sort4"
    SHELL_5 = "shell_sort5"


class PermutationType(str, Enum):
    UNIFORM = "unif"
    NEAR_SORTED = "near_sorted"
    TWO_ALTERNATING = "two_alt"


class AlgoData(BaseModel):
    time: float
    comparisons: int | float


class TrialGroup(BaseModel):
    trials: dict[int, AlgoData]

    @computed_field
    @property
    def average(self) -> AlgoData:
        if not self.trials:
            return AlgoData(time=0.0, comparisons=0)
        count = len(self.trials)
        avg_time = sum(t.time for t in self.trials.values()) / count
        avg_comp = sum(t.comparisons for t in self.trials.values()) / count
        return AlgoData(time=avg_time, comparisons=avg_comp)


class Benchmark(BaseModel):
    benchmark: dict[int, TrialGroup]


class AlgoStats(BaseModel):
    """
    A Base Model for storing algorithm stats into JSON
    """

    sort: Sort
    benchmarks: dict[PermutationType, Benchmark]
