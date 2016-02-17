import logging

from vcftoolbox import Genotype

logger = logging.getLogger(__name__)

def get_variant_id(chrom, pos, ref, alt):
    """docstring for get_variant_id"""
    return '_'.join([chrom, pos, ref, alt])

def get_formated_variant(variant_line=None, variant_dict=None, header_line = None,
                        affected_individuals = None):
    """Return a formatted variant line
    
        Take a vcf formatted variant line and return a dictionary with the
        relevant information.
        
        Args:
            variant_line (str): A vcf formatted variant line
            variant_dict (dict): A variant dictionary
        
        Return:
            formatted_variant (dict): A variant dictionary
    """
    if not header_line:
        raise Exception("Need to provide a header line to format variant")
    
    formatted_variant = {}
    
    if variant_line:
        splitted_line = variant_line.rstrip().split('\t')
        
        chrom = splitted_line[0].rstrip('chr')
        pos = splitted_line[1]
        ref = splitted_line[3]
        alt = splitted_line[4]
        
        if len(splitted_line) > 7:
            format_field = splitted_line[8].split(':')
        
    
    elif variant_dict:
        chrom = variant_dict['CHROM'].rstrip('chr')
        pos = variant_dict['POS']
        ref = variant_dict['REF']
        alt = variant_dict['ALT']
        
        format_field = variant_dict.get('FORMAT','').split(':')
        

    if ',' in alt:
        raise Exception("Multi allele calls are not allowed.")

    
    found_variant = False
    found_homozygote = False
    
    
    for index, ind_id in enumerate(header_line):
        if ind_id in affected_individuals:
            if variant_line:
                raw_gt_call = splitted_line[index].split(':')
            elif variant_dict:
                raw_gt_call = variant_dict.get(ind_id,'').split(':')
                
            gt_call = dict(zip(
                    format_field,
                    raw_gt_call)
                    )
            
            genotype = Genotype(**gt_call)
            
            if genotype.has_variant:
                logger.debug("Found variant in affected")
                found_variant = True
            if genotype.homo_alt:
                logger.debug("Found homozygote alternative variant in affected")
                found_homozygote = True
    
    
    if found_variant:
        formatted_variant['_id'] = get_variant_id(
            chrom = chrom, 
            pos = pos, 
            ref = ref, 
            alt = alt
        )
        if found_homozygote:
            formatted_variant['homozygote'] = 1
        else:
            formatted_variant['homozygote'] = 0
            
    
    return formatted_variant
