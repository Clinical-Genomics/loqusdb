import pytest
from loqusdb.exceptions import CaseError
from loqusdb.utils.load import load_database
from loqusdb.utils.update import update_database
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


def test_update_add_to_existing_snv(vcf_path, ped_path, real_mongo_adapter, case_id, tmp_path):
    mongo_adapter = real_mongo_adapter

    load_database(
        adapter=mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )
    existing_case = dict(mongo_adapter.case({"case_id": case_id}))
    existing_variants = list(mongo_adapter.db.variant.find())
    additional_vcf = tmp_path / "additional.vcf"
    with open(vcf_path) as original_vcf:
        original_vcf_content = original_vcf.read()
    additional_vcf.write_text(
        original_vcf_content
        + "1\t999999\t.\tA\tC\t100\tPASS\tMQ=1\tGT:AD:GQ\t"
        + "\t".join(["0/1:10,10:60"] * 6)
        + "\n"
    )

    nr_inserted = update_database(
        adapter=mongo_adapter,
        variant_file=str(additional_vcf),
        family_file=ped_path,
        family_type="ped",
        add_to_existing_snv=True,
    )

    assert nr_inserted == 1
    updated_case = mongo_adapter.case({"case_id": case_id})
    assert updated_case["nr_variants"] == existing_case["nr_variants"] + nr_inserted
    assert updated_case["vcf_path"] == existing_case["vcf_path"]
    updated_variants = {variant["_id"]: variant for variant in mongo_adapter.db.variant.find()}
    assert all(
        updated_variants[variant["_id"]]["observations"] == variant["observations"]
        for variant in existing_variants
    )
