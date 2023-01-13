import unittest
from typing import Callable, List, Tuple

import numpy as np

DEFAULT_TIMBER_CONSTANTS = (
    (1, 1, 1, 1, 2),
    (160.0, 160.0, 160.0, 160.0, 70.0),
    (370.0, 400.0, 430.0, 460.0, 300.0),
    (55.0, 57.0, 59.0, 59.0, 17.0)
)


class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: List[Tuple], fn: Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)

class TestCaseExtension(unittest.TestCase):
    def assertListsAlmostEqual(self, first: List, second: List, places: int):
        self.assertEqual(len(first), len(second))
        for i in range(len(first)):
            self.assertAlmostEqual(first[i], second[i], places=places)
