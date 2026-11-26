import pytest

from loqusdb.build_models.variant import get_variant_id
from loqusdb.utils.delete import delete_variants
from loqusdb.utils.load import load_variants
from loqusdb.constants import GRCH37, GRCH38


@pytest.mark.parametrize("has_qualifying_het", [False, True])
def test_delete_replays_load_gq_threshold(
    real_mongo_adapter, het_variant, case_obj, has_qualifying_het
):
    adapter = real_mongo_adapter
    other_case = {**case_obj, "case_id": "retained_case"}
    settings = {"gq_threshold": 20, "genome_build": GRCH37}
    assert load_variants(adapter, [het_variant], other_case, **settings) == 1

    het_variant.gt_types = [1, 3, 0]
    het_variant.gt_quals = [60 if has_qualifying_het else 10, 10, 60]
    assert load_variants(adapter, [het_variant], case_obj, **settings) == int(has_qualifying_het)

    delete_variants(adapter, [het_variant], case_obj, **settings)

    variant = adapter.get_variant({"_id": get_variant_id(het_variant)})
    assert variant is not None
    assert variant["observations"] == 1
    assert variant["homozygote"] == 0
    assert variant["families"] == [other_case["case_id"]]


def test_delete_variants(real_mongo_adapter, het_variant, case_obj):
    ## GIVEN a database with one variant
    db = real_mongo_adapter.db
    case_id = case_obj["case_id"]

    db.variant.insert_one(
        {
            "_id": get_variant_id(het_variant),
            "families": [case_id],
            "observations": 1,
        }
    )

    mongo_variant = db.variant.find_one()
    assert mongo_variant["families"] == [case_id]

    ## WHEN deleting the variant
    delete_variants(
        adapter=real_mongo_adapter, vcf_obj=[het_variant], case_obj=case_obj, genome_build=GRCH37
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant was not found
    assert mongo_variant is None


def test_delete_variant(real_mongo_adapter, het_variant, case_obj):
    ## GIVEN a database with one variant that is observed twice
    db = real_mongo_adapter.db
    case_id = case_obj["case_id"]

    db.variant.insert_one(
        {
            "_id": get_variant_id(het_variant),
            "families": [case_id, "2"],
            "observations": 2,
        }
    )

    mongo_variant = db.variant.find_one()
    assert mongo_variant["observations"] == 2

    ## WHEN deleting the variant for one case
    delete_variants(
        adapter=real_mongo_adapter,
        vcf_obj=[het_variant],
        case_obj=case_obj,
        case_id="2",
        genome_build=GRCH37,
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that one case has been removed from 'families'
    assert mongo_variant["families"] == [case_id]
    ## THEN assert that the observation count is decreased
    assert mongo_variant["observations"] == 1


def test_delete_non_existing_variant(mongo_adapter, het_variant, case_obj):
    """docstring for test_load_variants"""
    ## GIVEN a mongo adapter to an empty database
    db = mongo_adapter.db
    case_obj["case_id"]

    ## WHEN deleting the variants
    delete_variants(
        adapter=mongo_adapter, vcf_obj=[het_variant], case_obj=case_obj, genome_build=GRCH37
    )

    # THEN assert nothing happens
    mongo_variant = db.variant.find_one()

    assert mongo_variant is None


def test_delete_variants_grch38(real_mongo_adapter, het_variant, case_obj):
    ## GIVEN a database with one variant
    db = real_mongo_adapter.db
    case_id = case_obj["case_id"]

    db.variant.insert_one(
        {
            "_id": get_variant_id(het_variant),
            "families": [case_id],
            "observations": 1,
        }
    )

    mongo_variant = db.variant.find_one()
    assert mongo_variant["families"] == [case_id]

    ## WHEN deleting the variant
    delete_variants(
        adapter=real_mongo_adapter, vcf_obj=[het_variant], case_obj=case_obj, genome_build=GRCH38
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant was not found
    assert mongo_variant is None


def test_delete_variant_grch38(real_mongo_adapter, het_variant, case_obj):
    ## GIVEN a database with one variant that is observed twice
    db = real_mongo_adapter.db
    case_id = case_obj["case_id"]

    db.variant.insert_one(
        {
            "_id": get_variant_id(het_variant),
            "families": [case_id, "2"],
            "observations": 2,
        }
    )

    mongo_variant = db.variant.find_one()
    assert mongo_variant["observations"] == 2

    ## WHEN deleting the variant for one case
    delete_variants(
        adapter=real_mongo_adapter,
        vcf_obj=[het_variant],
        case_obj=case_obj,
        case_id="2",
        genome_build=GRCH38,
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that one case has been removed from 'families'
    assert mongo_variant["families"] == [case_id]
    ## THEN assert that the observation count is decreased
    assert mongo_variant["observations"] == 1


def test_delete_non_existing_variant_grch38(mongo_adapter, het_variant, case_obj):
    """docstring for test_load_variants"""
    ## GIVEN a mongo adapter to an empty database
    db = mongo_adapter.db
    case_obj["case_id"]

    ## WHEN deleting the variants
    delete_variants(
        adapter=mongo_adapter, vcf_obj=[het_variant], case_obj=case_obj, genome_build=GRCH38
    )

    # THEN assert nothing happens
    mongo_variant = db.variant.find_one()

    assert mongo_variant is None
