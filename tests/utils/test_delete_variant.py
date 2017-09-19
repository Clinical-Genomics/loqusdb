from loqusdb.utils import (delete_variants, load_variants)


def test_delete_variants(mongo_adapter, het_variant, case_obj, ind_positions):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(het_variant)
    
    family_id = case_obj.family_id
    individuals = case_obj.individuals
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals,
        ind_positions=ind_positions,
        vcf=vcf,
        gq_treshold=20,
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == [family_id]

    delete_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        ind_positions=ind_positions,
        individuals=individuals, 
        vcf=vcf
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant == None

def test_delete_variant(mongo_adapter, het_variant, case_obj, ind_positions):
    """docstring for test_load_variants"""
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    family_id_1 = case_obj.family_id
    individuals = case_obj.individuals

    load_variants(
        adapter=mongo_adapter,
        family_id=family_id_1,
        individuals=individuals,
        ind_positions=ind_positions,
        vcf=vcf,
        gq_treshold=20,
    )

    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == [family_id_1]

    family_id_2 = '2'

    load_variants(
        adapter=mongo_adapter,
        family_id=family_id_2,
        individuals=individuals,
        ind_positions=ind_positions,
        vcf=vcf,
        gq_treshold=20,
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant['families'] == [family_id_1, family_id_2]
    assert mongo_variant['observations'] == 2

    delete_variants(
        adapter=mongo_adapter,
        family_id=family_id_2,
        ind_positions=ind_positions,
        individuals=individuals,
        vcf=vcf
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant['families'] == [family_id_1]
    assert mongo_variant['observations'] == 1

def test_delete_non_existing_variant(mongo_adapter, het_variant, case_obj, ind_positions):
    """docstring for test_load_variants"""
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    family_id = case_obj.family_id
    individuals = case_obj.individuals

    delete_variants(
        adapter=mongo_adapter,
        family_id=family_id,
        individuals=individuals,
        ind_positions=ind_positions,
        vcf=vcf
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant == None
