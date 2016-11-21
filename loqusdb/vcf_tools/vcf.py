import os

from codecs import open
import gzip

VALID_ENDINGS = ['.vcf', '.gz']

def get_file_handle(file_path):
    """Return a opened file"""
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
