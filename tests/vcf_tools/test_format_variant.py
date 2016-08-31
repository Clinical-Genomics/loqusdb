from loqusdb.vcf_tools import get_formated_variant
import pytest


def test_format_variant(cyvcf2_het_variant):
    formated_variant = get_formated_variant(
        variant=cyvcf2_het_variant,
        individuals=[],
        family_id='1'
        )
    assert formated_variant
    assert formated_variant['_id'] == '1_10_A_T'
    assert formated_variant['chrom'] == '1'
    assert formated_variant['pos'] == 10
    assert formated_variant['ref'] == 'A'
    assert formated_variant['alt'] == 'T'
    assert formated_variant['family_id'] == '1'
    assert formated_variant['homozygote'] == 0

def test_format_variant_no_gq(cyvcf2_variant_no_gq):
    formated_variant = get_formated_variant(
        variant=cyvcf2_variant_no_gq,
        individuals=[],
        family_id='1'
        )
    assert formated_variant == {}

def test_format_variant_no_family_id(cyvcf2_het_variant):
    formated_variant = get_formated_variant(
        variant=cyvcf2_het_variant,
        individuals=[],
        family_id=None
        )
    assert formated_variant
    assert formated_variant.get('family_id') == None


def test_format_homozygote_variant(cyvcf2_hom_variant):
    formated_variant = get_formated_variant(
        variant=cyvcf2_hom_variant,
        individuals=[],
        family_id='1'
        )
    assert formated_variant['homozygote'] == 1

def test_format_variant_no_call(cyvcf2_variant_no_call):
    formated_variant = get_formated_variant(
        variant=cyvcf2_variant_no_call,
        individuals=[],
        family_id='1'
        )
    assert formated_variant == {}
