import unittest
from typing import List, Callable, Tuple

class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: List[Tuple], fn: Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)
