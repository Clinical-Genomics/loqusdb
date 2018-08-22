import pytest

from loqusdb.utils.vcf import (check_vcf, get_vcf)
from loqusdb.exceptions import VcfError

def test_check_vcf_correct(vcf_path):
    ## GIVEN a vcf file and a counter that checks the number of variants
    true_nr = 0
    
    with open(vcf_path, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                true_nr += 1
    
    ## WHEN collecting the VCF info
    vcf_obj = get_vcf(vcf_path)
    vcf_info = check_vcf(vcf_obj)
    
    ## THEN assert that the number of variants collected is correct
    assert vcf_info['nr_variants'] == true_nr
    ## THEN assert that the variant type is correct
    assert vcf_info['variant_type'] == 'snv'

def test_check_vcf_double_variant(double_vcf_path):
    ## GIVEN a variant file where a variant is duplicated
    vcf_obj = get_vcf(double_vcf_path)
    ## WHEN checking the vcf
    ## THEN assert that the function raises a VcfError
    with pytest.raises(VcfError):
        check_vcf(vcf_obj)

def test_check_vcf_unsorted(unsorted_vcf_path):
    ## GIVEN a vcf file with unsorted variants
    vcf_obj = get_vcf(unsorted_vcf_path)
    ## WHEN checking the vcf
    ## THEN assert that the function raises a VcfError
    with pytest.raises(VcfError):
        check_vcf(vcf_obj)

def test_check_sv_vcf(sv_vcf_path):
    ## GIVEN a vcf file and a counter that checks the number of variants
    true_nr = 0
    
    with open(sv_vcf_path, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                true_nr += 1
    
    ## WHEN collecting the VCF info
    vcf_obj = get_vcf(sv_vcf_path)
    vcf_info = check_vcf(vcf_obj)
    
    ## THEN assert that the number of variants collected is correct
    assert vcf_info['nr_variants'] == true_nr
    ## THEN assert that the variant type is correct
    assert vcf_info['variant_type'] == 'sv'
