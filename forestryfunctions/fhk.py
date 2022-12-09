from forestdatamodel.model import ForestStand
import fhk
from forestryfunctions.naturalprocess.grow_motti import spe2motti

def definevars(graph: fhk.Graph):

    #---- global variables ----------------------------------------

    @graph.given("year")
    def year(stand: ForestStand) -> float:
        return stand.year

    #---- site variables ----------------------------------------

    @graph.given("site")
    def group_site() -> fhk.Subset:
        return fhk.interval1(1)

    @graph.given("site#mty")
    def site_mty(stand: ForestStand) -> int:
        return int(stand.site_type_category)

    @graph.given("site#mal")
    def site_mal(stand: ForestStand) -> int:
        return int(stand.land_use_category)

    @graph.given("site#alr")
    def site_alr(stand: ForestStand) -> int:
        return int(stand.soil_peatland_category)

    @graph.given("site#verl")
    def site_verl(stand: ForestStand) -> int:
        return int(stand.tax_class)

    @graph.given("site#verlt")
    def site_verlt(stand: ForestStand) -> int:
        return int(stand.tax_class_reduction)

    @graph.given("site#spedom")
    def site_spedom(stand: ForestStand) -> int:
        return 1 # TODO (see grow_motti)

    @graph.given("site#prt")
    def site_prt(stand: ForestStand) -> int:
        return 1 # TODO (see grow_motti)

    @graph.given("site#Y")
    def site_Y(stand: ForestStand) -> float:
        return stand.geo_location[0]

    @graph.given("site#X")
    def site_X(stand: ForestStand) -> float:
        return stand.geo_location[1]

    @graph.given("site#Z")
    def site_Z(stand: ForestStand) -> float:
        return stand.geo_location[2]

    @graph.given("site#dd")
    def site_dd(stand: ForestStand) -> float:
        return stand.degree_days

    @graph.given("site#sea")
    def site_sea(stand: ForestStand) -> float:
        return stand.sea_effect

    @graph.given("site#lake")
    def site_lake(stand: ForestStand) -> float:
        return stand.lake_effect

    #---- tree variables ----------------------------------------

    @graph.given("tree")
    def group_tree(stand: ForestStand) -> fhk.Subset:
        return fhk.interval1(len(stand.reference_trees))

    @graph.given("tree#->site", ldef="mode 's'")
    def tree2site() -> fhk.Subset:
        return 0

    @graph.given("tree#f")
    def tree_f(stand: ForestStand, idx: int) -> float:
        return stand.reference_trees[idx].stems_per_ha

    @graph.given("tree#spe")
    def tree_spe(stand: ForestStand, idx: int) -> int:
        return spe2motti(stand.reference_trees[idx].species)

    @graph.given("tree#d")
    def tree_d(stand: ForestStand, idx: int) -> float:
        return stand.reference_trees[idx].breast_height_diameter

    @graph.given("tree#h")
    def tree_h(stand: ForestStand, idx: int) -> float:
        return stand.reference_trees[idx].height

    @graph.given("tree#storie")
    def tree_storie(stand: ForestStand, idx: int) -> int:
        return 0 # TODO

    @graph.given("tree#snt")
    def tree_snt(stand: ForestStand, idx: int) -> int:
        return (stand.reference_trees[idx].origin or 0) + 1

    @graph.given("tree#t0")
    def tree_t0(stand: ForestStand, idx: int) -> float:
        return stand.year - stand.reference_trees[idx].biological_age

    @graph.given("tree#t13")
    def tree_t13(stand: ForestStand, idx: int) -> float:
        return stand.year - stand.reference_trees[idx].breast_height_age
