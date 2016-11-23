from loqusdb.utils import (load_database, delete)

def test_delete_case_and_variants(vcf_path, ped_path, mongo_adapter, case_id):
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter, 
        variant_file=vcf_path, 
        family_file=ped_path, 
        family_type='ped', 
    )

    mongo_case = db.case.find_one()

    assert mongo_case['case_id'] == case_id

    delete(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type='ped',
    )

    mongo_case = db.case.find_one()
    
    assert mongo_case == None
    
    mongo_variant = db.case.find_one()
    
    assert mongo_variant == None
    
