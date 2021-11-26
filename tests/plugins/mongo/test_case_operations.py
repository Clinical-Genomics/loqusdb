import pytest

from loqusdb.exceptions import CaseError


class TestDeleteCase:
    def test_delete_one_case(self, mongo_adapter, case_obj):
        """Test to delete one case"""

        db = mongo_adapter.db

        mongo_case = db.case.find_one()

        assert mongo_case == None

        db.case.insert_one(case_obj)

        mongo_case = db.case.find_one()

        assert mongo_case["case_id"] == case_obj["case_id"]
        assert mongo_case["vcf_path"] == case_obj["vcf_path"]

        mongo_adapter.delete_case(case_obj)

        assert db.case.find_one() == None

    def test_delete_non_existing(self, mongo_adapter, case_obj):
        """Test to delete non exsting case"""

        with pytest.raises(CaseError):
            mongo_adapter.delete_case(case_obj)


class TestInsertCase:
    def test_insert_one_case(self, mongo_adapter, case_obj):
        db = mongo_adapter.db

        mongo_adapter.add_case(case_obj)

        mongo_case = db.case.find_one()

        assert mongo_case["case_id"] == case_obj["case_id"]
        assert mongo_case["vcf_path"] == case_obj["vcf_path"]

    def test_insert_one_case_twice(self, mongo_adapter, case_obj):
        db = mongo_adapter.db

        mongo_adapter.add_case(case_obj)

        with pytest.raises(CaseError):
            mongo_adapter.add_case(case_obj)


class TestGetCase:
    def test_get_case(self, mongo_adapter, case_obj):
        """Test to get non existing case"""

        db = mongo_adapter.db
        db.case.insert_one(case_obj)

        mongo_case = mongo_adapter.case(case_obj)

        assert mongo_case["case_id"] == case_obj["case_id"]
        assert mongo_case["vcf_path"] == case_obj["vcf_path"]

    def test_get_non_existing(self, mongo_adapter, simple_case):
        """Test to get non existing case"""

        db = mongo_adapter.db

        mongo_case = mongo_adapter.case(simple_case)

        assert mongo_case == None

    def test_get_multiple_cases(self, mongo_adapter):
        """Test to get non existing case"""

        db = mongo_adapter.db
        case_1 = {"case_id": "test", "vcf_path": "test.vcf"}

        case_2 = {"case_id": "test2", "vcf_path": "test2.vcf"}

        db.case.insert_one(case_1)
        db.case.insert_one(case_2)

        mongo_cases = mongo_adapter.cases()

        assert sum(1 for i in mongo_cases) == 2

    def test_nr_cases(self, mongo_adapter):
        """Test to get non existing case"""

        db = mongo_adapter.db
        case_1 = {"case_id": "test", "vcf_path": "test.vcf", "vcf_sv_path": None}

        db.case.insert_one(case_1)

        assert mongo_adapter.nr_cases() == 1
        assert mongo_adapter.nr_cases(sv_cases=True) == 0
        assert mongo_adapter.nr_cases(snv_cases=True) == 1
        assert mongo_adapter.nr_cases(snv_cases=True, sv_cases=True) == 1

    def test_nr_cases_only_snv(self, mongo_adapter):
        """Test to get non existing case"""
        db = mongo_adapter.db
        case_1 = {"case_id": "test", "vcf_path": "test.vcf"}

        db.case.insert_one(case_1)

        assert mongo_adapter.nr_cases() == 1
        assert mongo_adapter.nr_cases(sv_cases=True) == 0
        assert mongo_adapter.nr_cases(snv_cases=True) == 1

    def test_nr_cases_sv(self, mongo_adapter):
        """Test to get non existing case"""

        db = mongo_adapter.db
        case_1 = {"case_id": "test", "vcf_sv_path": "test.vcf"}

        db.case.insert_one(case_1)

        assert mongo_adapter.nr_cases() == 1
        assert mongo_adapter.nr_cases(sv_cases=True) == 1
        assert mongo_adapter.nr_cases(snv_cases=True) == 0

    def test_get_multiple_cases(self, mongo_adapter):
        """Test to get non existing case"""

        db = mongo_adapter.db
        case_1 = {"case_id": "test", "vcf_path": "test.vcf", "vcf_sv_path": "test.vcf"}

        case_2 = {"case_id": "test2", "vcf_path": "test2.vcf"}

        case_3 = {"case_id": "test3", "vcf_path": "test3.vcf"}

        db.case.insert_one(case_1)
        db.case.insert_one(case_2)
        db.case.insert_one(case_3)

        assert mongo_adapter.nr_cases() == 3
        assert mongo_adapter.nr_cases(snv_cases=True) == 3
        assert mongo_adapter.nr_cases(sv_cases=True) == 1
        assert mongo_adapter.nr_cases(sv_cases=True, snv_cases=True) == 3
