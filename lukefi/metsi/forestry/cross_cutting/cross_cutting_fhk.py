from dataclasses import dataclass, field, fields, make_dataclass
from json import dumps
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence
from lukefi.metsi.data.model import TreeSpecies
import fhk
import numpy as np

CrossCutFn = Callable[..., tuple[Sequence[int], Sequence[float], Sequence[float]]]


@dataclass
class Args:
    spe: TreeSpecies
    d: float
    h: float


def ltab(xs: Iterable[float]) -> str:
    return f"{{ {', '.join(map(str, xs))} }}"


# operator.attrgetter but inspectable
def attrgetter(attr: str) -> Callable:
    return lambda o: getattr(o, attr)


def definevars(graph: fhk.Graph):
    for field in fields(Args):
        graph.add_given(field.name, attrgetter(field.name))


def defineapt(graph: fhk.Graph, P: np.ndarray, retnames: Iterable[str], div: float = 10):
    nas = np.unique(P[:,0])
    path = dumps(str(Path(__file__).parent.parent.resolve() / "lua" / "?.lua"))
    rv = " ".join(retnames)
    graph.ldef(f"""
        package.path = package.path..";"..{path}
        model () {{
            params "spe d h",
            returns "{rv}",
            impl.Lua {{
                "crosscut",
                load = function(pkg)
                    return pkg.aptfunc_fhk(
                        {ltab(P[:,0])},
                        {ltab(P[:,1])},
                        {ltab(P[:,2])},
                        {ltab(P[:,3])},
                        {P.shape[0]},
                        {div},
                        {len(nas)}
                    )
                end
            }}
        }}
    """)


def queryclass(retnames: Iterable[str]) -> type:
    return make_dataclass(
        "Query",
        [(name, float, field(default=fhk.root(name))) for name in retnames]
    )


def cross_cut_fhk(P: np.ndarray) -> CrossCutFn:
    """Produce a cross-cut wrapper function intialized with the crosscut.lua script in the FHK graph solver."""
    nas = list(map(int, np.unique(P[:, 0])))
    retnames = []
    for v in nas:
        retnames.append(f"val{v}")
        retnames.append(f"vol{v}")
    with fhk.Graph() as g:
        definevars(g)
        defineapt(g, P, retnames)
        query = g.query(queryclass(retnames))

    def cc(
        spe: TreeSpecies,
        d: float,
        h: float,
        mem: Optional[fhk.Mem] = None
    ) -> tuple[Sequence[int], Sequence[float], Sequence[float]]:
        r = query(Args(spe=spe, d=d, h=round(h)), mem=mem)
        vol, val = [], []
        for i in range(0, len(retnames), 2):
            vol.append(getattr(r, retnames[i]))
            val.append(getattr(r, retnames[i+1]))
        return nas, vol, val # type: ignore
    return cc
