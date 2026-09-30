import pytest
from loqusdb.exceptions import VcfError
from loqusdb.utils.vcf import check_vcf


def test_check_vcf_correct(vcf_path):
    ## GIVEN a vcf file and a counter that checks the number of variants
    true_nr = 0

    with open(vcf_path, "r") as f:
        for line in f:
            if not line.startswith("#"):
                true_nr += 1

    ## WHEN collecting the VCF info
    vcf_info = check_vcf(vcf_path)

    ## THEN assert that the number of variants collected is correct
    assert vcf_info["nr_variants"] == true_nr
    ## THEN assert that the variant type is correct
    assert vcf_info["variant_type"] == "snv"


def test_check_vcf_double_variant(double_vcf_path):
    ## GIVEN a variant file where a variant is duplicated
    ## WHEN checking the vcf
    ## THEN assert that the function raises a VcfError
    with pytest.raises(VcfError):
        check_vcf(double_vcf_path)


def test_check_vcf_unsorted(unsorted_vcf_path):
    ## GIVEN a vcf file with unsorted variants
    ## WHEN checking the vcf
    ## THEN assert that the function raises a VcfError
    with pytest.raises(VcfError):
        check_vcf(unsorted_vcf_path)


def test_check_sv_vcf(sv_vcf_path):
    ## GIVEN a vcf file and a counter that checks the number of variants
    true_nr = 0

    with open(sv_vcf_path, "r") as f:
        for line in f:
            if not line.startswith("#"):
                true_nr += 1

    ## WHEN collecting the VCF info
    vcf_info = check_vcf(sv_vcf_path, expected_type="sv")

    ## THEN assert that the number of variants collected is correct
    assert vcf_info["nr_variants"] == true_nr
    ## THEN assert that the variant type is correct
    assert vcf_info["variant_type"] == "sv"


def test_check_vcf_wrong_type(sv_vcf_path):
    ## GIVEN a sv vcf file

    ## WHEN collecting the VCF info with wrong variant type
    ## THEN assert that a VcfError is raised
    with pytest.raises(VcfError):
        vcf_info = check_vcf(sv_vcf_path, "snv")


def test_check_mixed_manta_and_gatk_sv_vcf(tmp_path):
    vcf_path = tmp_path / "mixed.sv.vcf"
    vcf_path.write_text(
        "##fileformat=VCFv4.2\n"
        "##contig=<ID=1,length=1000000>\n"
        '##INFO=<ID=END,Number=1,Type=Integer,Description="End position">\n'
        '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="SV type">\n'
        '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsample\n"
        "1\t100\tmanta1\tN\t<DEL>\t100\tPASS\tEND=200;SVTYPE=DEL\tGT\t0/1\n"
        "1\t300\tgatk1\tN\t<DUP:TANDEM>\t100\tPASS\tEND=400\tGT\t0/1\n"
    )

    vcf_info = check_vcf(str(vcf_path), expected_type="sv")

    assert vcf_info["variant_type"] == "sv"
    assert vcf_info["nr_variants"] == 2
