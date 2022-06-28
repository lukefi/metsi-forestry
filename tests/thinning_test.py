import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions.harvest import thinning
from forestryfunctions import forestry_utils as futil

class ThinningTest(unittest.TestCase):

    def test_iterative_thinning(self):
        species = [ TreeSpecies(i) for i in [1,2,3] ]
        diameters = [ 20.0 + i for i in range(0, 3) ]
        stems = [ 200.0 + i for i in range(0, 3) ]
        fixture = ForestStand()
        fixture.reference_trees = [
            ReferenceTree(species=spe, breast_height_diameter=d, stems_per_ha=f)
            for spe, d, f in zip(species, diameters, stems)
        ]

        thinning_factor = 0.97
        basal_area_upper_bound = 18.0
        thin_predicate = lambda stand: basal_area_upper_bound < futil.overall_basal_area(stand)
        extra_factor_solver = lambda i, n ,c: 0
        result_stand, result_aggregates = thinning.iterative_thinning(fixture, thinning_factor, thin_predicate, extra_factor_solver)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertEqual(171.747, round(result_stand.reference_trees[0].stems_per_ha, 3))
        self.assertEqual(172.606, round(result_stand.reference_trees[1].stems_per_ha, 3))
        self.assertEqual(173.464, round(result_stand.reference_trees[2].stems_per_ha, 3))
        self.assertEqual(85.183, round(result_aggregates['stems_removed'], 3))
