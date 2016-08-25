import logging

from ped_parser import FamilyParser

from loqusdb.exceptions import CaseError

logger = logging.getLogger(__name__)

def get_family(family_lines, family_type='ped'):
    """Return the families found in  a family file
    
        Args:
            family_lines (iterator): The family lines
            family_type (str): The format of the family lines
        
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
