import unittest
from forestdatamodel.model import TreeStratum
from forestryfunctions.preprocessing import distributions
from tests import test_util


class TestDistributions(test_util.ConverterTestSuite):

    def test_reference_trees_from_height_distribution(self):
        """ Testing the generation of reference trees from sapling height distribution """
        fixture_values = [
            # species, mean_height, mean_diameter, stems_per_ha
            [1.0, 2.5, 1.8, 1350],
            [2.0, 1.4, 0.0, 1350],
            [2.0, 0.9, 0.0, 1350],
            [2.0, 1.25, 0.0, 1350],
            [1.0, 2.5, 1.8, 1350]
        ]
        tree_strata = [
            TreeStratum(
            species=value[0],
            mean_height=value[1],
            mean_diameter=value[2],
            stems_per_ha=value[3])
            for value in fixture_values
        ]
        assertions = \
        [
            (
                # TreeStratum, dominant_height, n_trees
                [tree_strata[0], 0.0, 10],  [(135, 1.78, 2.19),
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
                [tree_strata[1], 0.0, 10],  [(135, 0.00, 1.22),
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
                [tree_strata[2], 0.0, 10],  [(135, 0.00, 0.78),
                                            (135, 0.00, 0.84),
                                            (135, 0.00, 0.87),
                                            (135, 0.00, 0.89),
                                            (135, 0.00, 0.91),
                                            (135, 0.00, 0.92),
                                            (135, 0.00, 0.94),
                                            (135, 0.00, 0.95),
                                            (135, 0.00, 0.97),
                                            (135, 0.00, 1.00)]
            ),
            (
                [tree_strata[3], 0.0, 10],  [(135, 0.00, 1.09),
                                            (135, 0.00, 1.17),
                                            (135, 0.00, 1.21),
                                            (135, 0.00, 1.24),
                                            (135, 0.00, 1.26),
                                            (135, 0.00, 1.28),
                                            (135, 0.65, 1.30),
                                            (135, 0.69, 1.32),
                                            (135, 0.74, 1.35),
                                            (135, 0.82, 1.38)]
            ),
            (
                [tree_strata[4], 0.0, 1],   [(1350, 1.80, 2.50)]
            )
        ]
        for i in assertions:
            tree_list = distributions.sapling_height_distribution(*i[0])
            asse = iter(i[1])
            for tree in tree_list:
                result = (tree.stems_per_ha, tree.breast_height_diameter, tree.height)
                self.assertEqual(next(asse), result)
