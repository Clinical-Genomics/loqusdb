import logging

from loqusdb.models import (Case, Individual)

LOG = logging.getLogger(__name__)

def build_case(case, case_id=None, vcf_path=None, vcf_individuals=None, sv_individuals=None, nr_variants=None):
    """Build a Case from the given information
    
    Args:
        case(ped_parser.Family): A family object
        case_id(str): If another name than the one in family file should be used
        vcf_individuals(list): Show the order of inds in vcf file
        sv_individuals(list): Show the order of inds in sv vcf file
    """

    if not family.affected_individuals:
        LOG.warning("No affected individuals could be found in ped file")

    case_id = case_id or family.family_id
    
    case_obj = Case(
        case_id=case_id, 
        vcf_path=vcf_path, 
        vcfsv_path=None, 
        nr_variants=nr_variants
    )
    
    for ind_id in family.individuals:
        individual = family.individuals[ind_id]
        ind_obj = Individual(
            ind_id=ind_id,
            case_id=case_id,
            mother=individual.mother,
            father=individual.father,
            sex=individual.sex,
            phenotype=individual.phenotype,
        )
        case_obj.add_individual(ind_obj)
    
    return case_obj