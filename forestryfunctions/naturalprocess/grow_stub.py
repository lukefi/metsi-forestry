from typing import List
from forestdatamodel.model import ReferenceTree


def grow_saplings(saplings: List[ReferenceTree]):
    """ Stub for sapling height and diameter growth """
    for sapling in saplings:
        if sapling.height < 1.3:
            sapling.height += 0.3
        if sapling.height >= 1.3:
            sapling.breast_height_diameter = (1.0
                                              if sapling.breast_height_diameter in (0.0, None)
                                              else sapling.breast_height_diameter)
            sapling.sapling = False
    return saplings
