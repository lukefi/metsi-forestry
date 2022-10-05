import unittest
from forestdatamodel.model import TreeStratum
from forestryfunctions.preprocessing import distributions
from tests import test_util


class TestDistributions(test_util.ConverterTestSuite):
    def test_height_distributon(self):
        """
        Testing the generation of reference trees from sapling height distribution

        Input values:(pl: float, H: float, D: float, N: float, Hdom: float, n_trees: int) -
            tree species, mean height, mean diameter, stem number, dominant height, number of trees
        Ouput values:
            List length is equal to the number of of trees in input
            (stems per hectare, diameter, height)
         """
        assertions = \
        [
                (
                    [1.0, 2.5, 1.8, 1350, 0.0, 10],   [(135, 1.78, 2.19),
                                                     (135, 2.00, 2.34),
                                                     (135, 2.12, 2.41),
                                                     (135, 2.20, 2.47),
                                                     (135, 2.27, 2.52),
                                                     (135, 2.33, 2.56),
                                                     (135, 2.39, 2.60),
                                                     (135, 2.45, 2.64),
                                                     (135, 2.52, 2.69),
                                                     (135, 2.63, 2.76)]
                ),
                (
                    [2.0, 1.4, 0.0, 1350, 0.0, 10],   [(135, 0.00, 1.22),
                                                     (135, 0.66, 1.31),
                                                     (135, 0.75, 1.35),
                                                     (135, 0.82, 1.38),
                                                     (135, 0.88, 1.41),
                                                     (135, 0.93, 1.43),
                                                     (135, 0.97, 1.46),
                                                     (135, 1.02, 1.48),
                                                     (135, 1.08, 1.51),
                                                     (135, 1.16, 1.55)]
                ),
                (
                    [1.0, 2.5, 1.8, 1350, 0.0, 1],   [(1350, 1.80, 2.50)]
                )
            ]
        for i in assertions:
            tree_list = distributions.WpituusNOtos(*i[0])
            asse = iter(i[1])
            for tree in tree_list:
                result = (round(tree.stems_per_ha, 2), round(tree.breast_height_diameter,2), round(tree.height,2))
                self.assertEqual(next(asse), result)

