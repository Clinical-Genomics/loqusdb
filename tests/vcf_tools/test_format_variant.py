from loqusdb.vcf_tools import get_formatted_variant
import pytest

def get_variant(chrom='1', pos='10', rs_id='.', ref='A', alt='T', qual='100', 
filt='INFO', info='.', form='GT', genotypes=['0/1']):
    """Return a variant"""
    
    variant_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(
        chrom, pos, rs_id, ref, alt, qual, filt, info, form
    )
    
    for gt_call in genotypes:
        variant_line += '\t{0}'.format(gt_call)
    
    variant_line += '\n'
    
    return variant_line

def get_header_line(individuals=['proband']):
    """docstring for get_header_line"""
    header_line = ['CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO',
                    'FORMAT']
    for ind_id in individuals:
        header_line.append(ind_id)
    
    return header_line

def test_format_variant():
    """docstring for test_format_variant"""
    variant_line = get_variant()
    header_line = get_header_line()
    
    affected_individuals = set(['proband'])
    formatted_variant = get_formatted_variant(
        variant_line = variant_line,
        header_line = header_line,
        affected_individuals = affected_individuals
    )
    
    assert formatted_variant['_id'] == '1_10_A_T'
    assert formatted_variant['homozygote'] == 0

def test_format_homozygote_variant():
    """docstring for test_format_variant"""
    variant_line = get_variant(genotypes=['1/1'])
    header_line = get_header_line()
    
    affected_individuals = set(['proband'])
    formatted_variant = get_formatted_variant(
        variant_line = variant_line,
        header_line = header_line,
        affected_individuals = affected_individuals
    )
    
    assert formatted_variant['_id'] == '1_10_A_T'
    assert formatted_variant['homozygote'] == 1

def test_format_variant_no_header():
    """docstring for test_format_variant"""
    variant_line = get_variant(genotypes=['1/1'])
    header_line = []
    
    affected_individuals = set(['proband'])
    
    with pytest.raises(Exception):
        formatted_variant = get_formatted_variant(
            variant_line = variant_line,
            header_line = header_line,
            affected_individuals = affected_individuals
        )

def test_format_variant_no_call():
    """docstring for test_format_variant"""
    variant_line = get_variant(genotypes=['./.'])
    header_line = get_header_line()
    
    affected_individuals = set(['proband'])
    formatted_variant = get_formatted_variant(
        variant_line = variant_line,
        header_line = header_line,
        affected_individuals = affected_individuals
    )
    
    assert formatted_variant == {}
