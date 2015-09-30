import pytest
from mongomock import MongoClient
from loqusdb.utils import get_case

def test_insert_one_case():
    """Test to insert one case"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    db.case.insert(case)
    
    mongo_case = get_case(db, case)
    
    assert mongo_case['case_id'] == 'test'
    assert mongo_case['vcf_path'] == './test.vcf'

def test_get_non_existing():
    """Test to get non existing case"""
    
    client = MongoClient()
    db = client['loqusdb']

    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    
    mongo_case = get_case(db, case)
    
    assert mongo_case == None