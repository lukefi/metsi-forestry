from dataclasses import dataclass
from typing import Optional
from forestdatamodel.enums.internal import TreeSpecies

@dataclass
class CrossCutAggregate:
    volume: float
    value: float


@dataclass
class TreeThinData:
    stems_removed_per_ha: float
    species: TreeSpecies
    breast_height_diameter: float
    height: float


@dataclass
class ThinningOutput:
    removed: list[TreeThinData]
    cross_cut_result: Optional[CrossCutAggregate] = None

