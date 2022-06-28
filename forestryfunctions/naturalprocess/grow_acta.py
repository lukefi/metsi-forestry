import math
import itertools
from typing import List
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions import forestry_utils as futil


def yearly_diameter_growth_by_species(
    tree: ReferenceTree,
    biological_age_aggregate: float,
    d13_aggregate: float,
    height_aggregate: float,
    dominant_height: float,
    basal_area_total: float
) -> float:
    """ Model source: Acta Forestalia Fennica 163 """
    if tree.species == TreeSpecies.PINE:
        growth_percent = math.exp(5.4625
            - 0.6675 * math.log(biological_age_aggregate)
            - 0.4758 * math.log(basal_area_total)
            + 0.1173 * math.log(d13_aggregate)
            - 0.9442 * math.log(dominant_height)
            - 0.3631 * math.log(tree.breast_height_diameter)
            + 0.7762 * math.log(tree.height))
    else:
        growth_percent = math.exp(6.9342
            - 0.8808 * math.log(biological_age_aggregate)
            - 0.4982 * math.log(basal_area_total)
            + 0.4159 * math.log(d13_aggregate)
            - 0.3865 * math.log(height_aggregate)
            - 0.6267 * math.log(tree.breast_height_diameter)
            + 0.1287 * math.log(tree.height))
    return growth_percent


def yearly_height_growth_by_species(
    tree: ReferenceTree,
    biological_age_aggregate: float,
    d13_aggregate: float,
    height_aggregate: float,
    dominant_height: float,
    basal_area_total: float
) -> float:
    """ Model source: Acta Forestalia Fennica 163 """
    if tree.species == TreeSpecies.PINE:
        growth_percent = math.exp(5.4636
            - 0.9002 * math.log(biological_age_aggregate)
            + 0.5475 * math.log(d13_aggregate)
            - 1.1339 * math.log(tree.height))
    else:
        growth_percent = (12.7402
            - 1.1786 * math.log(biological_age_aggregate)
            - 0.0937 * math.log(basal_area_total)
            - 0.1434 * math.log(d13_aggregate)
            - 0.8070 * math.log(height_aggregate)
            + 0.7563 * math.log(tree.breast_height_diameter)
            - 2.0522 * math.log(tree.height))
    return growth_percent


def grow_diameter_and_height(matures_trees: List[ReferenceTree], years: int = 5):
    """ Diameter and height growth for trees with height > 1.3 meters. Based on Acta Forestalia Fennica 163. """
    basal_area_total = futil.calculate_attribute_sum(matures_trees, futil.calculate_basal_area)
    dominant_height = futil.solve_dominant_height(matures_trees)
    tree_groups = itertools.groupby(matures_trees, key=lambda rt: rt.species)
    # Calculate growth for each tree species
    for _, tree_group in tree_groups:
        trees = list(tree_group)
        breast_height_diameter_wsum = futil.calculate_basal_area_weighted_attribute_sum(
            trees,
            lambda tree: tree.breast_height_diameter * futil.calculate_basal_area(tree))
        height_wsum = futil.calculate_basal_area_weighted_attribute_sum(
            trees,
            lambda tree: tree.height * futil.calculate_basal_area(tree))
        biological_age_wsum = futil.calculate_basal_area_weighted_attribute_sum(
            trees,
            lambda tree: tree.biological_age * futil.calculate_basal_area(tree))
        # Solve and update growth for each tree
        for tree in trees:
            # Calculate yearly growth percents
            growth_percent_diameter = yearly_diameter_growth_by_species(
                tree,
                biological_age_wsum,
                breast_height_diameter_wsum,
                height_wsum,
                dominant_height,
                basal_area_total)
            growth_percent_height = yearly_height_growth_by_species(
                tree,
                biological_age_wsum,
                breast_height_diameter_wsum,
                height_wsum,
                dominant_height,
                basal_area_total)
            # Calculate the growth and update tree
            tree.breast_height_diameter = tree.breast_height_diameter * futil.compounded_growth_factor(
                growth_percent_diameter,
                years)
            tree.height = tree.height * futil.compounded_growth_factor(
                growth_percent_height,
                years)
    return matures_trees
