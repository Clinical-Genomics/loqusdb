from . import GRCH37

global GENOME_BUILD 
GENOME_BUILD = GRCH37

def set_genome_build(genome_build):
    """Set global genome build"""
    if genome_build is not None:
        global GENOME_BUILD
        GENOME_BUILD = genome_build
