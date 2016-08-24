import os

from cyvcf2 import VCF

VALID_ENDINGS = ['.vcf', '.bcf', '.gz']

def get_vcf(file_path):
    """Return a cyvcf2 vcf file object"""
    if not os.path.exists(file_path):
        raise IOError("No such file:{0}".format(file_path))
    
    if not os.path.splitext(file_path)[-1] in VALID_ENDINGS:
        raise IOError("Not a valid vcf file name: {}".format(file_path))

    return VCF(file_path)