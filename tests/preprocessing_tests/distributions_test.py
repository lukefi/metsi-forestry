from forestdatamodel.model import TreeStratum, ReferenceTree
from forestryfunctions.preprocessing import distributions
from tests import test_util


class TestDistributions(test_util.ConverterTestSuite):
    def test_weibull_coeffs(self):
        assertions = [
            ([1.0, 1.0, 0.0], (0.0, 1.1931032411956006, 2.075882078133891)),
            ([1.0, 1.0, 1.0], (1.0, 0.0, 2.075882078133891)),
            ([28.0, 27.0, None], (13.436882429476194, 16.133339870229843, 3.5793748463876014)),
        ]
        self.run_with_test_assertions(assertions, distributions.weibull_coeffs)

    def test_weibull(self):
        """
        Testing the generation of reference trees from weibull distribution

        Input values:
            number of trees, mean diameter, basal_area, mean height, (optional) minimum diameter
        Ouput values:
            List length is equal to the number of of trees in input
            (stems per hectare, diameter)
         """
        assertions = \
        [
                (
                    [3, 28.0, 27.0, 1.3, 1.0],  [(397.60, 8.64),
                                                 (344.87, 23.91),
                                                 (76.10, 39.19)]
                ),
                (
                    [3, 9.0, 11.0, 7.0, 0.0],   [(3599.74, 3.29),
                                                 (782.04, 9.88),
                                                 (91.22, 16.46)]
                ),
                (
                    [10, 28.0, 27.0, 22.0, None],   [(1.94, 14.67),
                                                     (15.42, 17.14),
                                                     (40.76, 19.62),
                                                     (69.84, 22.09),
                                                     (91.52, 24.56),
                                                     (95.55, 27.03),
                                                     (79.15, 29.50),
                                                     (50.70, 31.98),
                                                     (24.18, 34.45),
                                                     (10.72, 36.92)]
                )
            ]
        for i in assertions:
            tree_list = distributions.weibull(*i[0])
            asse = iter(i[1])
            for tree in tree_list:
                result = (tree.stems_per_ha, tree.breast_height_diameter)
                self.assertEqual(next(asse), result)

    def test_trees_from_simple_height_distribution(self):
        fixture = TreeStratum()
        fixture.mean_diameter = 28.0
        fixture.stems_per_ha = 170.0
        fixture.mean_height = 22.0
        n_trees = 10
        result = distributions.simple_height_distribution(fixture, n_trees)
        self.assertEqual(10, len(result))
        self.assertEqual(17, result[0].stems_per_ha)
        self.assertEqual(17, result[1].stems_per_ha)
        self.assertEqual(28.0, result[0].breast_height_diameter)
        self.assertEqual(28.0, result[1].breast_height_diameter)
        self.assertEqual(22.0, result[0].height)
        self.assertEqual(22.0, result[1].height)

    def test_diameter_model_valkonen(self):
        result = distributions.diameter_model_valkonen(height_rt=10.0)
        self.assertEqual(result, 13.961394503710512)

    def test_diameter_model_siipilehto(self):
        result = distributions.diameter_model_siipilehto(height_rt=10.0, height=12.0, diameter=9.0, dominant_height=1.1)
        self.assertEqual(result, 10.94882228311327)

    def test_predict_sapling_diameters(self):
        assertions = [
            (10.0, 11.55),
            (10.0, 13.96),
            (10.0, 13.96),
            (10.0, 0.0),
            (1.0, 0.0)
        ]
        hs = [10.0, 10.0, 10.0, 10.0, 1.0]
        ds = [8.0, 8.0, 8.0, 8.0, 8.0]
        reference_trees = [
            [ ReferenceTree(
                height=h,
                breast_height_diameter=d) ]
            for h, d in zip(hs, ds)
        ]
        avghs = [20.0, 1.3, 1.2, 1.2, 999.0]
        avgds = [18.0, 0.0, 0.0, 10.0, 999.0]
        strata = [
            TreeStratum(
                mean_height=h,
                mean_diameter=d)
            for h, d in zip(avghs, avgds)
        ]
        for rts, st, ass in zip(reference_trees, strata, assertions):
            result = distributions.predict_sapling_diameters(
                rts,
                height=st.mean_height,
                diameter=st.mean_diameter,
                dominant_height=1.1)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].height, ass[0])
            self.assertEqual(result[0].breast_height_diameter, ass[1])

    def test_weibull_sapling(self):
        assertions = [
            7.8371012020168695,
            8.720685904543247,
            9.19442826383905,
            9.54481956443186,
            9.839019302036084,
            10.106379021414261,
            10.365825850104796,
            10.636249807741741,
            10.949869466788893,
            11.423214009923312,
        ]
        result = distributions.weibull_sapling(
            height=10.0,
            stem_count=99.0,
            dominant_height=1.1,
            n_trees=10)
        self.assertEqual(len(result), 10)
        for res, asse in zip(result, assertions):
            self.assertEqual(res.sapling, True)
            self.assertEqual(res.stems_per_ha, 9.9)
            self.assertEqual(res.height, asse)



