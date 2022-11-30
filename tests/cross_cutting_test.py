import unittest
from typing import Dict

import numpy as np
import rpy2.robjects as robjects
from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand, ReferenceTree
from parameterized import parameterized

import forestryfunctions.r_utils as r_utils
from forestryfunctions.cross_cutting import cross_cutting
from forestryfunctions.cross_cutting.model import (
    CrossCutResult, CrossCuttableTree, cross_cuttable_trees_from_stand)
from tests.test_util import (DEFAULT_TIMBER_PRICE_TABLE,
                             TIMBER_PRICE_TABLE_THREE_GRADES,
                             TestCaseExtension)


class CrossCuttingTest(TestCaseExtension):

    def _cross_cut_with_r(
        self,
        species: TreeSpecies,
        breast_height_diameter: float,
        height: float, 
        timber_price_table,
        div = 10    
        ) -> tuple[Dict, Dict]:
        """This function is used only to to test the python-ported version of the cross-cutting scripts against the original R version."""

        species_string = cross_cutting._cross_cut_species_mapper.get(species, "birch") #birch is used as the default species in cross cutting
        height = round(height)

        r = robjects.r
        r.source("./tests/resources/cross_cutting/cross_cutting_main.R")
        result = r["cross_cut"](species_string, breast_height_diameter, height)
        result = r_utils.convert_r_named_list_to_py_dict(result)
        return (result["volumes"], result["values"])


    def test_cross_cut_thinning_output(self):
        stand_area = 1.93
        thinned_trees = [
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.006261167484111818,
                                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                breast_height_diameter = 15.57254199723247,
                                height = 18.293846547993535,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.003917869416142222,
                                species = TreeSpecies.PINE,
                                breast_height_diameter = 16.071397406682646,
                                height = 23.617432525999664,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.008092431491823593,
                                species = TreeSpecies.SPRUCE,
                                breast_height_diameter = 17.721245087039236,
                                height = 16.353742669109522,
                                source="thin1",
                                time_point=0
                            )
                        ]

        results = []
        for tree in thinned_trees:
            results.extend(cross_cutting.cross_cut_tree(tree, stand_area, DEFAULT_TIMBER_PRICE_TABLE))

        self.assertEqual(len(results), 6)
        self.assertAlmostEqual(sum([r.value_per_ha for r in results]), 0.05577748139, places=6)
        self.assertAlmostEqual(sum([r.volume_per_ha for r in results]), 0.0032810283, places=6)

    
    @parameterized.expand([
        (TreeSpecies.PINE,30,25),
        (TreeSpecies.UNKNOWN_CONIFEROUS, 15.57254199723247, 18.293846547993535),
        (TreeSpecies.SPRUCE, 17.721245087039236, 16.353742669109522)
    ])
    def test_py_implementation_equals_r_implementation(self, species, breast_height_diameter, height):

        unique_timber_grades, py_volumes, py_values = cross_cutting._cross_cut(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)
        r_volumes, r_values = self._cross_cut_with_r(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)

        decimals = 6
        py_volumes = np.around(py_volumes, decimals=decimals)
        py_values = np.around(py_values, decimals=decimals)

        r_volumes = np.around(np.array(r_volumes), decimals=decimals)
        r_values = np.around(np.array(r_values), decimals=decimals)

        self.assertTrue(np.array_equal(py_volumes, r_volumes))
        self.assertTrue(np.array_equal(py_values, r_values))


    def test_cross_cut_returns_three_timber_grades(self):
        stand_area = 1.93
        thinning_output = [
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.006261167484111818,
                                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                breast_height_diameter = 15.57254199723247,
                                height = 18.293846547993535,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.003917869416142222,
                                species = TreeSpecies.PINE,
                                breast_height_diameter = 16.071397406682646,
                                height = 23.617432525999664,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.008092431491823593,
                                species = TreeSpecies.SPRUCE,
                                breast_height_diameter = 17.721245087039236,
                                height = 16.353742669109522,
                                source="thin1",
                                time_point=0
                            )
                        ]
        
        results = []
        for tree in thinning_output:
            results.extend(cross_cutting.cross_cut_tree(tree, stand_area, TIMBER_PRICE_TABLE_THREE_GRADES))

        grades = [r.timber_grade for r in results]
        unique_grades = set(grades)
        self.assertEqual(len(unique_grades), 3)

class CrossCuttableTreesTest(unittest.TestCase):
    def test_CrossCuttableTrees_from_stand(self):
        stand = ForestStand(
            reference_trees=[
                ReferenceTree(
                    species=TreeSpecies.PINE,
                    breast_height_diameter=45.678,
                    height=28.43,
                    stems_per_ha=22.3
                )
            ],
            area=296.23
        )

        res = cross_cuttable_trees_from_stand(stand, source="thin1", time_point=0)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].species, TreeSpecies.PINE)
        self.assertEqual(res[0].breast_height_diameter, 45.678)
        self.assertEqual(res[0].height, 28.43)
        self.assertAlmostEqual(res[0].stems_to_cut_per_ha, 22.3, places=6)


class CrossCutResultTest(unittest.TestCase):
    fixture = CrossCutResult(
            species=TreeSpecies.PINE,
            timber_grade=1,
            volume_per_ha=2.0,
            value_per_ha=10.0,
            stand_area=2.0,
            source="thin1",
            time_point=0
        )

    def test_get_real_volume(self):
        self.assertEqual(self.fixture.get_real_volume(), 4.0)

    def test_get_real_value(self):
        self.assertEqual(self.fixture.get_real_value(), 20.0)





