import logging

from ped_parser import FamilyParser

from loqusdb.exceptions import CaseError

LOG = logging.getLogger(__name__)

def get_case(family_lines, family_type='ped', vcf_path=None):
    """Return ped_parser case from a family file
    
    Create a dictionary with case data. If no family file is given create from VCF
    
    Args:
        family_lines (iterator): The family lines
        family_type (str): The format of the family lines
        vcf_path(str): Path to VCF
    
    Returns:
        family (Family): A ped_parser family object
    """
    family = None
    logger.info("Parsing family information")
    
    family_parser = FamilyParser(family_lines, family_type)
    
    families = list(family_parser.families.keys())
    
    logger.info("Found families {0}".format(', '.join(families)))
    
    if len(families) > 1:
        raise CaseError("Only one family per load can be used")
    
    family = family_parser.families[families[0]]
    
    return family
