import pytest
from mongomock import MongoClient
from loqusdb.utils import delete_case

def test_delete_one_case():
    """Test to delete one case"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    db.case.insert(case)
    
    mongo_case = db.case.find_one()
    
    assert mongo_case['case_id'] == 'test'
    assert mongo_case['vcf_path'] == './test.vcf'
    
    delete_case(db, case)

    assert db.case.find_one() == None
    

def test_delete_non_existing():
    """Test to delete non exsting case"""

    client = MongoClient()
    db = client['loqusdb']

    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    
    delete_case(db, case)
    