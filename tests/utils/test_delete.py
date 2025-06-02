from loqusdb.utils.delete import delete
from loqusdb.utils.load import load_database
from loqusdb.constants import GRCH37, GRCH38


def test_delete_case(mongo_adapter, simple_case):
    ## GIVEN a mongoadapter with a inserted case
    db = mongo_adapter.db
    db.case.insert_one(simple_case)
    mongo_case = db.case.find_one()

    assert mongo_case
    ## WHEN deleting the case

    mongo_adapter.delete_case(simple_case)
    ## THEN assert that the case was deleted
    mongo_case = db.case.find_one()

    mongo_case = db.case.find_one()

    assert mongo_case is None


def test_delete_case_and_variants(vcf_path, ped_path, real_mongo_adapter, case_id, case_obj):
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

    delete(adapter=mongo_adapter, case_obj=case_obj, genome_build=GRCH37)

    mongo_case = db.case.find_one()

    assert mongo_case is None

    mongo_variant = db.variant.find_one()

    assert mongo_variant is None


def test_delete_structural_variants(vcf_path, ped_path, real_mongo_adapter, case_id, sv_case_obj):
    # GIVEN a mongo adapter with an inserted case with SVs
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        family_file=ped_path,
        family_type="ped",
        sv_file=sv_case_obj["vcf_sv_path"],
        genome_build=GRCH37,
    )

    mongo_svs = db.structural_variant.find()
    assert len(list(mongo_svs)) == 19

    # WHEN deleteing the case
    delete(adapter=mongo_adapter, case_obj=sv_case_obj, genome_build=GRCH37)

    # All structural variants should be deleted.
    mongo_svs = db.structural_variant.find()
    assert len(list(mongo_svs)) == 0


def test_delete_case_and_variants_grch38(vcf_path, ped_path, real_mongo_adapter, case_id, case_obj):
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

    delete(adapter=mongo_adapter, case_obj=case_obj, genome_build=GRCH38)

    mongo_case = db.case.find_one()

    assert mongo_case is None

    mongo_variant = db.variant.find_one()

    assert mongo_variant is None


def test_delete_structural_variants_grch38(
    vcf_path, ped_path, real_mongo_adapter, case_id, sv_case_obj
):
    # GIVEN a mongo adapter with an inserted case with SVs
    mongo_adapter = real_mongo_adapter
    db = mongo_adapter.db

    load_database(
        adapter=mongo_adapter,
        family_file=ped_path,
        family_type="ped",
        sv_file=sv_case_obj["vcf_sv_path"],
        genome_build=GRCH37,
    )

    mongo_svs = db.structural_variant.find()
    assert len(list(mongo_svs)) == 19

    # WHEN deleteing the case
    delete(adapter=mongo_adapter, case_obj=sv_case_obj, genome_build=GRCH38)

    # All structural variants should be deleted.
    mongo_svs = db.structural_variant.find()
    assert len(list(mongo_svs)) == 0
