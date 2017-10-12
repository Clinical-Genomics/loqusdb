import pytest

from loqusdb.exceptions import CaseError

def test_load_family(mongo_adapter, simple_case):
    ## GIVEN a adapter to an empty database
    db = mongo_adapter.db
    
    ## WHEN loading a family to the database
    mongo_adapter.add_family(simple_casem)
    
    ## THEN assert that the case was loaded
    mongo_case = db.case.find_one()
    assert mongo_case['case_id'] == simple_case['case_id']


def test_load_same_family_twice(mongo_adapter, simple_case):
    ## GIVEN a adapter to an empty database
    db = mongo_adapter.db

    ## WHEN loading a family to the database twice
    mongo_adapter.add_family(simple_case)
    
    ## THEN assert that a CaseError is raised
    with pytest.raises(CaseError):
        mongo_adapter.add_family(simple_case)
        
