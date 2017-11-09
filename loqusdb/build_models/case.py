import logging

from loqusdb.models import (Case, Individual)
from loqusdb.exceptions import CaseError

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

    family_id = None
    if case:
        if not case.affected_individuals:
            LOG.warning("No affected individuals could be found in ped file")
        family_id = case.family_id

    case_id = case_id or family_id

    case_obj = Case(
        case_id=case_id, 
        vcf_path=vcf_path, 
        vcfsv_path=None, 
        nr_variants=nr_variants
    )

    ind_objs = []
    if case:
        for ind_id in case.individuals:
            individual = case.individuals[ind_id]
            try:
                ind_obj = Individual(
                    ind_id=ind_id,
                    case_id=case_id,
                    ind_index=individual_positions[ind_id],
                    sex=individual.sex,
                )
                ind_objs.append(ind_obj)
            except KeyError:
                raise CaseError("Ind %s in ped file does not exist in VCF", ind_id)
    else:
        for ind_id in individual_positions:
            ind_obj = Individual(
                ind_id = ind_id,
                case_id = case_id,
                ind_index=individual_positions[ind_id],
            )
            ind_objs.append(ind_obj)
    
    for ind_obj in ind_objs:
        case_obj.add_individual(ind_obj)

    return case_obj