from loqusdb.build_models.variant import get_variant_id
from loqusdb.utils.delete import delete_variants


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
    delete_variants(adapter=real_mongo_adapter, vcf_obj=[het_variant], case_obj=case_obj)

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
    case_id = case_obj["case_id"]

    ## WHEN deleting the variants
    delete_variants(adapter=mongo_adapter, vcf_obj=[het_variant], case_obj=case_obj)

    # THEN assert nothing happens
    mongo_variant = db.variant.find_one()

    assert mongo_variant == None
