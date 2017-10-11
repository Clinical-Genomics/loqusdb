from loqusdb.build_models import build_variant
import pytest


def test_format_variant(het_variant, individuals, ind_positions, case_id):
    ## GIVEN a parsed variant
    
    ## WHEN building an internal variant
    formated_variant = build_variant(
        variant=het_variant,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id=case_id
        )
    
    expected_id = '_'.join([
        het_variant.CHROM,
        str(het_variant.POS), 
        het_variant.REF, 
        het_variant.ALT[0]
    ])
    
    ## THEN assert it was built in a correct way
    assert formated_variant
    assert formated_variant['variant_id'] == expected_id
    assert formated_variant['chrom'] == het_variant.CHROM
    assert formated_variant['pos'] == het_variant.POS
    assert formated_variant['ref'] == het_variant.REF
    assert formated_variant['alt'] == het_variant.ALT[0]
    assert formated_variant['case_id'] == case_id
    assert formated_variant['homozygote'] == 0

def test_format_variant_no_gq(variant_no_gq, individuals, ind_positions, case_id):

    formated_variant = build_variant(
        variant=variant_no_gq,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id=case_id,
        gq_treshold=20
        )
    assert formated_variant is None

def test_format_variant_chr_prefix(variant_chr, individuals, ind_positions, case_id):

    formated_variant = build_variant(
        variant=variant_chr,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id=case_id,
        gq_treshold=20
        )
    assert formated_variant['chrom'] == variant_chr.CHROM[3:]


def test_format_variant_no_family_id(het_variant, individuals, ind_positions):
    formated_variant = build_variant(
        variant=het_variant,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id=None
        )
    assert formated_variant
    assert formated_variant.get('case_id') == None
    assert formated_variant['homozygote'] == 0
    assert formated_variant['hemizygote'] == 0

def test_format_homozygote_variant(hom_variant, individuals, case_id, ind_positions):

    formated_variant = build_variant(
        variant=hom_variant,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id=case_id
        )
    assert formated_variant['homozygote'] == 1
    assert formated_variant['hemizygote'] == 0

def test_format_hemizygote_variant(hem_variant, individuals, case_id, ind_positions):

    formated_variant = build_variant(
        variant=hem_variant,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id=case_id
        )
    assert formated_variant['homozygote'] == 0
    assert formated_variant['hemizygote'] == 1

def test_format_variant_no_call(variant_no_call, individuals, case_id, ind_positions):

    formated_variant = build_variant(
        variant=variant_no_call,
        ind_positions=ind_positions,
        individuals=individuals,
        case_id=case_id
        )
        
    assert formated_variant is None
