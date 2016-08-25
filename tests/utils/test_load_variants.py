import pytest
from loqusdb.utils import load_variants

def test_load_variants(mongo_adapter, cyvcf2_het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(cyvcf2_het_variant)
    
    family_id = '1'
    individuals=['proband']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        bulk_insert=False
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == ['1']

def test_load_two_variants(mongo_adapter, cyvcf2_het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(cyvcf2_het_variant)
    vcf.append(cyvcf2_het_variant)
    
    family_id = '1'
    individuals=['proband']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        bulk_insert=False
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['observations'] == 2

def test_load_same_variant_different_case(mongo_adapter, cyvcf2_het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(cyvcf2_het_variant)
    
    family_id = '1'
    individuals=['proband', 'mother', 'father']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        bulk_insert=False
    )

    family_id = '2'
    individuals=['proband', 'mother', 'father']
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        bulk_insert=False
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['observations'] == 2
    assert mongo_variant['families'] == ['1', '2']

# def test_load_same_variant_many_cases(real_mongo_adapter, cyvcf2_het_variant):
#     """docstring for test_load_variants"""
#     db = real_mongo_adapter.db
#
#     vcf = []
#     vcf.append(cyvcf2_het_variant)
#     individuals=['proband', 'mother', 'father']
#
#     for i in range(40):
#         family_id = str(i)
#
#         load_variants(
#             adapter=real_mongo_adapter,
#             family_id=family_id,
#             individuals=individuals,
#             vcf=vcf,
#             bulk_insert=False
#             )
#
#     mongo_variant = db.variant.find_one()
#
#     assert mongo_variant['observations'] == 40
#     assert len(mongo_variant['families']) == 20