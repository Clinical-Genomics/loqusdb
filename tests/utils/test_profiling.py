import pytest
from loqusdb.exceptions import ProfileError
from loqusdb.utils.load import load_profile_variants, load_case
from loqusdb.utils.profiling import get_profiles, profile_match, compare_profiles, check_duplicates
from loqusdb.utils.vcf import check_vcf


def test_get_profiles(real_mongo_adapter, profile_vcf_path, zipped_vcf_path):
    # Load profile variants
    load_profile_variants(real_mongo_adapter, profile_vcf_path)

    vcf_info = check_vcf(zipped_vcf_path)

    # Get profiles from vcf
    profiles = get_profiles(real_mongo_adapter, zipped_vcf_path, False)

    # Assert that all individuals are included
    assert list(profiles.keys()) == vcf_info["individuals"]

    # Assert that profile strings are of same lengths
    for i, individual in enumerate(profiles.keys()):
        if i == 0:
            length = len(profiles[individual])
        assert len(profiles[individual]) == length


def test_profile_match(real_mongo_adapter, profile_vcf_path, profile_list, case_obj):
    # Load profile variants
    load_profile_variants(real_mongo_adapter, profile_vcf_path)

    # Load case having profiles profile_list
    load_case(real_mongo_adapter, case_obj)

    # Get profiles from vcf
    profiles = {"test_individual": profile_list}

    # Assert that error is raised
    with pytest.raises(ProfileError) as error:
        profile_match(real_mongo_adapter, profiles)


def test_check_duplicates(real_mongo_adapter, profile_vcf_path, profile_list, case_obj):
    # Load profile variants
    load_profile_variants(real_mongo_adapter, profile_vcf_path)
    # Load case having profiles profile_list
    load_case(real_mongo_adapter, case_obj)
    # Create profiles dictionary
    profiles = {"test_individual": profile_list}
    # match profiles to the profiles in the database
    match = check_duplicates(real_mongo_adapter, profiles, hard_threshold=0.95)
    # This should match with the sample in the database
    assert match["profile"] == profile_list

    # Change last genotype, now no matches should be found
    profiles = {"test_individual": profile_list[:-1] + ["NN"]}
    match = check_duplicates(real_mongo_adapter, profiles, hard_threshold=0.80)
    assert match is None

    # Lower threshold. Now match should be found
    match = check_duplicates(real_mongo_adapter, profiles, hard_threshold=0.75)
    assert match["profile"] == profile_list


def test_compare_profiles():
    assert compare_profiles(["AA", "CC"], ["AA", "CC"]) == 1.0
    assert compare_profiles(["AA", "CC"], ["GG", "CC"]) == 0.5
    assert compare_profiles(["AC", "CG"], ["TC", "CG"]) == 0.5
    assert compare_profiles(["AC", "GT"], ["AA", "GG"]) == 0.0
