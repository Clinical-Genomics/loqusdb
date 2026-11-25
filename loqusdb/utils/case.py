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
    variant_files = [
        ("snv", "vcf_path", "nr_variants", "individuals", "_inds"),
        ("sv", "vcf_sv_path", "nr_sv_variants", "sv_individuals", "_sv_inds"),
        ("mei", "vcf_mei_path", "nr_mei_variants", "mei_individuals", "_mei_inds"),
    ]

    updated_case = deepcopy(existing_case)

    for variant_type, file_name, nr_variants_key, individuals_key, inds_key in variant_files:
        if case_obj.get(file_name):
            if updated_case.get(file_name):
                LOG.warning("VCF of type %s already exists in case", variant_type)
                raise CaseError("Can not replace VCF in existing case")
            else:
                updated_case[file_name] = case_obj[file_name]
                updated_case[nr_variants_key] = case_obj[nr_variants_key]
                updated_case[individuals_key] = case_obj[individuals_key]
                updated_case[inds_key] = case_obj[inds_key]

    return updated_case
