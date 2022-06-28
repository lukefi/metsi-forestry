from typing import Tuple, Callable
from forestdatamodel.model import ForestStand

def iterative_thinning(
        stand: ForestStand,
        thinning_factor: float,
        thin_predicate: Callable,
        extra_factor_solver: Callable
) -> Tuple[ForestStand, dict]:
    n = len(stand.reference_trees)
    c = thinning_factor
    stems_removed = 0.0
    while thin_predicate(stand):
        # cut until lower bound reached
        for i, rt in enumerate(stand.reference_trees):
            thin_factor = c + extra_factor_solver(i, n, c)
            thin_factor = 1.0 if thin_factor > 1.0 else thin_factor
            new_stems_per_ha = rt.stems_per_ha * thin_factor
            stems_removed += rt.stems_per_ha - new_stems_per_ha
            rt.stems_per_ha = new_stems_per_ha
    new_aggregate = { 'stems_removed': stems_removed }
    return (stand, new_aggregate)
