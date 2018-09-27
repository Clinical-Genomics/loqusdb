from pprint import pprint as pp

import pytest

from loqusdb.utils.load import load_database
from loqusdb.exceptions import CaseError

def test_load_database(vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db
    ## GIVEN a vcf, ped and adapter

    ## WHEN loading the case and its variants
    nr_loaded = load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type='ped',
    )

    mongo_case = db.case.find_one()

    ## THEN assert the case was loaded
    assert mongo_case['case_id'] == case_id
    ## THEN assert the number of loaded variants is correct
    assert nr_loaded == mongo_case['nr_variants']



def test_load_database_alternative_ped(vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type='ped',
        case_id='alternative'
    )

    mongo_case = db.case.find_one()
    mongo_variant = db.variant.find_one()

    assert mongo_case['case_id'] == 'alternative'
    assert mongo_variant['families'] == ['alternative']

def test_load_database_wrong_ped(vcf_path, funny_ped_path, mongo_adapter):
    ## GIVEN a vcf and ped file with wrong individuals
    ## WHEN loading the information
    ## THEN Error should be raised since individuals is not in vcf
    with pytest.raises(CaseError):
        load_database(
            adapter=mongo_adapter,
            variant_file=vcf_path,
            family_file=funny_ped_path,
            family_type='ped',
        )

def test_load_sv_case_database(sv_vcf_path, ped_path, mongo_adapter, case_id):
    db = mongo_adapter.db
    ## GIVEN a vcf, ped and adapter

    ## WHEN loading the case and its variants
    nr_loaded = load_database(
        adapter=mongo_adapter,
        sv_file=sv_vcf_path,
        family_file=ped_path,
        family_type='ped',
    )

    mongo_case = db.case.find_one()

    ## THEN assert the case was loaded
    assert mongo_case['case_id'] == case_id
    ## THEN assert the number of loaded variants is correct
    assert nr_loaded == mongo_case['nr_sv_variants']

def test_load_complete_case_database(sv_vcf_path, vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db
    ## GIVEN a vcf, svvcf, ped and adapter

    ## WHEN loading the case and its variants
    nr_loaded = load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        sv_file=sv_vcf_path,
        family_file=ped_path,
        family_type='ped',
    )

    mongo_case = db.case.find_one()

    ## THEN assert the case was loaded
    assert mongo_case['case_id'] == case_id
    ## THEN assert the number of loaded variants is correct
    assert nr_loaded == mongo_case['nr_sv_variants'] + mongo_case['nr_variants']

    ## THEN assert both svs and snvs where loaded
    for i,variant in enumerate(db.variant.find()):
        pass
    assert i > 0
    for j,variant in enumerate(db.structural_variant.find()):
        pass

    assert j > 0
