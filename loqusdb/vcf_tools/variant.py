import logging

from vcftoolbox import (Genotype)

logger = logging.getLogger(__name__)

def get_formated_variant(variant, individuals, family_id, gq_treshold=20):
    """Return a formated variant line
    
        Take a vcf formated variant line and return a dictionary with the
        relevant information.
        
        Args:
            variant (cyvcf2.Variant): A vcf formated variant line
            individuals (list[str]): A list with individual ids
            family_id (str): The family id
        
        Return:
            formated_variant (dict): A variant dictionary
    """
    formated_variant = {}
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
        formated_variant['_id'] = '_'.join([chrom, str(pos), ref, alt])
        formated_variant['chrom'] = chrom
        formated_variant['pos'] = pos
        formated_variant['ref'] = ref
        formated_variant['alt'] = alt

        if found_homozygote:
            formated_variant['homozygote'] = 1
        else:
            formated_variant['homozygote'] = 0
        
        if family_id:
            formated_variant['family_id'] = family_id
    
    return formated_variant
