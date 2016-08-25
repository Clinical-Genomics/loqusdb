import pytest
from loqusdb.utils import (delete_family, load_family)
from loqusdb.exceptions import CaseError

def test_delete_family(mongo_adapter):
    db = mongo_adapter.db
    
    case = {
        'case_id': '1',
        'vcf_path': 'path_to_vcf'
    }
    
    load_family(
        adapter=mongo_adapter,
        case_id=case['case_id'],
        vcf_path=case['vcf_path']
        )
    
    mongo_case = db.case.find_one()
    
    assert mongo_case['case_id'] == case['case_id']
    
    delete_family(
        adapter=mongo_adapter,
        family_id='1',
    )
    
    mongo_case = db.case.find_one()
    
    assert mongo_case == None

def test_delete_non_existing_family(mongo_adapter):
    db = mongo_adapter.db
    
    with pytest.raises(CaseError):
        delete_family(
            adapter=mongo_adapter,
            family_id='1',
        )
