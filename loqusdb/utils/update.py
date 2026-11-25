# -*- coding: utf-8 -*-
"""
loqusdb.utils.update.py

Functions to update data into the database.
This functions take an adapter which is the communication device for the database.

"""

import logging
from copy import deepcopy


from loqusdb.exceptions import CaseError

from loqusdb.utils.case import get_case
from loqusdb.utils.delete import delete
from loqusdb.constants import MEI_WINDOW
from loqusdb.utils.load import VARIANT_FILE_TYPES, load_case, load_variants
from loqusdb.utils.vcf import check_vcf, get_vcf
from loqusdb.build_models.case import build_case

LOG = logging.getLogger(__name__)


def update_database(
    adapter,
    variant_file=None,
    sv_file=None,
    family_file=None,
    family_type="ped",
    skip_case_id=False,
    gq_threshold=None,
    case_id=None,
    max_window=3000,
    mei_file=None,
    mei_window=MEI_WINDOW,
    keep_chr_prefix=False,
    genome_build=None,
):
    """Update a case in the database

    Args:
          adapter: Connection to database
          variant_file(str): Path to variant file
          sv_file(str): Path to sv variant file
          family_file(str): Path to family file
          family_type(str): Format of family file
          skip_case_id(bool): If no case information should be added to variants
          gq_threshold(int): If only quality variants should be considered
          case_id(str): If different case id than the one in family file should be used
          max_window(int): Specify the max size for sv windows
          mei_file(str): Path to mobile element insertion variant file
          mei_window(int): Distance from cluster mean within which MEIs are merged
          keep_chr_prefix(bool): Retain chr/CHR/Chr prefix when present
          genome_build(str): Genome build. Ex. GRCh37 or GRCh38

    Returns:
          nr_inserted(int)
    """
    vcf_files = []
    nr_variants = None
    vcf_individuals = None
    if variant_file:
        vcf_info = check_vcf(variant_file, keep_chr_prefix)
        nr_variants = vcf_info["nr_variants"]
        variant_type = vcf_info["variant_type"]
        vcf_files.append(variant_file)
        # Get the indivuduals that are present in vcf file
        vcf_individuals = vcf_info["individuals"]

    nr_sv_variants = None
    sv_individuals = None
    if sv_file:
        vcf_info = check_vcf(sv_file, keep_chr_prefix, "sv")
        nr_sv_variants = vcf_info["nr_variants"]
        vcf_files.append(sv_file)
        sv_individuals = vcf_info["individuals"]

    nr_mei_variants = None
    mei_individuals = None
    if mei_file:
        vcf_info = check_vcf(mei_file, keep_chr_prefix, "sv")
        nr_mei_variants = vcf_info["nr_variants"]
        vcf_files.append(mei_file)
        mei_individuals = vcf_info["individuals"]

    # If a gq threshold is used the variants needs to have GQ
    for _vcf_file in vcf_files:
        # Get a cyvcf2.VCF object
        vcf = get_vcf(_vcf_file)

        if gq_threshold:
            if not vcf.contains("GQ"):
                LOG.warning("Set gq-threshold to 0 or add info to vcf {0}".format(_vcf_file))
                raise SyntaxError("GQ is not defined in vcf header")

    # Get a ped_parser.Family object from family file
    family = None
    family_id = None
    if family_file:
        with open(family_file, "r") as family_lines:
            family = get_case(family_lines=family_lines, family_type=family_type)
            family_id = family.family_id

    # There has to be a case_id or a family at this stage.
    case_id = case_id or family_id

    # Convert infromation to a loqusdb Case object
    case_obj = build_case(
        case=family,
        case_id=case_id,
        vcf_path=variant_file,
        vcf_individuals=vcf_individuals,
        nr_variants=nr_variants,
        vcf_sv_path=sv_file,
        sv_individuals=sv_individuals,
        nr_sv_variants=nr_sv_variants,
        vcf_mei_path=mei_file,
        mei_individuals=mei_individuals,
        nr_mei_variants=nr_mei_variants,
    )

    existing_case = adapter.case(case_obj)
    if not existing_case:
        raise CaseError("Case {} does not exist in database".format(case_obj["case_id"]))

    # Update the existing case in database
    case_obj = load_case(
        adapter=adapter,
        case_obj=case_obj,
        update=True,
    )

    nr_inserted = 0
    # If case was succesfully added we can store the variants
    for file_type, variant_type in VARIANT_FILE_TYPES:
        # Only load the variant files that are new to the case
        if case_obj.get(file_type) is None or existing_case.get(file_type):
            continue

        vcf_obj = get_vcf(case_obj[file_type])
        try:
            nr_inserted += load_variants(
                adapter=adapter,
                vcf_obj=vcf_obj,
                case_obj=case_obj,
                skip_case_id=skip_case_id,
                gq_threshold=gq_threshold,
                max_window=max_window,
                variant_type=variant_type,
                keep_chr_prefix=keep_chr_prefix,
                genome_build=genome_build,
                mei_window=mei_window,
            )
        except Exception as err:
            # If something went wrong do a rollback of the new variant file(s)
            LOG.warning(err)
            new_files_case = deepcopy(case_obj)
            for rollback_file_type, _ in VARIANT_FILE_TYPES:
                if existing_case.get(rollback_file_type):
                    new_files_case.pop(rollback_file_type, None)
            delete(
                adapter=adapter,
                case_obj=new_files_case,
                update=True,
                existing_case=existing_case,
                keep_chr_prefix=keep_chr_prefix,
                genome_build=genome_build,
                mei_window=mei_window,
            )
            raise err
    return nr_inserted
