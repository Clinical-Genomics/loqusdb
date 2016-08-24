import pytest

from loqusdb.utils import load_family
from loqusdb.exceptions import CaseError

def test_load_family(mongo_adapter):
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


def test_load_same_family_twice(mongo_adapter):
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
    
    with pytest.raises(CaseError):
        load_family(
            adapter=mongo_adapter,
            case_id=case['case_id'],
            vcf_path=case['vcf_path']
            )
        
