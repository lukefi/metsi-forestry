from typing import Tuple, Callable
from forestdatamodel.model import ForestStand


def iterative_thinning(
        stand: ForestStand,
        thinning_factor: float,
        thin_predicate: Callable,
        extra_factor_solver: Callable
) -> Tuple[ForestStand, dict]:
    """ Iteratively decreases the stem count of stand reference trees until stoppin condition is met.

    The parameter :extra_factor_solver: may be used to customize the removal of stems.
    If given as (lambda i,n,c: 0) removes same amount of stems from each tree (a.k.a even thinning).

    :param stand: Forest stand instance of forestdatamodel library
    :param thinning_factor: Intensity of the thinning on each iteration
    :param thin_predicate: Condition to stop thinning
    :param extra_factor_solver: Gradually increasing proportion of removal
    :param time_point: Time point of thinning
    :returns: Thinned stand and number of removed stems per reference tree at the given time point
    """
    n = len(stand.reference_trees)
    c = thinning_factor

    #initialises the thinning_output dictionary where stems_removed_per_ha is aggregated to during the thinning operation
    thinning_output = {
        rt.identifier: 
            {
                'stems_removed_per_ha': 0.0,
                'species': rt.species,
                'breast_height_diameter': rt.breast_height_diameter,
                'height': rt.height,
                'stems_per_ha': rt.stems_per_ha,
                'stand_area': stand.area,
            } 
            for rt in stand.reference_trees
        }

    while thin_predicate(stand):
        # cut until lower bound reached
        for i, rt in enumerate(stand.reference_trees):
            thin_factor = c + extra_factor_solver(i, n, c)
            thin_factor = 1.0 if thin_factor > 1.0 else thin_factor
            new_stems_per_ha = rt.stems_per_ha * thin_factor
            thinning_output[rt.identifier]["stems_removed_per_ha"] += rt.stems_per_ha - new_stems_per_ha
            rt.stems_per_ha = new_stems_per_ha

    new_aggregate = {'thinning_output': thinning_output}
    return (stand, new_aggregate)
