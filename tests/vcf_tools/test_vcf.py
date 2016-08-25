import pytest

from loqusdb.vcf_tools import get_vcf
from cyvcf2 import VCF

def test_get_vcf(vcf_path):
    vcf = get_vcf(vcf_path)
    assert type(vcf) is VCF

def test_get_vcf_non_vcf(ped_path):
    with pytest.raises(IOError):
        vcf = get_vcf(ped_path)

def test_get_vcf_non_existing():
    with pytest.raises(IOError):
        vcf = get_vcf('hello')
