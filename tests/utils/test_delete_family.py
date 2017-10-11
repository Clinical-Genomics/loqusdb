import pytest
from loqusdb.models import Case
from loqusdb.exceptions import CaseError


def test_delete_family(mongo_adapter):
    ## GIVEN a mongo adapter with a case
    db = mongo_adapter.db
    case = {
        'case_id': '1',
        'vcf_path': 'path_to_vcf'
    }
    
    db.case.insert_one(case)
    mongo_case = db.case.find_one()
    assert mongo_case['case_id'] == case['case_id']
    
    ## WHEN deleting the case
    mongo_adapter.delete_case(case)
    
    ## THEN assert that the case was deleted
    mongo_case = db.case.find_one()
    
    assert mongo_case == None

def test_delete_non_existing_family(mongo_adapter):
    ## GIVEN a mongo adapter and a empty database
    case = {
        'case_id': '1',
        'vcf_path': 'path_to_vcf'
    }
    
    ## WHEN deleting a non existing case
    with pytest.raises(CaseError):
    ## THEN assert a CaseError is raised
        mongo_adapter.delete_case(case)
