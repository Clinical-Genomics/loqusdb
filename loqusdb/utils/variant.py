import logging

from pprint import pprint as pp
LOG = logging.getLogger(__name__)

def format_info(variant, variant_type='snv'):
    """Format the info field for SNV variants
    
    Args:
        variant(dict)
        variant_type(str): snv or sv
    
    Returns:
        vcf_info(str): A VCF formated info field
    """
    
    observations = variant.get('observations',0)

    homozygotes = variant.get('homozygote')
    hemizygotes = variant.get('hemizygote')

    
    vcf_info = f"Obs={observations}"
    if homozygotes:
        vcf_info += f";Hom={homozygotes}"
    if hemizygotes:
        vcf_info += f";Hem={hemizygotes}"

    # This is SV specific
    if variant_type == 'sv':
        end = int((variant['end_left'] + variant['end_right'])/2)
        
        vcf_info += f";SVTYPE={variant['sv_type']};END={end};SVLEN={variant['length']}"

    return vcf_info

def format_variant(variant, variant_type='snv'):
    """Convert variant information to a VCF formated string
    
    Args:
        variant(dict)
        variant_type(str)
    
    Returns:
        vcf_variant(str)
    """
    chrom = variant.get('chrom')
    pos = variant.get('start')
    
    ref = variant.get('ref')
    alt = variant.get('alt')
    
    if variant_type == 'sv':
        pos = int((variant['pos_left'] + variant['pos_right'])/2)
        ref = 'N'
        alt = f"<{variant['sv_type']}>"

    info = None
    
    info = format_info(variant, variant_type=variant_type)

    variant_line = f"{chrom}\t{pos}\t.\t{ref}\t{alt}\t.\t.\t{info}"
    
    return variant_line