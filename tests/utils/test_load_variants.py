import pytest
from loqusdb.utils import load_variants

def test_load_variants(mongo_adapter, cyvcf2_het_variant):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = [cyvcf2_het_variant]
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