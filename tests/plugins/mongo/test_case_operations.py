import pytest

from loqusdb.exceptions import CaseError

class TestDeleteCase:
    
    def test_delete_one_case(self, mongo_adapter, simple_case):
        """Test to delete one case"""
    
        db = mongo_adapter.db
    
        db.case.insert(simple_case)
    
        mongo_case = db.case.find_one()
    
        assert mongo_case['case_id'] == simple_case['case_id']
        assert mongo_case['vcf_path'] == simple_case['vcf_path']
    
        mongo_adapter.delete_case(simple_case)

        assert db.case.find_one() == None
    

    def test_delete_non_existing(self, mongo_adapter, simple_case):
        """Test to delete non exsting case"""
        
        mongo_adapter.delete_case(simple_case)
        
        assert True

class TestInsertCase:
    
    def test_insert_one_case(self, mongo_adapter, simple_case):
    
        db = mongo_adapter.db
        
        mongo_adapter.add_case(simple_case)
        
        mongo_case = db.case.find_one()
    
        assert mongo_case['case_id'] == simple_case['case_id']
        assert mongo_case['vcf_path'] == simple_case['vcf_path']

    def test_insert_one_case_twice(self, mongo_adapter, simple_case):
    
        db = mongo_adapter.db
        
        mongo_adapter.add_case(simple_case)
        
        with pytest.raises(CaseError):
            mongo_adapter.add_case(simple_case)
        

class TestGetCase:

    def test_get_case(self, mongo_adapter, simple_case):
        """Test to get non existing case"""
    
        db = mongo_adapter.db
        db.case.insert(simple_case)

        mongo_case = mongo_adapter.case(simple_case)
    
        assert mongo_case['case_id'] == simple_case['case_id']
        assert mongo_case['vcf_path'] == simple_case['vcf_path']
        
        
    def test_get_non_existing(self, mongo_adapter, simple_case):
        """Test to get non existing case"""
    
        db = mongo_adapter.db

        mongo_case = mongo_adapter.case(simple_case)
    
        assert mongo_case == None