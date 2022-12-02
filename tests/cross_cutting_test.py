from typing import Dict

import numpy as np
import rpy2.robjects as robjects
from forestdatamodel.enums.internal import TreeSpecies
from parameterized import parameterized

import forestryfunctions.r_utils as r_utils
from forestryfunctions.cross_cutting import cross_cutting
from tests.test_util import DEFAULT_TIMBER_PRICE_TABLE, TestCaseExtension


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

    
    @parameterized.expand([
        (TreeSpecies.PINE,30,25),
        (TreeSpecies.UNKNOWN_CONIFEROUS, 15.57254199723247, 18.293846547993535),
        (TreeSpecies.SPRUCE, 17.721245087039236, 16.353742669109522)
    ])
    def test_py_implementation_equals_r_implementation(self, species, breast_height_diameter, height):

        unique_timber_grades, py_volumes, py_values = cross_cutting.cross_cut(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)
        r_volumes, r_values = self._cross_cut_with_r(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)

        decimals = 6
        py_volumes = np.around(py_volumes, decimals=decimals)
        py_values = np.around(py_values, decimals=decimals)

        r_volumes = np.around(np.array(r_volumes), decimals=decimals)
        r_values = np.around(np.array(r_values), decimals=decimals)

        self.assertTrue(np.array_equal(py_volumes, r_volumes))
        self.assertTrue(np.array_equal(py_values, r_values))
