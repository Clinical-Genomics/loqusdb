import pytest

from loqusdb.vcf_tools.vcf import (check_vcf, get_vcf)
from loqusdb.exceptions import VcfError

def test_check_vcf_correct(vcf_path):
    true_nr = 0
    
    with open(vcf_path, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                true_nr += 1
    
    vcf_obj = get_vcf(vcf_path)
    nr_variants = check_vcf(vcf_obj)
    
    assert nr_variants == true_nr

def test_check_vcf_double_variant(double_vcf_path):
    vcf_obj = get_vcf(double_vcf_path)
    with pytest.raises(VcfError):
        check_vcf(vcf_obj)

def test_check_vcf_unsorted(unsorted_vcf_path):
    vcf_obj = get_vcf(unsorted_vcf_path)
    with pytest.raises(VcfError):
        check_vcf(vcf_obj)