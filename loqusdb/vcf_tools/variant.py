import logging

from vcftoolbox import (Genotype)

from loqusdb.exceptions import CaseError

logger = logging.getLogger(__name__)

# These are coordinate for the pseudo autosomal regions in GRCh37
PAR = {
    'Y': [[10001, 2649520], [59034050, 59373566]],
    'X': [[60001, 2699520], [154931044, 155270560]]
}

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
    

def get_formated_variant(variant, individuals, family_id, gq_treshold=None):
    """Return a formated variant line
    
        Take a vcf formated variant line and return a dictionary with the
        relevant information.
    
        If criterias are not fullfilled, eg. variant have no gt call or quality
        is below gq treshold then an empty dictionary is returned.
        
        Args:
            variant (dict): A variant dictionary
            individuals (list[str]): A list with individual ids
            family_id (str): The family id
        
        Return:
            formated_variant (dict): A variant dictionary
    """
    gq_treshold = gq_treshold or 20
    
    chrom = variant['CHROM'].lstrip('chr')
    pos = int(variant['POS'])
    ref = variant['REF']
    alt = variant['ALT']

    formated_variant = {}

    if ',' in alt:
        raise Exception("Multi allele calls are not allowed.")

    format_field = variant['FORMAT'].split(':')

    found_variant = False
    found_homozygote = False
    found_hemizygote = False

    for ind_id in individuals:
        ind_obj = individuals[ind_id]
        
        if ind_id in variant:
            raw_gt_call = variant[ind_id]
        else:
            raise CaseError("Individual {0} from ped does not exist in"\
                            " vcf".format(ind_id))

        gt_call = dict(zip(
                format_field,
                raw_gt_call.split(':'))
                )

        genotype = Genotype(**gt_call)
        if genotype.genotype_quality >= gq_treshold:
            if genotype.has_variant:
                logger.debug("Found variant in affected")
                found_variant = True
            
                # If variant in X or Y and individual is male,
                # we need to check hemizygosity
                if chrom in ['X','Y'] and ind_obj.sex == 1:
                    if not check_par(chrom, pos):
                        logger.debug("Found hemizygous variant")
                        found_hemizygote = True
                
                if genotype.homo_alt:
                    logger.debug("Found homozygote alternative variant")
                    found_homozygote = True

    if found_variant:
        formated_variant['_id'] = '_'.join([chrom, str(pos), ref, alt])
        formated_variant['chrom'] = chrom
        formated_variant['pos'] = pos
        formated_variant['ref'] = ref
        formated_variant['alt'] = alt
        formated_variant['homozygote'] = 0
        formated_variant['hemizygote'] = 0

        if found_hemizygote:
            formated_variant['hemizygote'] = 1
        elif found_homozygote:
            formated_variant['homozygote'] = 1
        
        if family_id:
            formated_variant['family_id'] = family_id
    
    return formated_variant
