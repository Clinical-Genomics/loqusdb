import pytest

from loqusdb.build_models.case import build_case, get_individual_positions
from loqusdb.exceptions import CaseError


def test_get_individual_positions():
    ## GIVEN a list with ids
    inds = ["1", "2", "3"]
    ## WHEN getting the individual positions
    ind_pos = get_individual_positions(inds)
    ## THEN assert they where given the correct position
    assert ind_pos["1"] == 0
    assert ind_pos["2"] == 1
    assert ind_pos["3"] == 2


def test_get_individual_positions_no_inds():
    ## GIVEN a list with ids
    inds = None
    ## WHEN getting the individual positions
    ind_pos = get_individual_positions(inds)
    ## THEN assert an empty dict is returned
    assert ind_pos == {}


def test_build_case_no_ped():
    ## GIVEN some vcf individuals

    vcf_individuals = ["mother", "proband"]
    case_id = "test"

    ## WHEN building a case object
    case_obj = build_case(
        case=None,
        vcf_individuals=vcf_individuals,
        case_id=case_id,
    )

    ## THEN assert that the case got the right ID
    assert case_obj["case_id"] == case_id
    for ind_obj in case_obj["individuals"]:
        assert ind_obj["name"] in vcf_individuals
        assert ind_obj["ind_id"] in vcf_individuals


def test_build_case_no_ped_no_case_id():
    ## WHEN building a case object

    ## THEN assert a CaseError is raised
    with pytest.raises(CaseError):
        ## GIVEN some vcf individuals

        vcf_individuals = ["mother", "proband"]

        case_obj = build_case(
            case=None,
            vcf_individuals=vcf_individuals,
        )


def test_build_case_ped(family_obj, vcf_path):
    ## GIVEN a ped parser family_obj
    vcf_inds = [ind_id for ind_id in family_obj.individuals]
    nr_variants = 10

    ## WHEN building a case object
    case_obj = build_case(
        case=family_obj,
        vcf_individuals=vcf_inds,
        vcf_path=vcf_path,
        nr_variants=nr_variants,
    )

    ## THEN assert that the case has the correct id
    assert case_obj["case_id"] == family_obj.family_id

    for ind_obj in case_obj["individuals"]:
        assert ind_obj["ind_id"] in vcf_inds

    ## THEN assert that the vcf_path was added
    assert case_obj["vcf_path"] == vcf_path

    ## THEN assert that the nr variants is correct
    assert case_obj["nr_variants"] == nr_variants


def test_build_case_ped_sv(family_obj, sv_vcf_path):
    ## GIVEN a ped parser family_obj
    vcf_inds = [ind_id for ind_id in family_obj.individuals]
    nr_sv_variants = 10

    ## WHEN building a case object
    case_obj = build_case(
        case=family_obj,
        sv_individuals=vcf_inds,
        vcf_sv_path=sv_vcf_path,
        nr_sv_variants=nr_sv_variants,
    )

    ## THEN assert that the case has the correct id
    assert case_obj["case_id"] == family_obj.family_id

    case_obj["individuals"] == []
    for ind_obj in case_obj["sv_individuals"]:
        assert ind_obj["ind_id"] in vcf_inds

    ## THEN assert that the vcf_path was added
    assert case_obj["vcf_path"] is None
    assert case_obj["vcf_sv_path"] == sv_vcf_path

    ## THEN assert that the nr variants is correct
    assert case_obj["nr_variants"] is None
    assert case_obj["nr_sv_variants"] == nr_sv_variants


def test_build_case_ped_sv_and_snv(family_obj, sv_vcf_path, vcf_path):
    ## GIVEN a ped parser family_obj
    vcf_inds = [ind_id for ind_id in family_obj.individuals]
    sv_vcf_inds = [ind_id for ind_id in family_obj.individuals]
    nr_sv_variants = 10
    nr_variants = 20

    ## WHEN building a case object
    case_obj = build_case(
        case=family_obj,
        sv_individuals=vcf_inds,
        vcf_sv_path=sv_vcf_path,
        nr_sv_variants=nr_sv_variants,
        vcf_individuals=vcf_inds,
        vcf_path=vcf_path,
        nr_variants=nr_variants,
    )

    ## THEN assert that the case has the correct id
    assert case_obj["case_id"] == family_obj.family_id

    for ind_obj in case_obj["individuals"]:
        assert ind_obj["ind_id"] in vcf_inds

    for ind_obj in case_obj["sv_individuals"]:
        assert ind_obj["ind_id"] in sv_vcf_inds

    ## THEN assert that the vcf_path was added
    assert case_obj["vcf_path"] == vcf_path
    assert case_obj["vcf_sv_path"] == sv_vcf_path

    ## THEN assert that the nr variants is correct
    assert case_obj["nr_variants"] == nr_variants
    assert case_obj["nr_sv_variants"] == nr_sv_variants
