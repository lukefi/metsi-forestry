from dataclasses import dataclass
from itertools import groupby
from typing import Dict, List

from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand


@dataclass
class CrossCutResult:
    species: TreeSpecies
    timber_grade: int
    volume_per_ha: float
    value_per_ha: float
    stand_area: float

    #what's the right word here? "real", "absolute", something else?
    def get_real_volume(self) -> float:
        return self.volume_per_ha*self.stand_area 

    def get_real_value(self) -> float:
        return self.value_per_ha*self.stand_area


@dataclass
class CrossCutResults:
    """
    This type is used to store the results of a cross cut operation in AggregateResults. The methods in this class
    allow calculating some aggregates from the stored results. 
    """
    results: List[CrossCutResult]

    def group_cross_cut_results_by_species(self) -> Dict[TreeSpecies, List[CrossCutResult]]:
        results = sorted(self.results, key=lambda res: res.species)
        grouped = {key: list(res) for key, res in groupby(results, key=lambda res: res.species)}
        return grouped

    def group_cross_cut_data_by_timber_grade(self) -> Dict[int, List[CrossCutResult]]:
        results = sorted(self.results, key=lambda res: res.species)
        grouped = {key: list(res) for key, res in groupby(results, key=lambda res: res.timber_grade)}
        return grouped

    def get_total_cross_cut_volume(self) -> float:
        return sum([c.get_real_volume() for c in self.results])
    
    def get_total_cross_cut_value(self) -> float:
        return sum([c.get_real_value() for c in self.results])


@dataclass
class CrossCuttableTree:
    stems_to_cut_per_ha: float
    species: TreeSpecies
    breast_height_diameter: float
    height: float

@dataclass
class CrossCuttableTrees:
    trees: list[CrossCuttableTree]
    cross_cut_done: bool = False

    @classmethod
    def from_stand(cls, stand: ForestStand) -> "CrossCuttableTrees":
        trees = [CrossCuttableTree(tree.stems_per_ha, tree.species, tree.breast_height_diameter, tree.height) for tree in stand.reference_trees]
        return cls(trees=trees)




