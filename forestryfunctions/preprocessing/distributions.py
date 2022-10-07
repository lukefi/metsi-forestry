""" Module contains distribution based model functions
    - weibull distribution
    - simple height distribution
    - weibull height distribution for sapling stratum and diameter models of generated
      sapling trees
"""
import math
from typing import Optional, List, Tuple
from forestdatamodel.model import ReferenceTree, TreeStratum, ForestStand
from forestryfunctions.preprocessing import pre_util
from enum import Enum


# ---- Weibull distribution model ----

def weibull_coeffs(diameter: float, basal_area: float, min_diameter: Optional[float] = None) -> Tuple:
    """ Weight parameter calcualtions for Weibull distribution formula.

    Notice that min_diameter can be used to override the formulation of weight (a).

    :param diameter: Mean diameter
    :param basal_area: Basal area
    :param min_diameter: (optional) Should be a value between [0.0, 4.5]
    :return weight coefficients (a, b, c) used in the Weibull distribution calculation
    """
    w1 = pre_util.get_or_default(min_diameter, math.exp(-1.306454 + (1.154433 * math.log(diameter)) + (math.pow(0.33956, 2) / 2.0)))
    w3 = math.exp(0.64788 - (0.005558 * basal_area) + (0.025530 * diameter) + (math.pow(0.35365,2) / 2.0))
    w2 = (diameter - w1) / (pow((-math.log(0.5)), (1.0 / w3)))
    if w2 < 0.0:
        w2 = 0.0
    return w1, w2, w3


def weibull(n_samples: int, diameter: float, basal_area: float, height: float, min_diameter: Optional[float] = None) -> List[ReferenceTree]:
    """ Computes Stems per hectare and diameter for given number of refernece trees. The values are driven from the Weibull distribution.

    :param n_samples: Number of trees to be created
    :param diameter: Average diameter
    :param basal_area: Basal area
    :param height: Average height
    :param min_diameter: (optional) Minimum diameter used in weight calculation. If given should be a value between [0.0, 4.5]
    :return Given number of trees containing stems per hectare and diameters as object instance members.
    """
    (a, b, c) = weibull_coeffs(diameter, basal_area, min_diameter)

    # x-axis upperlimit
    ax = a + b * math.pow(4.60517, (1.0 / c))

    interval = (ax - a) / float(n_samples)
    if interval < 0.0:
        interval = 1.0

    f1 = 0.0
    xx = a
    result = []
    # For each sample pick-up stems per hectare from Weibull distribution
    for _ in range(1, n_samples + 1):
        xx = xx + interval
        computed_diameter = xx - (interval / 2.0)
        if height < 1.3:
            computed_diameter = 0.0

        f = 1 - math.exp(-math.pow(((xx - a) / b), c))

        if xx >= ax:
            f = 1.0

        p = f - f1 # precentual ratio of stems in sample i
        f1 = f

        stems = (12732.4 * basal_area) / math.pow(computed_diameter, 2.0)
        stems_per_sample = p * stems

        reference_tree = ReferenceTree()
        reference_tree.stems_per_ha = round(stems_per_sample, 2)
        reference_tree.breast_height_diameter = round(computed_diameter, 2)

        result.append(reference_tree)
    return result


# ---- Simple height distribution model ----

# NOTE: debricated only for test purposes
def simple_height_distribution(stratum: TreeStratum, n_trees: int) -> List[ReferenceTree]:
    """ Generate N trees from tree stratum.

    For a single tree, height and diameter are obtained from stratum.
    The stem count for single reference tree is the fraction of stratums total stem count.
    NOTE: that the stem count for all trees is even.
    NOTE: for testing and alternative for sapling weibull distributions
    """
    stems_per_tree = stratum.stems_per_ha / n_trees
    result = []
    for _ in range(n_trees):
        reference_tree = ReferenceTree()
        reference_tree.height = stratum.mean_height
        reference_tree.breast_height_diameter = stratum.mean_diameter
        reference_tree.stems_per_ha = stems_per_tree
        result.append(reference_tree)
    return result

# ---- Weibull height distribution models forand diameter models of sapling trees ----

def reference_trees_from_height_distribution(stratum: TreeStratum, n_trees: Optional[int] = None) -> List[ReferenceTree]:
    Hdom = 0.0
    result = []
    result = WpituusNOtos(stratum.species,stratum.mean_height,stratum.mean_diameter,stratum.stems_per_ha,Hdom,n_trees)
    return result

