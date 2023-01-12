from functools import cache
from typing import Callable, Sequence

import lupa
from lukefi.metsi.data.enums.internal import TreeSpecies

from pathlib import Path

CrossCutFn = Callable[..., tuple[Sequence[int], Sequence[float], Sequence[float]]]


@cache
def cross_cut_lupa(constants, div=10):
    """Produce a cross-cut wrapper function intialized with the crosscut.lua script using the Lupa bindings."""
    path = Path(__file__).parent.parent.resolve() / "lua" / "crosscut.lua"

    with open(path, "r") as file:
        script = file.read()

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    fn = lua.execute(script)['aptfunc_lupa']
    pcls = lua.table_from(constants[0])
    ptop = lua.table_from(constants[1])
    plen = lua.table_from(constants[2])
    pval = lua.table_from(constants[3])
    aptfunc = fn(pcls, ptop, plen, pval, len(constants[0]), div, len(set(constants[0])))

    def cc(
            spe: TreeSpecies,
            d: float,
            h: float
    ):
        vol, val = aptfunc(spe, d, round(h))
        return list(set(constants[0])), list(vol.values()), list(val.values())
    return cc
