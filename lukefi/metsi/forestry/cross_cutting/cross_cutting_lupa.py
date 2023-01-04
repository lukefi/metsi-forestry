from typing import Callable, Sequence

import lupa
import numpy as np
from lukefi.metsi.data.enums.internal import TreeSpecies

from lukefi.metsi.forestry.cross_cutting.cross_cutting import ZERO_DIAMETER_TREE_TIMBER_GRADE, ZERO_DIAMETER_TREE_VOLUME, \
    ZERO_DIAMETER_TREE_VALUE
from pathlib import Path

CrossCutFn = Callable[..., tuple[Sequence[int], Sequence[float], Sequence[float]]]

def cross_cut_lupa(P: np.ndarray) -> CrossCutFn:
    path = Path(__file__).parent.parent.resolve() / "lua" / "crosscut.lua"

    with open(path, "r") as file:
        script = file.read()

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    fn = lua.execute(script)['aptfunc']
    pcls = lua.table_from(P[:, 0])
    ptop = lua.table_from(P[:, 1])
    plen = lua.table_from(P[:, 2])
    pval = lua.table_from(P[:, 3])
    m = P.shape[0]
    div = 10
    nas = np.unique(P[:, 0])

    aptfunc = fn(pcls, ptop, plen, pval, m, div, len(nas))

    def cc(
            spe: TreeSpecies,
            d: float,
            h: float
    ):
        if d is not None and d < 0:
            raise ValueError("breast_height_diameter must be a non-negative number")
        if d in (None, 0):
            return (np.array([ZERO_DIAMETER_TREE_TIMBER_GRADE]), np.array([ZERO_DIAMETER_TREE_VOLUME]), np.array([ZERO_DIAMETER_TREE_VALUE]))
        result = aptfunc(spe, d, h)
        vol, val = [], []
        for i in range(0, len(nas)*2, 2):
            vol.append(result[i])
            val.append(result[i+1])
        return list(map(int, np.unique(P[:, 0]))), vol, val
    return cc