def WpituusNOtos(pl: float, H: float, D: float, N: float, Hdom: float, n_trees: int) -> List[ReferenceTree]:
    """Formulates height distribution of sapling stratum and predicts the diameters and the number of stems of the simulation trees
    References: Siipilehto, J. 2009, Modelling stand structure in young Scots pine dominated stands.
                Forest Ecology and management 257: 223–232. (GLM model)
    param: pl: tree species
    param: H: mean height
    param: D: mean diameter at breast height
    param: N: stem number
    param: Hdom: Dominant height
    param: n_trees: The number of simulation trees in tree stratum
    return: trees: diameters, heights and stem numbers of the simulation trees
    """

# only one simulation tree:
    if n_trees == 1:
        result = []
        reference_tree = ReferenceTree()
        reference_tree.breast_height_diameter = D
        reference_tree.height = H
        reference_tree.stems_per_ha = N
        result.append(reference_tree)
        return result
# simulation trees more than 1:
    result = Weib_sapling(pl, H, D, N, Hdom, n_trees)
    Hdom=1.05*H
# Sapling diameters are predicted
    for i, reference_tree in enumerate(result):
#    for reference_tree in result:
#        reference_tree = ReferenceTree()
        i=i+1
        if reference_tree.height <= 1.300:
            reference_tree.breast_height_diameter =0.0
        elif (reference_tree.height > 1.3 and H > 1.3 and D > 0.0):
#..FORECO 257.
            lndiJS = 0.3904 + 0.9119 * math.log(reference_tree.height - 1.0) + 0.05318 * reference_tree.height \
            -1.0845 * math.log(H) + 0.9468 * math.log(D+1) - 0.0311 * Hdom
            dvari = 0.000478 + 0.000305 + 0.03199 # for bias correction
            di = math.exp(lndiJS + dvari / 2.)
            reference_tree.breast_height_diameter = di
        elif (reference_tree.height > 1.3 and (H >= 1.3 or D <= 0)):
#       for the youngest sapling stands diameter is predicted directly from height Valkonen (1997)
            lndi = 1.5663 + 0.4559 * math.log(reference_tree.height) + 0.0324 * reference_tree.height
            di = math.exp(lndi + 0.004713 / 2) - 5.0
            reference_tree.breast_height_diameter = di
    return result


def Weib_sapling(pl: float, H: float, D: float, N: float, Hdom: float, n_trees: int) -> List[ReferenceTree]:
    """Formulates weibull height distribution of sapling stratum and the number of stems of the simulation trees
    References: Siipilehto, J. 2009, Modelling stand structure in young Scots pine dominated stands.
                Forest Ecology and management 257: 223–232. (GLM model)
    """

# Mean diameter and dominant height can be illogical:
    if Hdom <= H:
        Hdom = 1.05 * H

    Ph = 0
    Nh = 0

# Weibull parameters Generalized Linear Model (look Cao 2004)
# With GLM model, fitting the distribution to treewise data and
# the solution of parameters of the prediction model are done at the same time
    a = 0.0

    b0 = 0.1942
    b1 = 0.9971
    b2 = -0.0580

    c0 = -2.4203
    c1 = 0.0895
    c2 = -0.0637
    c3 = 0.2510
    c4 = 1.2707

# KHar Error correction: Siipilehto 2009, Forest ecology...  p. 8, formula 6
# Height H pmust be logarithmic.
    b = math.exp(b0 + b1 * math.log(H) + b2 / math.log(Hdom/H + 0.4))
    c = math.exp(c0 + c1 * H + c2 * Hdom + c3 * math.log(N) + c4 / math.log(Hdom / H + 0.4))

# Weibull height distribution is known, trees are picked up from the distribution
    classN = 1 / float(n_trees)    # stem number from class border
    Nh = N / float(n_trees)        # frequency
    classH = classN / 2          # for the class center
    result=[]

    for i in range(n_trees):
        reference_tree = ReferenceTree()
        Ph = float(i+1) * classN - classH         # class center
        hi = b * (-math.log(1.0 - Ph))**(1.0 / c) + a   # picking up height from the cumulative Weibull distribution. Analytical solution.
        reference_tree.height = hi

        reference_tree.stems_per_ha = Nh
        result.append(reference_tree)
    return result

