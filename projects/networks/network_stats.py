from enum import Enum

from pydantic import BaseModel, computed_field


class Property(Enum):
    DIAMETER = "diam"
    CLUSTERING = "cluster"
    DEGREE_DIST = "deg_dist"


class TrialGroup(BaseModel):
    type Seed = int

    results: dict[Seed, float]

    @computed_field
    @property
    def average(self) -> float:
        if not self.results:
            return 0.0
        return sum(self.results.values()) / len(self.results)


class NetworkStats(BaseModel):
    type InputSize = int
    property: Property
    benchmarks: dict[InputSize, TrialGroup]
