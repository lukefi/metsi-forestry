import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions.harvest import thinning
from forestryfunctions import forestry_utils as futil
from test_util import DEFAULT_TIMBER_PRICE_TABLE

class ThinningTest(unittest.TestCase):

    def test_iterative_thinning(self):
        species = [ TreeSpecies(i) for i in [1,2,3] ]
        diameters = [ 20.0 + i for i in range(0, 3) ]
        stems = [ 200.0 + i for i in range(0, 3) ]
        heights = [ 25.0 + i for i in range(0, 3) ]
        ids = ["tree-1", "tree-2", "tree-3"]
        fixture = ForestStand()
        fixture.reference_trees = [
            ReferenceTree(species=spe, breast_height_diameter=d, stems_per_ha=f, height=h, identifier=id)
            for spe, d, f, h, id in zip(species, diameters, stems, heights, ids)
        ]

        thinning_factor = 0.97
        basal_area_upper_bound = 18.0
        thin_predicate = lambda stand: basal_area_upper_bound < futil.overall_basal_area(stand)
        extra_factor_solver = lambda i, n ,c: 0
        result_stand, result_aggregates = thinning.iterative_thinning(fixture, thinning_factor, thin_predicate, extra_factor_solver, timber_price_table=DEFAULT_TIMBER_PRICE_TABLE)
        self.assertEqual(3, len(result_stand.reference_trees))

        new_stems_per_ha_1 = round(result_stand.reference_trees[0].stems_per_ha, 3)
        new_stems_per_ha_2 = round(result_stand.reference_trees[1].stems_per_ha, 3)
        new_stems_per_ha_3 = round(result_stand.reference_trees[2].stems_per_ha, 3)

        self.assertEqual(171.747, new_stems_per_ha_1)
        self.assertEqual(172.606, new_stems_per_ha_2)
        self.assertEqual(173.464, new_stems_per_ha_3)

        #assert quantities removed
        self.assertEqual(28.253, round((stems[0] - new_stems_per_ha_1), 3))
        self.assertEqual(28.394, round((stems[1] - new_stems_per_ha_2), 3))
        self.assertEqual(28.536, round((stems[2] - new_stems_per_ha_3), 3))


