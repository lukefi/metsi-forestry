""" Module contains tree generation logic that uses distribution based tree generation models (see. distributions module) """
import math
from typing import Optional, List, Tuple
from forestdatamodel.model import ReferenceTree, TreeStratum, ForestStand
from enum import Enum
from forestryfunctions.preprocessing import distributions
from forestryfunctions.preprocessing.naslund import naslund_height

class TreeStrategy(Enum):
    SAPLING_TREE = 'sapling_tree'
    WEIBULL_DISTRIBUTION = 'weibull_distribution'
    HEIGHT_DISTRIBUTION = 'height_distribution'
    SKIP = 'skip_tree_generation'


def trees_from_weibull(stratum: TreeStratum, n_trees: int) -> List[ReferenceTree]:
    """ Generate N trees from weibull distribution.

    For a single tree, stem count and diameter are obtained
    from weibull distribution.
    The height is derived with Näslund height prediction model.
    """
    # stems_per_ha and diameter
    result = distributions.weibull(
        n_trees,
        stratum.mean_diameter,
        stratum.basal_area,
        stratum.mean_height)
    # height
    for reference_tree in result:
        height = naslund_height(
            reference_tree.breast_height_diameter,
            stratum.species)
        reference_tree.height = 0.0 if height is None else height
    return result


def finalize_trees(reference_trees: List[ReferenceTree], stratum: TreeStratum) -> List[ReferenceTree]:
    """ For all given trees inflates the common variables from stratum. """
    n_trees = len(reference_trees)
    for i, reference_tree in enumerate(reference_trees):
        reference_tree.stand = stratum.stand
        reference_tree.species = stratum.species
        reference_tree.breast_height_age = 0.0 if n_trees == 1 else stratum.get_breast_height_age()
        reference_tree.biological_age = stratum.biological_age
        reference_tree.tree_number = i + 1
    return reference_trees


def solve_tree_generation_strategy(stratum: TreeStratum) -> str:
    """ Solves the strategy of tree generation for given stratum """
    if stratum.has_height_over_130_cm():
        # big trees
        if stratum.has_diameter() and stratum.has_height() and stratum.has_basal_area():
            return TreeStrategy.WEIBULL_DISTRIBUTION
        elif stratum.has_diameter() and stratum.has_height() and stratum.has_stems_per_ha():
            return TreeStrategy.HEIGHT_DISTRIBUTION
        else:
            return TreeStrategy.SKIP
    else:
        # small trees
        if stratum.has_height() and stratum.has_sapling_stems_per_ha():
            return TreeStrategy.SAPLING_TREE
        else:
            return TreeStrategy.SKIP


def solve_reference_tree_count(stratum: TreeStratum, value: Optional[int]) -> Optional[int]:
    """ Solve reference tree count or use given value"""
    if value is None:
        if stratum.has_height():
            return 10 if stratum.has_height_over_130_cm() else 1
        else:
            return None
    else:
        return value


def reference_trees_from_tree_stratum(stratum: TreeStratum, n_trees: Optional[int] = None) -> List[ReferenceTree]:
    """ Composes N number of reference trees based on values of the stratum.

    The tree generation strategies: weibull distribution, height distribution and singel tree generation.
    From big trees generation strategies are weibull distribution (primary) and height distribution (secondary).
    For small trees a single tree (n_trees == 1) is generated when possible.

    Big trees need diameter, height and basal area or stem count for the generation process to succeed.
    Small trees need only height and stem count.
    All other cases are skipped.

    :param stratum: Single stratum instance.
    :param (optional) n_trees: Number of reference trees to be generated.
    :return: List of reference trees derived from given stratum.
    """
    n_trees = solve_reference_tree_count(stratum, n_trees)
    strategy = solve_tree_generation_strategy(stratum)
    result = []
    if strategy == TreeStrategy.SAPLING_TREE:
        result.append(stratum.to_sapling_reference_tree())
    elif strategy == TreeStrategy.WEIBULL_DISTRIBUTION:
        result = trees_from_weibull(stratum, n_trees)
    elif strategy == TreeStrategy.HEIGHT_DISTRIBUTION:
        result = distributions.reference_trees_from_height_distribution(stratum, n_trees) 
    elif strategy == TreeStrategy.SKIP:
        return []
    else:
        raise UserWarning("Unable to generate reference trees from stratum {}".format(stratum.identifier))
    return finalize_trees(result, stratum)

