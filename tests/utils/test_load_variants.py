import pytest
from loqusdb.utils.load import load_variants

def test_load_variants(mongo_adapter, het_variant, case_obj):
    ## GIVEN an adapter and a vcf with one heterozygote variant
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(het_variant)
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant == None
    
    ## WHEN loading the variant into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj,
    )
    
    mongo_variant = db.variant.find_one()
    
    ## THEN assert that the variant is loaded correct
    assert mongo_variant['families'] == [case_obj['case_id']]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 0
    assert mongo_variant['hemizygote'] == 0

def test_load_homozygote(mongo_adapter, hom_variant, case_obj):
    ## GIVEN an adapter and a vcf with one homozygote variant
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(hom_variant)
    assert db.variant.find_one() == None
    
    ## WHEN loading the variant into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj, 
    )
    mongo_variant = db.variant.find_one()
    
    ## THEN assert that the variant is loaded correct
    assert mongo_variant['families'] == [case_obj['case_id']]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 1
    assert mongo_variant['hemizygote'] == 0

def test_load_hemizygote(mongo_adapter, hem_variant, case_obj):
    ## GIVEN an adapter and a vcf with one hemizygote variant
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(hem_variant)

    assert db.variant.find_one() == None
    
    ## WHEN loading the variant into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj, 
    )
    mongo_variant = db.variant.find_one()
    
    ## THEN assert that the variant is loaded correct
    assert mongo_variant['families'] == [case_obj['case_id']]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 0
    assert mongo_variant['hemizygote'] == 1

def test_load_par_variant(mongo_adapter, par_variant, case_obj):
    ## GIVEN an adapter and a vcf with one PAR variant
    db = mongo_adapter.db
    
    vcf = []
    vcf.append(par_variant)

    assert db.variant.find_one() == None
    
    ## WHEN loading the variant into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj, 
    )
    mongo_variant = db.variant.find_one()
    
    ## THEN assert that the variant is loaded correct
    assert mongo_variant['families'] == [case_obj['case_id']]
    assert mongo_variant['observations'] == 1
    assert mongo_variant['homozygote'] == 0
    assert mongo_variant['hemizygote'] == 0

def test_load_two_variants(mongo_adapter, het_variant, case_obj):
    ## GIVEN an adapter and a vcf with tho heterygote variants
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    vcf.append(het_variant)

    ## WHEN loading the variants into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj, 
    )

    ## THEN assert that the variant is loaded correct
    mongo_variant = db.variant.find_one()

    assert mongo_variant['observations'] == 2

def test_load_variants_skip_case_id(mongo_adapter, het_variant, case_obj):
    ## GIVEN an adapter and a vcf with tho heterygote variants
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    ## WHEN loading the variants into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj,
        skip_case_id=True,
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant.get('families') == None

def test_load_same_variant_different_case(mongo_adapter, het_variant, case_obj):
    ## GIVEN an adapter and a vcf
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    ## WHEN loading the variant into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj,
    )

    case_id = case_obj['case_id']
    case_id2 = '2'
    case_obj['case_id'] = case_id2

    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf, 
        case_obj=case_obj,
    )

    mongo_variant = db.variant.find_one()

    assert mongo_variant['observations'] == 2
    assert mongo_variant['families'] == [case_id, case_id2]

