from loqusdb.build_models.variant import build_mei_variant
from loqusdb.constants import MEI_COLLECTION, SV_COLLECTION


def _add(adapter, factory, case_id, mei_window=150, **kwargs):
    variant = build_mei_variant(factory(**kwargs), case_id=case_id)
    adapter.add_mei_variant(variant, mei_window=mei_window)
    return variant


def test_add_mei_variant(mongo_adapter, mei_variant_factory):
    ## GIVEN an empty database
    ## WHEN adding a MEI
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    ## THEN it is stored in the mei collection only, as a cluster around the insertion
    assert mongo_adapter.db[SV_COLLECTION].count_documents({}) == 0
    cluster = mongo_adapter.db[MEI_COLLECTION].find_one()
    assert cluster["sv_type"] == "INS:ME:ALU"
    assert cluster["observations"] == 1
    assert cluster["families"] == ["case_1"]
    assert (cluster["pos_left"], cluster["pos_right"]) == (850, 1150)
    assert cluster["window"] == 150


def test_add_mei_same_element_within_window(mongo_adapter, mei_variant_factory):
    ## GIVEN a MEI in the database
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    ## WHEN adding the same element from another case, with an imprecise breakpoint
    _add(mongo_adapter, mei_variant_factory, "case_2", pos=1100)
    ## THEN they are merged into one cluster, recentred on the mean
    clusters = list(mongo_adapter.db[MEI_COLLECTION].find())
    assert len(clusters) == 1
    assert clusters[0]["observations"] == 2
    assert (clusters[0]["pos_left"], clusters[0]["pos_right"]) == (900, 1200)


def test_add_mei_other_element_same_position(mongo_adapter, mei_variant_factory):
    ## GIVEN an ALU insertion
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000, element="ALU")
    ## WHEN adding an L1 insertion at the same position
    _add(mongo_adapter, mei_variant_factory, "case_2", pos=1000, element="L1")
    ## THEN they are counted separately
    assert mongo_adapter.db[MEI_COLLECTION].count_documents({}) == 2
    assert set(mongo_adapter.get_mei_types()) == {"INS:ME:ALU", "INS:ME:L1"}


def test_add_mei_outside_window(mongo_adapter, mei_variant_factory):
    ## GIVEN a MEI
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    ## WHEN adding the same element further away than the window
    _add(mongo_adapter, mei_variant_factory, "case_2", pos=1151)
    ## THEN they are separate clusters
    assert mongo_adapter.db[MEI_COLLECTION].count_documents({}) == 2


def test_add_mei_same_case_twice(mongo_adapter, mei_variant_factory):
    ## GIVEN a MEI from a case
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    ## WHEN the same case reports a nearby insertion of the same element
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1010)
    ## THEN the case is only counted once
    cluster = mongo_adapter.db[MEI_COLLECTION].find_one()
    assert cluster["observations"] == 1


def test_mei_window_is_kept_for_the_cluster(mongo_adapter, mei_variant_factory):
    ## GIVEN a MEI cluster created with a large window
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000, mei_window=500)
    ## WHEN adding a second observation with the default window
    _add(mongo_adapter, mei_variant_factory, "case_2", pos=1400, mei_window=150)
    ## THEN the cluster keeps its original window
    cluster = mongo_adapter.db[MEI_COLLECTION].find_one()
    assert cluster["observations"] == 2
    assert cluster["pos_right"] - cluster["pos_left"] == 1000


def test_delete_mei_variant(mongo_adapter, mei_variant_factory):
    ## GIVEN a MEI observed in two cases
    first = _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    second = _add(mongo_adapter, mei_variant_factory, "case_2", pos=1100)
    ## WHEN deleting one observation
    mongo_adapter.delete_mei_variant(second)
    ## THEN the cluster is recentred on the remaining observation
    cluster = mongo_adapter.db[MEI_COLLECTION].find_one()
    assert cluster["observations"] == 1
    assert cluster["families"] == ["case_1"]
    assert (cluster["pos_left"], cluster["pos_right"]) == (850, 1150)
    ## WHEN deleting the last observation
    mongo_adapter.delete_mei_variant(first)
    ## THEN the cluster is removed
    assert mongo_adapter.db[MEI_COLLECTION].count_documents({}) == 0


def test_get_mei_variant(mongo_adapter, mei_variant_factory):
    ## GIVEN a MEI in the database
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    query = {"chrom": "1", "end_chrom": "1", "pos": 1100, "end": 1100, "sv_type": "INS:ME:ALU"}
    ## THEN a query within the window finds it
    assert mongo_adapter.get_mei_variant(query)["observations"] == 1
    ## THEN a query for another element does not
    assert mongo_adapter.get_mei_variant({**query, "sv_type": "INS:ME:L1"}) is None


def test_get_mei_variants_region(mongo_adapter, mei_variant_factory):
    ## GIVEN MEIs on two chromosomes
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=1000)
    _add(mongo_adapter, mei_variant_factory, "case_1", pos=50000)
    _add(mongo_adapter, mei_variant_factory, "case_1", chrom="2", pos=1000)
    ## THEN they can be listed by chromosome and region
    assert len(list(mongo_adapter.get_mei_variants())) == 3
    assert len(list(mongo_adapter.get_mei_variants(chromosome="1"))) == 2
    assert len(list(mongo_adapter.get_mei_variants(chromosome="1", pos=1, end=2000))) == 1
