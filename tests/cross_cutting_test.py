import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions.cross_cutting import cross_cutting
from forestryfunctions.cross_cutting.model import ThinningOutput, TreeThinData
import numpy as np
from parameterized import parameterized
from test_util import DEFAULT_TIMBER_PRICE_TABLE, TestCaseExtension

class CrossCuttingTest(TestCaseExtension):

    def test_cross_cut_stand_returns_total_values(self):
        """This test ensures that the cross_cut_stand returns values that are multiplied by the reference tree's stem count per ha and the stand area."""

       # parameter values selected arbitrarily
        tree = ReferenceTree(
            species=TreeSpecies.PINE,
            breast_height_diameter=45.678,
            height=28.43,
            stems_per_ha=22.3
        )

        stand = ForestStand(
            reference_trees=[tree],
            area=296.23
        )

        volumes, values = cross_cutting.cross_cut_stand(stand, DEFAULT_TIMBER_PRICE_TABLE)

        self.assertEqual(volumes[0], [12.282591004865342, 0.26400044487502494])
        self.assertEqual(values[0], [724.6728692870552, 4.4880075628754215])

    def test_cross_cut_thinning_output(self):
        stand_area = 1.93
        thinned_trees = ThinningOutput(
                            removed= [
                                TreeThinData(
                                    stems_removed_per_ha = 0.006261167484111818,
                                    species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                    breast_height_diameter = 15.57254199723247,
                                    height = 18.293846547993535,
                                ),
                                TreeThinData(
                                    stems_removed_per_ha = 0.003917869416142222,
                                    species = TreeSpecies.PINE,
                                    breast_height_diameter = 16.071397406682646,
                                    height = 23.617432525999664,
                                ),
                                TreeThinData(
                                    stems_removed_per_ha = 0.008092431491823593,
                                    species = TreeSpecies.SPRUCE,
                                    breast_height_diameter = 17.721245087039236,
                                    height = 16.353742669109522,
                                )
                            ]
                        )

        volumes, values = cross_cutting.cross_cut_thinning_output(thinned_trees, stand_area, DEFAULT_TIMBER_PRICE_TABLE)

        self.assertListsAlmostEqual(volumes[0], [0.0, 1.7820312883923654e-06], places=6)
        self.assertListsAlmostEqual(volumes[1], [0.0, 1.5799273712399437e-06], places=6)
        self.assertListsAlmostEqual(volumes[2], [0.0, 2.970425992903034e-06], places=6)

        self.assertListsAlmostEqual(values[0], [0.0, 3.029453190267021e-05], places=6)
        self.assertListsAlmostEqual(values[1], [0.0, 2.6858765311079042e-05], places=6)
        self.assertListsAlmostEqual(values[2], [0.0, 5.049724187935157e-05], places=6)


    
    @parameterized.expand([
        (TreeSpecies.PINE,30,25),
        (TreeSpecies.UNKNOWN_CONIFEROUS, 15.57254199723247, 18.293846547993535),
        (TreeSpecies.SPRUCE, 17.721245087039236, 16.353742669109522)
    ])
    def test_py_implementation_equals_r_implementation(self, species, breast_height_diameter, height):

        py_volumes, py_values = cross_cutting._cross_cut(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)
        r_volumes, r_values = cross_cutting._cross_cut_with_r(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)

        decimals = 6
        py_volumes = np.around(py_volumes, decimals=decimals)
        py_values = np.around(py_values, decimals=decimals)

        r_volumes = np.around(np.array(r_volumes), decimals=decimals)
        r_values = np.around(np.array(r_values), decimals=decimals)

        self.assertTrue(np.array_equal(py_volumes, r_volumes))
        self.assertTrue(np.array_equal(py_values, r_values))
