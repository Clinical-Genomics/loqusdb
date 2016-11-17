from loqusdb.utils import (delete_variants, load_variants)


def test_delete_variants(mongo_adapter, het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(het_variant)
    
    family_id = '1'
    individuals=['proband']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == ['1']

    delete_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant == None

def test_delete_variant(mongo_adapter, het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(het_variant)
    
    family_id = '1'
    individuals=['proband']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
    )

    family_id = '2'
    individuals=['proband']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == ['1', '2']
    assert mongo_variant['observations'] == 2

    delete_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant['families'] == ['1']
    assert mongo_variant['observations'] == 1

def test_delete_non_existing_variant(mongo_adapter, het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(het_variant)
    family_id = '1'
    individuals=['proband']
    
    delete_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant == None
