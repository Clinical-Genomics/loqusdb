import logging
from copy import deepcopy

from loqusdb.exceptions import CaseError
from ped_parser import FamilyParser

LOG = logging.getLogger(__name__)


def get_case(family_lines, family_type="ped", vcf_path=None):
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
    LOG.info("Parsing family information")

    family_parser = FamilyParser(family_lines, family_type)

    families = list(family_parser.families.keys())

    LOG.info("Found families {0}".format(", ".join(families)))

    if len(families) > 1:
        raise CaseError("Only one family per load can be used")

    family = family_parser.families[families[0]]

    return family


def update_case(case_obj, existing_case):
    """Update an existing case

    This will add paths to VCF files, individuals etc

    Args:
        case_obj(models.Case)
        existing_case(models.Case)

    Returns:
        updated_case(models.Case): Updated existing case
    """
    variant_nrs = ["nr_variants", "nr_sv_variants"]
    individuals = [("individuals", "_inds"), ("sv_individuals", "_sv_inds")]

    updated_case = deepcopy(existing_case)

    for i, file_name in enumerate(["vcf_path", "vcf_sv_path"]):
        variant_type = "snv"
        if file_name == "vcf_sv_path":
            variant_type = "sv"
        if case_obj.get(file_name):
            if updated_case.get(file_name):
                LOG.warning("VCF of type %s already exists in case", variant_type)
                raise CaseError("Can not replace VCF in existing case")
            else:
                updated_case[file_name] = case_obj[file_name]
                updated_case[variant_nrs[i]] = case_obj[variant_nrs[i]]
                updated_case[individuals[i][0]] = case_obj[individuals[i][0]]
                updated_case[individuals[i][1]] = case_obj[individuals[i][1]]

    return updated_case
