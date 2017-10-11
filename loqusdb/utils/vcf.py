import os
import logging

from cyvcf2 import VCF

from loqusdb.exceptions import VcfError
from loqusdb.build_models.variant import get_variant_id

logger = logging.getLogger(__name__)
VALID_ENDINGS = ['.vcf', '.gz']

def get_file_handle(file_path):
    """Return cyvcf2 VCF object
    
    Args:
        file_path(str)
    
    Returns:
        vcf_obj(cyvcf2.VCF)
    """
    logger.debug("Check if file end is correct")
    
    if not os.path.exists(file_path):
        raise IOError("No such file:{0}".format(file_path))
    
    if not os.path.splitext(file_path)[-1] in VALID_ENDINGS:
        raise IOError("Not a valid vcf file name: {}".format(file_path))
    
    vcf_obj = VCF(file_path)
    
    return vcf_obj

def get_vcf(file_path):
    """Yield variants from a vcf file
    
    Args:
        file_path(str)
    
    Yields:
        vcf_obj(cyvcf2.VCF): An iterable with cyvcf2.Variant

    """

    vcf_obj = get_file_handle(file_path)
    
    return vcf_obj

def check_vcf(variants):
    """Check if there are any problems with the vcf file

    Args:
        variants(iterable(cyvcf2.Variant))

    Returns:
        nr_variants(int)
    """
    logger.info("Check if vcf is on correct format...")
    nr_variants = 0
    previous_pos = None
    previous_chrom = None
    
    posititon_variants = set()
    
    for variant in variants:
        if variant.var_type == 'sv':
            variant_type = 'sv'
        else:
            variant_type = 'snv'
        
        nr_variants += 1
        
        current_chrom = variant.CHROM
        current_pos = variant.POS
        
        # We start with a simple id that can be used by SV:s
        variant_id = "{0}_{1}".format(current_chrom, current_pos)
        if variant_type == 'snv':
            variant_id = get_variant_id(variant)
        
        if not previous_chrom:
            # Set the variables for first time
            previous_chrom = current_chrom
            previous_pos = current_pos
            posititon_variants = set([variant_id])

            continue
            
        if current_chrom != previous_chrom:
            previous_chrom = current_chrom
            previous_pos = current_pos
            posititon_variants = set([variant_id])
            continue
        
        
        if (current_pos == previous_pos and variant_type == 'snv'):
            if variant_id in posititon_variants:
                raise VcfError("Variant {0} occurs several times"\
                               " in vcf".format(variant_id))
            else:
                posititon_variants.add(variant_id)
        else:
            if not current_pos >= previous_pos:
                raise VcfError("Vcf if not sorted in a correct way")
            previous_pos = current_pos
            posititon_variants = set([variant_id])

    return nr_variants
