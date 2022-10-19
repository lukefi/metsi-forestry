from typing import Any, Dict, List, Tuple

import forestryfunctions.r_utils as r_utils
import numpy as np
from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand
from forestryfunctions.cross_cutting import stem_profile
from forestryfunctions.cross_cutting.model import ThinningOutput

_cross_cut_species_mapper = {
    TreeSpecies.PINE: "pine",
    TreeSpecies.SPRUCE: "spruce",
    TreeSpecies.CURLY_BIRCH: "birch",
    TreeSpecies.DOWNY_BIRCH: "birch",
    TreeSpecies.SILVER_BIRCH: "birch"
}


def apteeraus_Nasberg(T: np.ndarray, P: np.ndarray, m: int, n: int, div: int) -> tuple[np.ndarray, np.ndarray]:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    V = np.zeros(n)
    C = np.zeros(n)
    A = np.zeros(n)
    L = np.zeros(n)

    t = 1
    d_top = 0.0
    d_min = 0.0
    v = 0.0
    c = 0.0
    v_tot = 0.0
    c_tot = 0.0

    for i in range(n): #iterate over div-length segmnents of the tree trunk
        for j in range(m): #iterate over the number of timber assortment price classes (row count in puutavaralajimaarittelyt.txt)
            # numpy array indexing: 1st row 2nd element: arr[0, 1]
            # in R it's the same order: arr[2, 3] --> the item on 2nd row and 3rd column
            # but whereas R-indexing is one-based, Python's is zero-based --> indexing has been offset by one
            t = int(i + P[j,2] / div)
            if t < n:
                d_top = T[t,0]
                d_min = P[j, 1]
                
                if d_top >= d_min:
                    v = T[t,2] - T[i,2]
                    c = v * P[j, 3]
                    v_tot = v + V[i]
                    c_tot = c + C[i]

                    if c_tot > C[t]:
                        V[t] = v_tot
                        C[t] = c_tot
                        A[t] = P[j, 0]
                        L[t] = i
                    
    maxi = np.argmax(C)

    nas = np.unique(P[:, 0])

    volumes = np.zeros(len(nas))
    values = np.zeros(len(nas))

    a = l = 1

    while maxi > 0:
        a = int(A[maxi])-1 # a is used as an index for volumes and values. Here in Python, it must be subtracted by one to work with zero-based indexing.
        l = int(L[maxi])
        volumes[a] = volumes[a] + V[maxi] - V[l]
        values[a] = values[a] + C[maxi] - C[l]

        maxi = l

    return (volumes, values)


def _cross_cut(
        species: TreeSpecies,
        breast_height_diameter: float,
        height: float, 
        timber_price_table,
        div = 10
        ) -> tuple[np.ndarray, np.ndarray]:

    species_string = _cross_cut_species_mapper.get(species, "birch") #birch is used as the default species in cross cutting
    
    #the original cross-cut scripts rely on the height being an integer, thus rounding.
    height = round(height)

    n = int((height*100)/div-1)
    T = stem_profile.create_tree_stem_profile(species_string, breast_height_diameter, height, n)
    P = timber_price_table
    m = P.shape[0]

    return apteeraus_Nasberg(T, P, m, n, div)


def cross_cut_thinning_output(thinned_trees: ThinningOutput, stand_area: float, timber_price_table: np.ndarray) -> Tuple[List, List]:
    """
    Calculates the total volume and value of cross cutting the :thinned_trees:. 
    Returns a tuple of (volumes, values) where volumes and values are lists of floats.
    These lists are of size `(m, n)` where
       `m` is the number of unique timber grades (puutavaralaji) and 
        `n` is the count of cut reference trees.
    it's left to the caller to generate aggregates from these.
    """
    volumes_bucket = []
    values_bucket = []

    for thinning_data in thinned_trees.removed:
        volumes, values = _cross_cut(
                            thinning_data.species,
                            thinning_data.breast_height_diameter,
                            thinning_data.height,
                            timber_price_table
                            )

        #NOTE: the above 'volumes' and 'values' are calculated for a single reference tree. 
        # To report absolute (i.e. not in per hectare terms) numbers, they must be multiplied by the reference tree's stems_removed_per_ha and the stand area (in hectares)
        
        multiplier = thinning_data.stems_removed_per_ha * stand_area/1000
        volumes = [vol*multiplier for vol in volumes]
        values = [val*multiplier for val in values]

        volumes_bucket.append(volumes)
        values_bucket.append(values)
    
    return (volumes_bucket, values_bucket)



def cross_cut_stand(stand: ForestStand, timber_price_table: np.ndarray) -> tuple[List[float], List[float]]:
    """
    Calculates the volume and value of cross cutting all the reference trees in the :stand:. 
    Returns a tuple of (volumes, values) where volumes and values are lists of floats.
    These lists are of size `(m, n)` where
       `m` is the number of unique timber grades (puutavaralaji) and 
        `n` is the count of cut reference trees.
    it's left to the caller to generate aggregates from these.
    """
    volumes_bucket = []
    values_bucket = []

    for tree in stand.reference_trees:
        volumes, values = _cross_cut(
                            tree.species, 
                            tree.breast_height_diameter, 
                            tree.height, 
                            timber_price_table
                            )

        #NOTE: the above 'volumes' and 'values' are calculated for a single reference tree. To report meaningful numbers,
        # they must be multiplied by the reference tree's stem count per ha and the stand area (in hectares)
        multiplier = tree.stems_per_ha * stand.area/1000 #area is given in square meters, thus need to convert to ha.
        volumes = [vol*multiplier for vol in volumes] 
        values = [val*multiplier for val in values]

        volumes_bucket.append(volumes)
        values_bucket.append(values)
    
    return (volumes_bucket, values_bucket)

def calculate_cross_cut_aggregates(volumes: List[List[float]], values: List[List[float]]) -> Any:
    total_volume = sum(map(sum, volumes))
    total_value = sum(map(sum, values))

    return (total_volume, total_value)
