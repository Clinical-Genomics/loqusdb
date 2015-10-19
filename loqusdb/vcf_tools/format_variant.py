import logging

logger = logging.getLogger(__name__)


def get_variant_id(chrom, pos, ref, alt):
    """Return a variant id
    
        Args:
            chrom (str)
            pos (str)
            ref (str)
            alt (str)
        
        Returns:
            variant_id (str): chrom_pos_ref_alt
    """
    
    return '_'.join([chrom, pos, ref, alt])

def get_variant(variant_line=None, variant_dict=None):
    """Return a formatted variant line
    
        Take a vcf formatted variant line and return a dictionary with the
        relevant information.
        
        Args:
            variant_line (str): A vcf formatted variant line
            variant_dict (dict): A variant dictionary
        
        Return:
            variant (dict): A variant dictionary
    """
    mongo_variant = {}
    if variant_line:
        splitted_line = variant_line.rstrip().split()
        
        chrom = splitted_line[0]
        pos = splitted_line[1]
        ref = splitted_line[3]
        alt = splitted_line[4]
        
        if ',' in alt:
            raise Exception("Multi allele calls are not allowed.")
    
        variant = {}
    variant['variant_id'] = get_variant_id(
        chrom = chrom, 
        pos = pos, 
        ref = ref, 
        alt = alt
    )
    
    return variant
