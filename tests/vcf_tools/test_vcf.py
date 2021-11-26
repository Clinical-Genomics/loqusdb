import pytest
from cyvcf2 import VCF
from loqusdb.utils.vcf import get_file_handle, check_vcf


def test_get_file_handle(vcf_path):
    ## GIVEN the path to a vcf

    ## WHEN geting the file handle
    vcf = get_file_handle(vcf_path)

    ## THEN assert that a VCF object is returned
    assert type(vcf) is VCF


def test_get_zipped_file_handle(zipped_vcf_path):
    ## GIVEN the path to a zipped vcf

    ## WHEN geting the file handle
    vcf = get_file_handle(zipped_vcf_path)

    ## THEN assert that a VCF object is returned
    assert type(vcf) is VCF


def test_get_vcf_non_vcf(ped_path):
    ## GIVEN the path to a non vcf

    ## WHEN geting the file handle

    ## THEN assert that a IOError is raised
    with pytest.raises(IOError):
        vcf = get_file_handle(ped_path)


def test_get_vcf_non_existing():
    ## GIVEN the path to a non existing file

    ## WHEN geting the file handle

    ## THEN assert that a IOError is raised
    with pytest.raises(IOError):
        vcf = get_file_handle("hello")


def test_check_vcf(vcf_path):
    ## GIVEN the path to a vcf
    nr_variants = 0
    vcf = VCF(vcf_path)
    inds = vcf.samples
    for var in vcf:
        nr_variants += 1
    ## WHEN checking the vcf
    vcf_info = check_vcf(vcf_path)

    ## THEN assert that the number of variants is correct
    assert vcf_info["nr_variants"] == nr_variants

    ## THEN assert that the individuals are returned
    assert vcf_info["individuals"] == inds

    ## THEN assert that the variant type is correct
    assert vcf_info["variant_type"] == "snv"
