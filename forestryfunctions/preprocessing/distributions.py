""" Module contains distribution based model functions
    - weibull distribution
    - simple height distribution
"""
import math
from typing import Optional, List, Tuple
from forestdatamodel.model import ReferenceTree, TreeStratum, ForestStand
from forestryfunctions.preprocessing import pre_util
from enum import Enum


# ---- Weibull distribution model ----

def weibull_coeffs(diameter: float, basal_area: float, min_diameter: Optional[float] = None) -> Tuple:
    """ Weight parameter calcualtions for Weibull distribution formula.

    Notice that min_diameter can be used to override the formulation of weight (a).

    :param diameter: Mean diameter
    :param basal_area: Basal area
    :param min_diameter: (optional) Should be a value between [0.0, 4.5]
    :return weight coefficients (a, b, c) used in the Weibull distribution calculation
    """
    w1 = pre_util.get_or_default(min_diameter, math.exp(-1.306454 + (1.154433 * math.log(diameter)) + (math.pow(0.33956, 2) / 2.0)))
    w3 = math.exp(0.64788 - (0.005558 * basal_area) + (0.025530 * diameter) + (math.pow(0.35365,2) / 2.0))
    w2 = (diameter - w1) / (pow((-math.log(0.5)), (1.0 / w3)))
    if w2 < 0.0:
        w2 = 0.0
    return w1, w2, w3


def weibull(n_samples: int, diameter: float, basal_area: float, height: float, min_diameter: Optional[float] = None) -> List[ReferenceTree]:
    """ Computes Stems per hectare and diameter for given number of refernece trees. The values are driven from the Weibull distribution.

    :param n_samples: Number of trees to be created
    :param diameter: Average diameter
    :param basal_area: Basal area
    :param height: Average height
    :param min_diameter: (optional) Minimum diameter used in weight calculation. If given should be a value between [0.0, 4.5]
    :return Given number of trees containing stems per hectare and diameters as object instance members.
    """
    (a, b, c) = weibull_coeffs(diameter, basal_area, min_diameter)

    # x-axis upperlimit
    ax = a + b * math.pow(4.60517, (1.0 / c))

    interval = (ax - a) / float(n_samples)
    if interval < 0.0:
        interval = 1.0

    f1 = 0.0
    xx = a
    result = []
    # For each sample pick-up stems per hectare from Weibull distribution
    for _ in range(1, n_samples + 1):
        xx = xx + interval
        computed_diameter = xx - (interval / 2.0)
        if height < 1.3:
            computed_diameter = 0.0

        f = 1 - math.exp(-math.pow(((xx - a) / b), c))

        if xx >= ax:
            f = 1.0

        p = f - f1 # precentual ratio of stems in sample i
        f1 = f

        stems = (12732.4 * basal_area) / math.pow(computed_diameter, 2.0)
        stems_per_sample = p * stems

        reference_tree = ReferenceTree()
        reference_tree.stems_per_ha = round(stems_per_sample, 2)
        reference_tree.breast_height_diameter = round(computed_diameter, 2)

        result.append(reference_tree)
    return result


# ---- Simple height distribution model ----

def simple_height_distribution(stratum: TreeStratum, n_trees: int) -> List[ReferenceTree]:
    """ Generate N trees from tree stratum.

    For a single tree, height and diameter are obtained from stratum.
    The stem count for single reference tree is the fraction of stratums total stem count.
    Note that the stem count for all trees is even.
    """
    stems_per_tree = stratum.stems_per_ha / n_trees
    result = []
    for _ in range(n_trees):
        reference_tree = ReferenceTree()
        reference_tree.height = stratum.mean_height
        reference_tree.breast_height_diameter = stratum.mean_diameter
        reference_tree.stems_per_ha = stems_per_tree
        result.append(reference_tree)
    return result
