import logging

from vcftoolbox import (Genotype)

from loqusdb.exceptions import CaseError

logger = logging.getLogger(__name__)

# These are coordinate for the pseudo autosomal regions in GRCh37
PAR = {
    'Y': [[10001, 2649520], [59034050, 59373566]],
    'X': [[60001, 2699520], [154931044, 155270560]]
}

GENOTYPE_MAP = {0: 'hom_ref', 1: 'het', 2: 'no_call', 3:'hom_alt'}

def check_par(chrom, pos):
    """Check if a coordinate is in the PAR region
    
        Args:
            chrom(str)
            pos(int)
    
        Returns:
            par(bool)
    """
    par = False
    
    for interval in PAR.get(chrom,[]):
        if (pos >= interval[0] and pos <= interval[1]):
            par = True
    
    return par
    

def get_variant_id(variant):
    """Get a variant id on the format chrom_pos_ref_alt"""
    variant_id = '_'.join([
            str(variant.CHROM),
            str(variant.POS),
            str(variant.REF),
            str(variant.ALT[0])
        ]
    )
    return variant_id

def get_formated_variant(variant, individuals, family_id, ind_positions,
                         gq_treshold=None):
    """Return a formated variant line
    
        Take a vcf formated variant line and return a dictionary with the
        relevant information.
    
        If criterias are not fullfilled, eg. variant have no gt call or quality
        is below gq treshold then an empty dictionary is returned.
        
        Args:
            variant (cyvcf2.Variant)
            individuals (list[str]): A list with individual ids
            ind_positions (dict)
            family_id (str): The family id
        
        Return:
            formated_variant (dict): A variant dictionary
    """
    chrom = variant.CHROM
    if chrom.startswith(('chr', 'CHR', 'Chr')):
        chrom = chrom[3:]
    pos = int(variant.POS)
    end = int(variant.end)
    ref = variant.REF
    alt = variant.ALT[0]

    formated_variant = {}

    if ',' in alt:
        raise Exception("Multi allele calls are not allowed.")


    found_variant = False
    found_homozygote = 0
    found_hemizygote = 0
    
    # Only look at genotypes for the present individuals
    for ind_id in individuals:
        ind_obj = individuals[ind_id]
        
        ind_pos = ind_positions[ind_id]
        gq = int(variant.gt_quals[ind_pos])
        if (gq_treshold and gq < gq_treshold):
            continue
        
        genotype = GENOTYPE_MAP[variant.gt_types[ind_pos]]
        
        if genotype in ['het', 'hom_alt']:
            logger.debug("Found variant")
            found_variant = True
        
            # If variant in X or Y and individual is male,
            # we need to check hemizygosity
            if chrom in ['X','Y'] and ind_obj.sex == 1:
                if not check_par(chrom, pos):
                    logger.debug("Found hemizygous variant")
                    found_hemizygote = 1
            
            if genotype == 'hom_alt':
                logger.debug("Found homozygote alternative variant")
                found_homozygote = 1

    if found_variant:
        formated_variant['_id'] = get_variant_id(variant)
        formated_variant['chrom'] = chrom
        formated_variant['pos'] = pos
        formated_variant['end'] = end
        formated_variant['ref'] = ref
        formated_variant['alt'] = alt
        formated_variant['homozygote'] = found_homozygote
        formated_variant['hemizygote'] = found_hemizygote

        if family_id:
            formated_variant['family_id'] = family_id
    
    return formated_variant
