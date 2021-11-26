import pytest
from loqusdb.exceptions import CaseError

from loqusdb.utils.load import update_case, load_case


def test_load_family(mongo_adapter, simple_case):
    ## GIVEN a adapter to an empty database
    db = mongo_adapter.db

    ## WHEN loading a family to the database
    mongo_adapter.add_case(simple_case)

    ## THEN assert that the case was loaded
    mongo_case = db.case.find_one()
    assert mongo_case["case_id"] == simple_case["case_id"]


def test_load_same_family_twice(mongo_adapter, simple_case):
    ## GIVEN a adapter to an empty database
    db = mongo_adapter.db

    ## WHEN loading a family to the database twice
    mongo_adapter.add_case(simple_case)

    ## THEN assert that a CaseError is raised
    with pytest.raises(CaseError):
        mongo_adapter.add_case(simple_case)


def test_update_case(case_obj, sv_case_obj):
    ## GIVEN an existing case and a case with new info

    ## WHEN merging the two case objs
    updated_case = update_case(sv_case_obj, case_obj)

    ## THEN assert that the updated case includes information from both cases
    assert updated_case["sv_individuals"] == sv_case_obj["sv_individuals"]
    assert updated_case["sv_individuals"] != case_obj["sv_individuals"]

    assert updated_case["_sv_inds"] == sv_case_obj["_sv_inds"]
    assert updated_case["_sv_inds"] != case_obj["_sv_inds"]

    assert updated_case["nr_variants"] == case_obj["nr_variants"]
    assert updated_case["nr_sv_variants"] == sv_case_obj["nr_sv_variants"]


def test_update_case_same_vcf(case_obj, sv_case_obj):
    ## GIVEN an existing case and a case with new info
    sv_case_obj["vcf_path"] = case_obj["vcf_path"]
    ## WHEN merging the two case objs
    ## THEN assert that a CaseError is raised since we are trying to modify existing VCF
    with pytest.raises(CaseError):
        updated_case = update_case(sv_case_obj, case_obj)


def test_load_complete_case(mongo_adapter, complete_case_obj):
    ## GIVEN a case that includes both svs and snvs
    db = mongo_adapter.db

    ## WHEN loading the case
    case_obj = load_case(mongo_adapter, complete_case_obj)
    ## THEN assert that all info is added
    loaded_case = db.case.find_one()

    assert len(loaded_case["individuals"]) == 3
    assert len(loaded_case["sv_individuals"]) == 3
    assert loaded_case["nr_variants"] > 0
    assert loaded_case["nr_sv_variants"] > 0
