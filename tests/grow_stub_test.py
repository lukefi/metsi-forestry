import unittest
from forestdatamodel.model import ReferenceTree
from forestryfunctions.naturalprocess.grow_stub import grow_saplings

class GrowStubTest(unittest.TestCase):
    def test_grow_sapling(self):
        diameters = [1.0, 1.1, 1.2, None]
        heights = [0.5, 0.9, 1.2, 1.6]
        sapling_trees = [
            ReferenceTree(breast_height_diameter=d, height=h, sapling=True)
            for d, h in zip(diameters, heights)
        ]
        result = grow_saplings(sapling_trees)
        self.assertEqual(1.0, result[0].breast_height_diameter)
        self.assertEqual(1.1, result[1].breast_height_diameter)
        self.assertEqual(1.2, result[2].breast_height_diameter)
        self.assertEqual(1.0, result[3].breast_height_diameter)
        self.assertEqual(0.8, result[0].height)
        self.assertEqual(1.2, result[1].height)
        self.assertEqual(1.5, result[2].height)
        self.assertEqual(1.6, result[3].height)
        self.assertEqual(True, result[0].sapling)
        self.assertEqual(True, result[1].sapling)
        self.assertEqual(False, result[2].sapling)
        self.assertEqual(False, result[3].sapling)
