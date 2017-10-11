from loqusdb.utils.delete import delete_variants
from loqusdb.utils.load import load_variants
from loqusdb.build_models.variant import get_variant_id


def test_delete_variants(mongo_adapter, het_variant, case_obj, ind_positions):
    ## GIVEN a database with one variant
    db = mongo_adapter.db
    case_id = case_obj.family_id
    individuals = case_obj.individuals
    
    db.variant.insert_one({
        '_id': get_variant_id(het_variant),
        'families': [case_id],
        'observations': 1,
    })
    
    mongo_variant = db.variant.find_one()
    assert mongo_variant['families'] == [case_id]

    ## WHEN deleting the variant
    delete_variants(
        adapter=mongo_adapter,
        case_id=case_id,
        ind_positions=ind_positions,
        individuals=individuals, 
        vcf_obj=[het_variant]
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant was not found
    assert mongo_variant == None

def test_delete_variant(mongo_adapter, het_variant, case_obj, ind_positions):
    ## GIVEN a database with one variant that is observed twice
    db = mongo_adapter.db
    case_id = case_obj.family_id
    individuals = case_obj.individuals
    
    db.variant.insert_one({
        '_id': get_variant_id(het_variant),
        'families': [case_id, '2'],
        'observations': 2,
    })

    mongo_variant = db.variant.find_one()
    assert mongo_variant['observations'] == 2

    ## WHEN deleting the variant for one case
    delete_variants(
        adapter=mongo_adapter,
        case_id='2',
        ind_positions=ind_positions,
        individuals=individuals,
        vcf_obj=[het_variant]
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that one case has been removed from 'families'
    assert mongo_variant['families'] == [case_id]
    ## THEN assert that the observation count is decreased
    assert mongo_variant['observations'] == 1

def test_delete_non_existing_variant(mongo_adapter, het_variant, case_obj, ind_positions):
    """docstring for test_load_variants"""
    ## GIVEN a mongo adapter to an empty database
    db = mongo_adapter.db

    case_id = case_obj.family_id
    individuals = case_obj.individuals

    ## WHEN deleting the variants
    delete_variants(
        adapter=mongo_adapter,
        case_id=case_id,
        individuals=individuals,
        ind_positions=ind_positions,
        vcf_obj=[het_variant]
    )

    # THEN assert nothing happens
    mongo_variant = db.variant.find_one()

    assert mongo_variant == None
