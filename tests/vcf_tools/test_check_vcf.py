import pytest

from loqusdb.vcf_tools.vcf import check_vcf
from loqusdb.exceptions import VcfError

def test_check_vcf_correct(vcf_path):
    true_nr = 0
    
    with open(vcf_path, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                true_nr += 1
    
    with open(vcf_path, 'r') as f:
        nr_variants = check_vcf(f)
    
    assert nr_variants == true_nr

def test_check_vcf_double_variant(double_vcf_path):
    with pytest.raises(VcfError):
        with open(double_vcf_path, 'r') as f:
            check_vcf(f)

def test_check_vcf_unsorted(unsorted_vcf_path):
    with pytest.raises(VcfError):
        with open(unsorted_vcf_path, 'r') as f:
            check_vcf(f)