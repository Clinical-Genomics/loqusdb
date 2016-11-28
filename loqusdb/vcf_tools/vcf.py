import os
import gzip
import logging

from codecs import open

from loqusdb.exceptions import VcfError

logger = logging.getLogger(__name__)
VALID_ENDINGS = ['.vcf', '.gz']

def get_file_handle(file_path):
    """Return a opened file"""
    logger.debug("Check if file end is correct")
    
    if not os.path.exists(file_path):
        raise IOError("No such file:{0}".format(file_path))
    
    if not os.path.splitext(file_path)[-1] in VALID_ENDINGS:
        raise IOError("Not a valid vcf file name: {}".format(file_path))
    
    if file_path.endswith('.gz'):
        file_handle = gzip.open(file_path, 'r')
    else:
        file_handle = open(file_path, 'r')
    
    return file_handle

def get_vcf(file_path):
    """Yield variants from a vcf file
    
        Args:
            file_path(str)
        
        Yields:
            variant(dict): Variant dictionaries

    """

    file_handle = get_file_handle(file_path)

    header = []
    for line in file_handle:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split('\t')
        else:
            variant = dict(zip(header, line.split('\t')))
            yield variant

def check_vcf(variants):
    """Check if there are any problems with the vcf file
    
        Args:
            variants(iterable(str))
        
        Returns:
            nr_variants(int)
    """
    logger.info("Check if correct is on correct format...")
    nr_variants = 0
    previous_pos = None
    previous_chrom = None
    
    posititon_variants = set()
    
    for variant_line in variants:
        variant_line = variant_line.rstrip()
        if variant_line.startswith('#'):
            pass
        else:
            nr_variants += 1
            
            splitted_line = variant_line.split('\t')
            current_chrom = splitted_line[0]
            current_pos = int(splitted_line[1])
            
            variant_id = '_'.join([
                    splitted_line[0],
                    splitted_line[1],
                    splitted_line[3],
                    splitted_line[4]
                ]
            )
            
            if previous_chrom:
                if current_chrom != previous_chrom:
                    previous_chrom = current_chrom
                    previous_pos = current_pos
                    posititon_variants = set([variant_id])
                else:
                    if current_pos == previous_pos:
                        if variant_id in posititon_variants:
                            raise VcfError("Variant {0} occurs several times"\
                                           " in vcf".format(variant_id))
                        else:
                            posititon_variants.add(variant_id)
                    else:
                        if not current_pos > previous_pos:
                            raise VcfError("Vcf if not sorted in a correct way")
                        previous_pos = current_pos
                        posititon_variants = set([variant_id])
            else:
                previous_chrom = current_chrom
                previous_pos = current_pos
                posititon_variants = set([variant_id])

    return nr_variants

    
    