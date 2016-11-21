import pytest
import gzip
from loqusdb.vcf_tools.vcf import get_vcf, get_file_handle

def test_get_file_handle(vcf_path):
    vcf = get_file_handle(vcf_path)
    assert type(vcf) is type(open(vcf_path, 'r'))

def test_get_zipped_file_handle(zipped_vcf_path):
    vcf = get_file_handle(zipped_vcf_path)
    assert type(vcf) is type(gzip.open(zipped_vcf_path, 'r'))

def test_get_vcf_non_vcf(ped_path):
    with pytest.raises(IOError):
        vcf = get_file_handle(ped_path)

def test_get_vcf_non_existing():
    with pytest.raises(IOError):
        vcf = get_file_handle('hello')

def test_get_vcf(vcf_path):
    vcf = get_vcf(vcf_path)
    assert type(vcf) is type((i for i in [1,2]))
