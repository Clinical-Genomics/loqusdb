import logging

from loqusdb.models import (Case, Individual)

LOG = logging.getLogger(__name__)

def build_case(case, vcf_individuals, case_id=None, vcf_path=None, sv_individuals=None, nr_variants=None):
    """Build a Case from the given information
    
    Args:
        case(ped_parser.Family): A family object
        case_id(str): If another name than the one in family file should be used
        vcf_individuals(list): Show the order of inds in vcf file
        sv_individuals(list): Show the order of inds in sv vcf file
    """
    individual_positions = {}
    for i, ind in enumerate(vcf_individuals):
        individual_positions[ind] = i

    if not case.affected_individuals:
        LOG.warning("No affected individuals could be found in ped file")

    case_id = case_id or case.family_id

    case_obj = Case(
        case_id=case_id, 
        vcf_path=vcf_path, 
        vcfsv_path=None, 
        nr_variants=nr_variants
    )

    for ind_id in case.individuals:
        individual = case.individuals[ind_id]
        try:
            ind_obj = Individual(
                ind_id=ind_id,
                case_id=case_id,
                mother=individual.mother,
                father=individual.father,
                sex=individual.sex,
                phenotype=individual.phenotype,
                ind_index=individual_positions[ind_id],
            )
            case_obj.add_individual(ind_obj)
        except KeyError:
            raise CaseError("Ind %s in ped file does not exist in VCF", ind_id)

    return case_obj