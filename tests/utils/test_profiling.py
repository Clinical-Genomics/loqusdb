import pytest

from loqusdb.utils.profiling import (get_profiles, profile_match, compare_profiles)
from loqusdb.utils.load import (load_profile_variants, load_case)
from loqusdb.utils.vcf import check_vcf

from loqusdb.exceptions import ProfileError

def test_get_profiles(real_mongo_adapter, profile_vcf_path, zipped_vcf_path):

    #Load profile variants
    load_profile_variants(real_mongo_adapter, profile_vcf_path)

    vcf_info = check_vcf(zipped_vcf_path)

    #Get profiles from vcf
    profiles = get_profiles(real_mongo_adapter, zipped_vcf_path)

    #Assert that all individuals are included
    assert list(profiles.keys()) == vcf_info['individuals']

    #Assert that profile strings are of same lengths
    for i, individual in enumerate(profiles.keys()):
        if i==0: length = len(profiles[individual])
        assert len(profiles[individual]) == length


def test_profile_match(real_mongo_adapter, profile_vcf_path, profile_str, case_obj):

    #Load profile variants
    load_profile_variants(real_mongo_adapter, profile_vcf_path)

    #Load case having profiles profile_str
    load_case(real_mongo_adapter, case_obj)

    #Get profiles from vcf
    profiles = {'test_individual': profile_str}

    #Assert that error is raised
    with pytest.raises(ProfileError) as error:

        profile_match(real_mongo_adapter, profiles)

def test_compare_profiles():

    assert compare_profiles('AACC', 'AACC') == 1
    assert compare_profiles('AACC', 'GGCC') == 0.5
    assert compare_profiles('ACCG', 'TCCG') == 0.75
