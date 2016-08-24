from cyvcf2 import VCF

def get_vcf(file_path):
    """Return a cyvcf2 vcf file object"""
    #Might do some sanity checks here?
    return VCF(file_path)