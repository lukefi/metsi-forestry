import unittest
from typing import List, Callable, Tuple
import numpy as np

DEFAULT_TIMBER_PRICE_TABLE = np.array(
                        [[  1., 160., 370.,  55.],
                        [  1., 160., 400.,  57.],
                        [  1., 160., 430.,  59.],
                        [  1., 160., 460.,  59.],
                        [  2.,  70., 300.,  17.]])

class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: List[Tuple], fn: Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)
