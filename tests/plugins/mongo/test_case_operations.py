import pytest

from loqusdb.exceptions import CaseError

class TestDeleteCase:
    
    def test_delete_one_case(self, mongo_adapter, simple_case):
        """Test to delete one case"""
    
        db = mongo_adapter.db
    
        mongo_case = db.case.find_one()
        
        assert mongo_case == None
        
        db.case.insert(simple_case)
    
        mongo_case = db.case.find_one()
    
        assert mongo_case['case_id'] == simple_case['case_id']
        assert mongo_case['vcf_path'] == simple_case['vcf_path']
    
        mongo_adapter.delete_case(simple_case)

        assert db.case.find_one() == None
    

    def test_delete_non_existing(self, mongo_adapter, simple_case):
        """Test to delete non exsting case"""
        
        with pytest.raises(CaseError):
            mongo_adapter.delete_case(simple_case)

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
    
    def test_get_multiple_cases(self, mongo_adapter):
        """Test to get non existing case"""
    
        db = mongo_adapter.db
        case_1 = {
            'case_id': 'test',
            'vcf_path': 'test.vcf'
        }

        case_2 = {
            'case_id': 'test2',
            'vcf_path': 'test2.vcf'
        }
        
        db.case.insert(case_1)
        db.case.insert(case_2)

        mongo_cases = mongo_adapter.cases()

        assert mongo_cases.count() == 2
