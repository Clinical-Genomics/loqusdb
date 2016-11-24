import pytest
from loqusdb.utils import load_variants

def test_load_variants(mongo_adapter, het_variant, case_obj):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(het_variant)
    
    family_id = case_obj.family_id
    individuals = case_obj.individuals

    mongo_variant = db.variant.find_one()
    
    assert mongo_variant == None
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        gq_treshold=20,
    )
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == [family_id]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 0
    assert mongo_variant['hemizygote'] == 0

def test_load_homozygote(mongo_adapter, hom_variant, case_obj):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(hom_variant)
    
    family_id = case_obj.family_id
    individuals = case_obj.individuals

    mongo_variant = db.variant.find_one()
    
    assert mongo_variant == None
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        gq_treshold=20,
    )
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == [family_id]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 1
    assert mongo_variant['hemizygote'] == 0

def test_load_hemozygote(mongo_adapter, hem_variant, case_obj):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(hem_variant)
    
    family_id = case_obj.family_id
    individuals = case_obj.individuals

    mongo_variant = db.variant.find_one()
    
    assert mongo_variant == None
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        gq_treshold=20,
    )
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == [family_id]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 0
    assert mongo_variant['hemizygote'] == 1

def test_load_par_variant(mongo_adapter, par_variant, case_obj):
    """docstring for test_load_variants"""
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(par_variant)
    
    family_id = case_obj.family_id
    individuals = case_obj.individuals

    mongo_variant = db.variant.find_one()
    
    assert mongo_variant == None
    
    load_variants(
        adapter=mongo_adapter,
        family_id=family_id, 
        individuals=individuals, 
        vcf=vcf, 
        gq_treshold=20,
    )
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['families'] == [family_id]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 0
    assert mongo_variant['hemizygote'] == 0

def test_load_two_variants(mongo_adapter, het_variant, case_obj):
    """docstring for test_load_variants"""
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    vcf.append(het_variant)

    family_id = case_obj.family_id
    individuals = case_obj.individuals

    load_variants(
        adapter=mongo_adapter,
        family_id=family_id,
        individuals=individuals,
        vcf=vcf,
        gq_treshold=20,
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant['observations'] == 2

def test_load_variants_skip_case_id(mongo_adapter, het_variant, case_obj):
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
        vcf=vcf,
        skip_case_id=True,
        gq_treshold=20,
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant.get('families') == None

def test_load_same_variant_different_case(mongo_adapter, het_variant, case_obj):
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
        vcf=vcf,
    )

    family_id_2 = '2'
    individuals = case_obj.individuals

    load_variants(
        adapter=mongo_adapter,
        family_id=family_id_2,
        individuals=individuals,
        vcf=vcf,
        gq_treshold=20,
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant['observations'] == 2
    assert mongo_variant['families'] == [family_id, family_id_2]

# # This test works when using a real mongo adapter but not with mongomock yet...
# # def test_load_same_variant_many_cases(real_mongo_adapter, family_variant):
# #     """docstring for test_load_variants"""
# #     db = real_mongo_adapter.db
# #
# #     vcf = []
# #     vcf.append(family_variant)
# #     individuals=['proband', 'mother', 'father']
# #
# #     for i in range(40):
# #         family_id = str(i)
# #
# #         load_variants(
# #             adapter=real_mongo_adapter,
# #             family_id=family_id,
# #             individuals=individuals,
# #             vcf=vcf,
# #             )
# #
# #     mongo_variant = db.variant.find_one()
# #
# #     assert mongo_variant['observations'] == 40
# #     assert len(mongo_variant['families']) == 20