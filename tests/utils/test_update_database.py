import pytest

from loqusdb.exceptions import CaseError
from loqusdb.utils.load import load_database
from loqusdb.utils.update import update_database
from loqusdb.constants import GRCH37


def test_update_database_existing_case(vcf_path, sv_vcf_path, ped_path, real_mongo_adapter):
    """Test that an existing case can be updated with a new VCF type"""
    ## GIVEN a database with a case that only has SNVs
    load_database(
        adapter=real_mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )
    assert real_mongo_adapter.case_count() == 1
    assert real_mongo_adapter.db.case.find_one().get("vcf_sv_path") is None

    ## WHEN updating the same case with an SV file
    nr_inserted = update_database(
        adapter=real_mongo_adapter,
        sv_file=sv_vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )

    ## THEN the SVs are stored and there is still only one case
    assert nr_inserted > 0
    assert real_mongo_adapter.case_count() == 1
    assert real_mongo_adapter.db.case.find_one()["vcf_sv_path"] == sv_vcf_path


def test_update_database_missing_case(vcf_path, ped_path, real_mongo_adapter):
    """Test that updating a case that is not in the database raises an error"""
    ## GIVEN an empty database
    assert real_mongo_adapter.case_count() == 0

    ## WHEN updating a case that does not exist
    ## THEN a CaseError is raised
    with pytest.raises(CaseError):
        update_database(
            adapter=real_mongo_adapter,
            variant_file=vcf_path,
            family_file=ped_path,
            family_type="ped",
        )


def test_update_database_gq_threshold_without_gq(profile_vcf_path, real_mongo_adapter):
    """Test that a GQ threshold requires GQ in the VCF header"""
    ## GIVEN a VCF file without GQ in the header
    ## WHEN updating with a GQ threshold
    ## THEN a SyntaxError is raised before anything is written
    with pytest.raises(SyntaxError):
        update_database(
            adapter=real_mongo_adapter,
            variant_file=profile_vcf_path,
            gq_threshold=20,
            case_id="test",
        )
    assert real_mongo_adapter.case_count() == 0
