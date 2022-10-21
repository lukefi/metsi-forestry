import numpy as np
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions.cross_cutting import stem_profile
from forestryfunctions.cross_cutting.model import (CrossCutResult,
                                                   CrossCutResults,
                                                   CrossCuttableTrees)

_cross_cut_species_mapper = {
    TreeSpecies.PINE: "pine",
    TreeSpecies.SPRUCE: "spruce",
    TreeSpecies.CURLY_BIRCH: "birch",
    TreeSpecies.DOWNY_BIRCH: "birch",
    TreeSpecies.SILVER_BIRCH: "birch"
}


def apteeraus_Nasberg(T: np.ndarray, P: np.ndarray, m: int, n: int, div: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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

    return (nas, volumes, values) #deviating from the R implementation a little bit by also returning `nas`, the list of unique timber grades.


def _cross_cut(
        species: TreeSpecies,
        breast_height_diameter: float,
        height: float, 
        timber_price_table,
        div = 10
        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns a tuple containing unique timber grades and their respective volumes and values."""
    species_string = _cross_cut_species_mapper.get(species, "birch") #birch is used as the default species in cross cutting
    
    #the original cross-cut scripts rely on the height being an integer, thus rounding.
    height = round(height)

    n = int((height*100)/div-1)
    T = stem_profile.create_tree_stem_profile(species_string, breast_height_diameter, height, n)
    P = timber_price_table
    m = P.shape[0]

    return apteeraus_Nasberg(T, P, m, n, div)

def _create_cross_cut_results(stand_area, species, stems_removed_per_ha, unique_timber_grades, volumes, values):
    results = []
    for grade, volume, value in zip(unique_timber_grades, volumes, values):
        results.append(
                CrossCutResult(
                    species=species,
                    timber_grade=int(grade),
                    volume_per_ha=volume*stems_removed_per_ha,
                    value_per_ha=value*stems_removed_per_ha,
                    stand_area=stand_area
                )
            )
    return results

def cross_cut_trees(cross_cuttable_trees: CrossCuttableTrees, stand_area: float, timber_price_table: np.ndarray) -> CrossCutResults:
    """
    :param cross_cuttable_trees: A list of trees that can be cross cut. These can be for example trees that have been thinned, or all the trees of a stand in case of a clear cut.
    :returns: A list of CrossCutResult objects, whose length is given by the number of unique timber grades in the `timber_price_table` times the number of trees in `cross_cuttable_trees`.
    """
    cross_cut_results = []
    for tree in cross_cuttable_trees.trees:
        unique_timber_grades, volumes, values = _cross_cut(
                            tree.species,
                            tree.breast_height_diameter,
                            tree.height,
                            timber_price_table
                            )
        results = _create_cross_cut_results(
                            stand_area, 
                            tree.species, 
                            tree.stems_to_cut_per_ha, 
                            unique_timber_grades, 
                            volumes, 
                            values
                            )
        cross_cut_results.extend(results)

    return cross_cut_results
