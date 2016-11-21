from loqusdb.vcf_tools import get_formated_variant
import pytest


def test_format_variant(het_variant):
    formated_variant = get_formated_variant(
        variant=het_variant,
        individuals=['proband'],
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

def test_format_variant_no_gq(variant_no_gq):
    formated_variant = get_formated_variant(
        variant=variant_no_gq,
        individuals=['proband'],
        family_id='1'
        )
    assert formated_variant == {}

def test_format_variant_no_family_id(het_variant):
    formated_variant = get_formated_variant(
        variant=het_variant,
        individuals=['proband'],
        family_id=None
        )
    assert formated_variant
    assert formated_variant.get('family_id') == None


def test_format_homozygote_variant(hom_variant):
    formated_variant = get_formated_variant(
        variant=hom_variant,
        individuals=['proband'],
        family_id='1'
        )
    assert formated_variant['homozygote'] == 1

def test_format_variant_no_call(variant_no_call):
    formated_variant = get_formated_variant(
        variant=variant_no_call,
        individuals=['proband'],
        family_id='1'
        )
    assert formated_variant == {}
