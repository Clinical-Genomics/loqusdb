import os
import logging

from cyvcf2 import VCF

from loqusdb.exceptions import VcfError
from loqusdb.build_models.variant import get_variant_id

LOG = logging.getLogger(__name__)
VALID_ENDINGS = ['.vcf', '.gz']

def get_file_handle(file_path):
    """Return cyvcf2 VCF object
    
    Args:
        file_path(str)
    
    Returns:
        vcf_obj(cyvcf2.VCF)
    """
    LOG.debug("Check if file end is correct")
    
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

def check_sorting(previous_chrom, previous_pos, current_chrom, current_pos):
    """docstring for check_sorting"""
    pass

def check_vcf(variants):
    """Check if there are any problems with the vcf file

    Args:
        variants(iterable(cyvcf2.Variant))

    Returns:
        vcf_info(dict): dict like {'nr_variants':<INT>, 'variant_type': <STR>}
                        'variant_type' in ['snv', 'sv']
    """
    LOG.info("Check if vcf is on correct format...")
    
    nr_variants = 0
    variant_type = None
    
    previous_pos = None
    previous_chrom = None
    
    posititon_variants = set()
    
    for variant in variants:

        # Check the type of variant
        current_type = 'sv' if variant.var_type == 'sv' else 'snv'
        if not variant_type:
            variant_type = current_type

        # Vcf can not include both snvs and svs
        if variant_type != current_type:
            raise VcfError("Vcf includes a mix of snvs and svs")

        nr_variants += 1
        
        current_chrom = variant.CHROM
        current_pos = variant.POS
        
        # We start with a simple id that can be used by SV:s
        variant_id = "{0}_{1}".format(current_chrom, current_pos)
        if variant_type == 'snv':
            variant_id = get_variant_id(variant)

        # Initiate variables
        if not previous_chrom:
            previous_chrom = current_chrom
            previous_pos = current_pos
            posititon_variants = set([variant_id])

            continue

        # Update variables if new chromosome
        if current_chrom != previous_chrom:
            previous_chrom = current_chrom
            previous_pos = current_pos
            posititon_variants = set([variant_id])
            continue
        
        if variant_type == 'snv':
            # Check if variant is unique
            if current_pos == previous_pos:
                if variant_id in posititon_variants:
                    raise VcfError("Variant {0} occurs several times"\
                                   " in vcf".format(variant_id))
                else:
                    posititon_variants.add(variant_id)
            # Check if vcf is sorted
            else:
                if not current_pos >= previous_pos:
                    raise VcfError("Vcf if not sorted in a correct way")
                previous_pos = current_pos
                posititon_variants = set([variant_id])
    
    vcf_info = {
        'nr_variants': nr_variants,
        'variant_type': variant_type
    }

    return vcf_info
