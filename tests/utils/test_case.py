import pytest
from loqusdb.exceptions import CaseError
from loqusdb.utils.case import update_case


def test_update_case(case_obj, sv_case_obj):
    ## GIVEN a case with snv info and a case with sv info
    assert sv_case_obj["vcf_path"] is None
    assert case_obj["vcf_path"] is not None
    assert case_obj["vcf_sv_path"] is None
    assert sv_case_obj["vcf_sv_path"] is not None

    ## WHEN updating the case
    updated_case = update_case(case_obj=sv_case_obj, existing_case=case_obj)

    ## THEN assert that the cases have been merged without affecting the original cases
    assert updated_case["vcf_path"] is not None
    assert updated_case["vcf_path"] == case_obj["vcf_path"]
    assert sv_case_obj["vcf_path"] is None

    assert updated_case["vcf_sv_path"] is not None
    assert updated_case["vcf_sv_path"] == sv_case_obj["vcf_sv_path"]
    assert case_obj["vcf_sv_path"] is None

    assert updated_case["nr_variants"] == case_obj["nr_variants"]
    assert updated_case["nr_sv_variants"] == sv_case_obj["nr_sv_variants"]


def test_update_existing_vcf(case_obj):
    ## GIVEN a case object with VCF information
    ## WHEN trying to update existing VCF information
    ## THEN assert that a CaseError is raised
    with pytest.raises(CaseError):
        updated_case = update_case(case_obj, case_obj)
