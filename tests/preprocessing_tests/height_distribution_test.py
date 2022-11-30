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
                [tree_strata[0], 0.0, 10],  [(135, 1.784, 2.187),
                                            (135, 2.002, 2.336),
                                            (135, 2.116, 2.413),
                                            (135, 2.199, 2.469),
                                            (135, 2.268, 2.515),
                                            (135, 2.331, 2.557),
                                            (135, 2.391, 2.597),
                                            (135, 2.452, 2.639),
                                            (135, 2.524, 2.686),
                                            (135, 2.630, 2.757)]
            ),
            (
                [tree_strata[1], 0.0, 10],  [(135, 0.0, 1.222),
                                            (135, 0.657, 1.307),
                                            (135, 0.752, 1.351),
                                            (135, 0.820, 1.383),
                                            (135, 0.877, 1.410),
                                            (135, 0.927, 1.434),
                                            (135, 0.974, 1.457),
                                            (135, 1.023, 1.481),
                                            (135, 1.079, 1.508),
                                            (135, 1.162, 1.549)]
            ),
            (
                [tree_strata[2], 0.0, 10],  [(135, 0.0, 0.785),
                                            (135, 0.0, 0.840),
                                            (135, 0.0, 0.869),
                                            (135, 0.0, 0.890),
                                            (135, 0.0, 0.907),
                                            (135, 0.0, 0.923),
                                            (135, 0.0, 0.938),
                                            (135, 0.0, 0.953),
                                            (135, 0.0, 0.971),
                                            (135, 0.0, 0.998)]
            ),
            (
                [tree_strata[3], 0.0, 10],  [(135, 0.0, 1.090),
                                            (135, 0.0, 1.167),
                                            (135, 0.0, 1.206),
                                            (135, 0.0, 1.235),
                                            (135, 0.0, 1.259),
                                            (135,0.0, 1.281),
                                            (135, 0.646, 1.301),
                                            (135, 0.692, 1.323),
                                            (135, 0.744, 1.347),
                                            (135, 0.822, 1.384)]
            ),
            (
                [tree_strata[4], 0.0, 1],   [(1350, 1.80, 2.50)]
            )
        ]
        for i in assertions:
            tree_list = distributions.sapling_height_distribution(*i[0])
            asse = iter(i[1])
            for tree in tree_list:
                f = round(tree.stems_per_ha, 3)
                d = round(tree.breast_height_diameter, 3)
                h = round(tree.height, 3)
                result = (f, d, h)
                self.assertEqual(next(asse), result)
