import os 
from typing import Any, Dict

from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand
try:
    import rpy2.robjects as robjects
except ImportError:
    pass

initialised = False


def _set_working_dir_here() -> None:
    """Sets the working directory to forestryfunctions. Currently relies on the current file being directly under forestryfunctions."""
    dirname = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dirname)


def get_r_with_sourced_scripts() -> robjects.R:
    """Returns the R instance that has sourced all required R-scripts. During sourcing, the working directory is set to .../forestryfunctions, after which it's set back to the initial directory."""
    global initialised
    r = robjects.r

    if not initialised:
        original_wd = os.getcwd()
        
        #change wd temporarily
        _set_working_dir_here()
        r.source("./r/cross_cutting/cross_cutting_main.R")
        r.source('./r/lmfor_volume.R')
        initialised = True

        #set wd back to the initial
        os.chdir(original_wd)

    return r


lmfor_species_map = {
    TreeSpecies.PINE: 'pine',
    TreeSpecies.SHORE_PINE: 'pine',
    TreeSpecies.OTHER_PINE: 'pine',
    TreeSpecies.SPRUCE: 'spruce',
    TreeSpecies.BLACK_SPRUCE: 'spruce',
    TreeSpecies.OTHER_SPRUCE: 'spruce',
    TreeSpecies.OTHER_CONIFEROUS: 'spruce',
    TreeSpecies.CURLY_BIRCH: 'birch',
    TreeSpecies.DOWNY_BIRCH: 'birch',
    TreeSpecies.SILVER_BIRCH: 'birch',
    TreeSpecies.OTHER_DECIDUOUS: 'birch'
}


def lmfor_volume(stand: ForestStand) -> float:
    
    r = get_r_with_sourced_scripts()

    source_data = {
        'height': robjects.FloatVector([tree.height for tree in stand.reference_trees]),
        'breast_height_diameter': robjects.FloatVector([tree.breast_height_diameter for tree in stand.reference_trees]),
        'degree_days': robjects.FloatVector([stand.degree_days for _ in range(len(stand.reference_trees))]),
        'species': robjects.StrVector([lmfor_species_map.get(tree.species, 'birch') for tree in stand.reference_trees]),
        'model_type': robjects.StrVector(['scanned' for _ in range(len(stand.reference_trees))])
    }
    df = robjects.DataFrame(source_data)
    volumes = list(r['compute_tree_volumes'](df))
    total_volume = sum(volumes)
    return total_volume

def convert_r_named_list_to_py_dict(named_list) -> Dict[Any, Any]:
    return dict(zip(named_list.names, [list(i) for i in named_list]))