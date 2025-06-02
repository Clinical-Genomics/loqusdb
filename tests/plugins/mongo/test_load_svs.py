from loqusdb.build_models.variant import build_variant
from loqusdb.constants import GRCH37, GRCH38


def test_load_insertion(small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = small_insert_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert variant_cluster["families"] == [case_id]


def test_load_same_insertion_twice(small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = small_insert_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)
    formated_variant["case_id"] = "2"
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert set(variant_cluster["families"]) == set([case_id, "2"])


def test_load_translocation(translocation_variant, case_obj, mongo_adapter):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = translocation_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert variant_cluster["families"] == [case_id]


def test_load_same_translocation_twice(translocation_variant, case_obj, mongo_adapter):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = translocation_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)

    formated_variant["case_id"] = "2"
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert set(variant_cluster["families"]) == set([case_id, "2"])


def test_load_insertion_grch38(chr_small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = chr_small_insert_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert variant_cluster["families"] == [case_id]


def test_load_same_insertion_twice_grch38(chr_small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = chr_small_insert_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)
    formated_variant["case_id"] = "2"
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert set(variant_cluster["families"]) == set([case_id, "2"])


def test_load_translocation_grch38(chr_translocation_variant, case_obj, mongo_adapter):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = chr_translocation_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert variant_cluster["families"] == [case_id]


def test_load_same_translocation_twice_grch38(chr_translocation_variant, case_obj, mongo_adapter):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a case
    variant = chr_translocation_variant
    case_id = case_obj["case_id"]
    adapter.add_case(case_obj)

    ## WHEN loading a small insertion
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    adapter.add_structural_variant(formated_variant)

    formated_variant["case_id"] = "2"
    adapter.add_structural_variant(formated_variant)

    ## THEN assert the object returned is correct
    variant_cluster = adapter.db.structural_variant.find_one()

    assert set(variant_cluster["families"]) == set([case_id, "2"])
