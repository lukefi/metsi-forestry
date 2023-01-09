from typing import Callable, Sequence

import lupa
import numpy as np
from lukefi.metsi.data.enums.internal import TreeSpecies

from pathlib import Path

CrossCutFn = Callable[..., tuple[Sequence[int], Sequence[float], Sequence[float]]]


def cross_cut_lupa(P: np.ndarray) -> CrossCutFn:
    """Produce a cross-cut wrapper function intialized with the crosscut.lua script using the Lupa bindings."""
    path = Path(__file__).parent.parent.resolve() / "lua" / "crosscut.lua"

    with open(path, "r") as file:
        script = file.read()

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    fn = lua.execute(script)['aptfunc_lupa']
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
        vol, val = aptfunc(spe, d, round(h))
        return list(map(int, np.unique(P[:, 0]))), list(vol.values()), list(val.values())
    return cc
