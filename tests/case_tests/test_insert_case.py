import pytest
from mongomock import MongoClient
from loqusdb.utils import add_case
from loqusdb.exceptions import CaseError

def test_insert_one_case():
    """Test to insert one case"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    add_case(db, case)
    
    mongo_case = db.case.find_one()
    
    assert mongo_case['case_id'] == 'test'
    assert mongo_case['vcf_path'] == './test.vcf'

def test_insert_one_case_twice():
    """Test to insert one case twice"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    add_case(db, case)
    
    with pytest.raises(CaseError):
        add_case(db, case)