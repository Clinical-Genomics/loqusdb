import pytest
from loqusdb.exceptions import CaseError
from loqusdb.utils.load import load_database
from loqusdb.constants import GRCH37, GRCH38


def test_load_database(vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )

    mongo_case = db.case.find_one()

    assert mongo_case["case_id"] == case_id


def test_load_database_alternative_ped(vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        case_id="alternative",
        genome_build=GRCH37,
    )

    mongo_case = db.case.find_one()
    mongo_variant = db.variant.find_one()

    assert mongo_case["case_id"] == "alternative"
    assert mongo_variant["families"] == ["alternative"]


def test_load_database_wrong_ped(vcf_path, funny_ped_path, real_mongo_adapter):
    mongo_adapter = real_mongo_adapter
    ## GIVEN a vcf and ped file with wrong individuals
    ## WHEN loading the information
    ## THEN Error should be raised since individuals is not in vcf
    with pytest.raises(CaseError):
        load_database(
            adapter=mongo_adapter,
            variant_file=vcf_path,
            family_file=funny_ped_path,
            family_type="ped",
            genome_build=GRCH37,
        )


def test_load_database_grch38(vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH38,
    )

    mongo_case = db.case.find_one()

    assert mongo_case["case_id"] == case_id


def test_load_database_alternative_ped_grch38(vcf_path, ped_path, real_mongo_adapter, case_id):
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        case_id="alternative",
        genome_build=GRCH38,
    )

    mongo_case = db.case.find_one()
    mongo_variant = db.variant.find_one()

    assert mongo_case["case_id"] == "alternative"
    assert mongo_variant["families"] == ["alternative"]


def test_load_database_wrong_ped_grch38(vcf_path, funny_ped_path, real_mongo_adapter):
    mongo_adapter = real_mongo_adapter
    ## GIVEN a vcf and ped file with wrong individuals
    ## WHEN loading the information
    ## THEN Error should be raised since individuals is not in vcf
    with pytest.raises(CaseError):
        load_database(
            adapter=mongo_adapter,
            variant_file=vcf_path,
            family_file=funny_ped_path,
            family_type="ped",
            genome_build=GRCH38,
        )
