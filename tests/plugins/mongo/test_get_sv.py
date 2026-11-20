from loqusdb.build_models.variant import build_variant
from loqusdb.constants import GRCH37, GRCH38


def test_get_insertion(small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a small insertion
    variant = small_insert_variant
    case_id = case_obj["case_id"]
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )

    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)
    for variant_obj in adapter.db.structural_variant.find():
        assert variant_obj


def test_get_translocation(translocation_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a translocation
    variant = translocation_variant
    case_id = case_obj["case_id"]
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )

    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)
    for variant_obj in adapter.db.structural_variant.find():
        assert variant_obj


def test_get_insertion_grch38(chr_small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a small insertion
    variant = chr_small_insert_variant
    case_id = case_obj["case_id"]
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH38
    )

    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)
    for variant_obj in adapter.db.structural_variant.find():
        assert variant_obj


def test_get_translocation_grch38(chr_translocation_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a translocation
    variant = chr_translocation_variant
    case_id = case_obj["case_id"]
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH38
    )

    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)
    for variant_obj in adapter.db.structural_variant.find():
        assert variant_obj


def test_get_sv_variants_max_observations(small_insert_variant, mongo_adapter, case_obj):
    """Structural variants observed in >= max_observations individuals are excluded"""
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a structural variant observed once
    case_id = case_obj["case_id"]
    formated_variant = build_variant(
        variant=small_insert_variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)

    ## WHEN querying with max_observations equal to the observation count
    ## THEN the variant is excluded
    assert list(adapter.get_sv_variants(max_observations=1)) == []

    ## WHEN querying with max_observations above the observation count
    ## THEN the variant is returned
    assert len(list(adapter.get_sv_variants(max_observations=2))) == 1
