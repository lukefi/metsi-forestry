from dataclasses import dataclass

from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand


@dataclass
class CrossCutResult:
    species: TreeSpecies
    timber_grade: int
    volume_per_ha: float
    value_per_ha: float
    stand_area: float
    source: str
    time_point: int

    #what's the right word here? "real", "absolute", something else?
    def get_real_volume(self) -> float:
        return self.volume_per_ha*self.stand_area 

    def get_real_value(self) -> float:
        return self.value_per_ha*self.stand_area


@dataclass
class CrossCuttableTree:
    stems_to_cut_per_ha: float
    species: TreeSpecies
    breast_height_diameter: float
    height: float
    source: str
    time_point: int
    cross_cut_done: bool = False


def cross_cuttable_trees_from_stand(stand: ForestStand, source: str, time_point: int) -> list[CrossCuttableTree]:
     return [
            CrossCuttableTree(
                tree.stems_per_ha, 
                tree.species, 
                tree.breast_height_diameter, 
                tree.height,
                source,
                time_point
                )
                for tree in stand.reference_trees
            ]
