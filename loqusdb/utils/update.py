# -*- coding: utf-8 -*-
"""
loqusdb.utils.update.py

Functions to update data into the database.
This functions take an adapter which is the communication device for the database.

"""

import logging


from loqusdb.exceptions import CaseError

from loqusdb.utils.case import get_case
from loqusdb.utils.delete import delete
from loqusdb.utils.load import load_case, load_variants
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
    genome_build=None,
    keep_chr_prefix=False,
    add_to_existing_snv=False,
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
          genome_build(str): Genome version
          keep_chr_prefix(bool): Retain chr/CHR/Chr prefixes when present
          add_to_existing_snv(bool): Add SNVs without replacing the case's stored SNV VCF

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
    )

    existing_case = adapter.case(case_obj)
    if not existing_case:
        raise CaseError("Case {} does not exist in database".format(case_obj["case_id"]))

    if add_to_existing_snv:
        if not existing_case.get("vcf_path"):
            raise CaseError(
                "Case {0} does not have an existing SNV VCF".format(case_obj["case_id"])
            )

        nr_inserted = load_variants(
            adapter=adapter,
            vcf_obj=get_vcf(variant_file),
            case_obj=case_obj,
            skip_case_id=skip_case_id,
            gq_threshold=gq_threshold,
            keep_chr_prefix=keep_chr_prefix,
            genome_build=genome_build,
            variant_type="snv",
            skip_existing_case=True,
        )
        existing_case["nr_variants"] = existing_case.get("nr_variants") or 0
        existing_case["nr_variants"] += nr_inserted
        adapter.add_case(existing_case, update=True)
        return nr_inserted

    # Update the existing case in database
    case_obj = load_case(
        adapter=adapter,
        case_obj=case_obj,
        update=True,
    )

    nr_inserted = 0
    # If case was succesfully added we can store the variants
    for file_type in ["vcf_path", "vcf_sv_path"]:
        variant_type = "snv"
        if file_type == "vcf_sv_path":
            variant_type = "sv"
        if case_obj.get(file_type) is None:
            continue

        vcf_obj = get_vcf(case_obj[file_type])
        try:
            nr_inserted += load_variants(
                adapter=adapter,
                vcf_obj=vcf_obj,
                case_obj=case_obj,
                skip_case_id=skip_case_id,
                gq_threshold=gq_threshold,
                keep_chr_prefix=keep_chr_prefix,
                genome_build=genome_build,
                max_window=max_window,
                variant_type=variant_type,
            )
        except Exception as err:
            # If something went wrong do a rollback
            LOG.warning(err)
            delete(
                adapter=adapter,
                case_obj=case_obj,
                update=True,
                existing_case=existing_case,
            )
            raise err
    return nr_inserted
