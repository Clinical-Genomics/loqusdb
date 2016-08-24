import logging

from vcftoolbox import (get_variant_dict, get_variant_id, Genotype)

logger = logging.getLogger(__name__)


def get_formated_variant(variant, individuals, family_id, gq_treshold=20):
    """Return a formatted variant line
    
        Take a vcf formatted variant line and return a dictionary with the
        relevant information.
        
        Args:
            variant (cyvcf2.Variant): A vcf formatted variant line
            individuals (list[str]): A list with individual ids
        
        Return:
            formatted_variant (dict): A variant dictionary
    """
    formatted_variant = {}
    splitted_line = str(variant).rstrip().split('\t')

    chrom = variant.CHROM.rstrip('chr')
    pos = variant.POS
    ref = variant.REF
    alt = variant.ALT[0]

    if len(splitted_line) > 7:
        format_field = splitted_line[8].split(':')

    if ',' in alt:
        raise Exception("Multi allele calls are not allowed.")

    found_variant = False
    found_homozygote = False

    for index, raw_gt_call in enumerate(splitted_line[9:]):
        gt_call = dict(zip(
                format_field,
                raw_gt_call.split(':'))
                )

        genotype = Genotype(**gt_call)
        
        if genotype.genotype_quality >= gq_treshold:
            if genotype.has_variant:
                logger.debug("Found variant in affected")
                found_variant = True
            if genotype.homo_alt:
                logger.debug("Found homozygote alternative variant in affected")
                found_homozygote = True

    if found_variant:
        formatted_variant['_id'] = '_'.join([chrom, str(pos), ref, alt])
        formatted_variant['chrom'] = chrom
        formatted_variant['pos'] = pos
        formatted_variant['ref'] = ref
        formatted_variant['alt'] = alt

        if found_homozygote:
            formatted_variant['homozygote'] = 1
        else:
            formatted_variant['homozygote'] = 0
        
        if family_id:
            formatted_variant['family_id'] = family_id
    
    return formatted_variant
