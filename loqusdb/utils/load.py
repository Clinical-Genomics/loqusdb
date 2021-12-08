# -*- coding: utf-8 -*-
"""
loqusdb.utils.load.py

Functions to load data into the database.
This functions take an adapter which is the communication device for the database.

"""

import logging

import click

from loqusdb.exceptions import CaseError, VcfError

from loqusdb.utils.case import get_case, update_case
from loqusdb.utils.delete import delete
from loqusdb.utils.profiling import get_profiles, profile_match
from loqusdb.utils.vcf import check_vcf, get_vcf
from loqusdb.build_models.case import build_case
from loqusdb.build_models.profile_variant import build_profile_variant
from loqusdb.build_models.variant import build_variant

LOG = logging.getLogger(__name__)


def load_database(
    adapter,
    variant_file=None,
    sv_file=None,
    family_file=None,
    family_type="ped",
    skip_case_id=False,
    gq_treshold=None,
    case_id=None,
    max_window=3000,
    profile_file=None,
    hard_threshold=0.95,
    soft_threshold=0.9,
    genome_build=None,
):
    """Load the database with a case and its variants

    Args:
          adapter: Connection to database
          variant_file(str): Path to variant file
          sv_file(str): Path to sv variant file
          family_file(str): Path to family file
          family_type(str): Format of family file
          skip_case_id(bool): If no case information should be added to variants
          gq_treshold(int): If only quality variants should be considered
          case_id(str): If different case id than the one in family file should be used
          max_window(int): Specify the max size for sv windows
          check_profile(bool): Does profile check if True
          hard_threshold(float): Rejects load if hamming distance above this is found
          soft_threshold(float): Stores similar samples if hamming distance above this is found

    Returns:
          nr_inserted(int)
    """
    vcf_files = []

    nr_variants = None
    vcf_individuals = None
    if variant_file:
        vcf_info = check_vcf(variant_file)
        nr_variants = vcf_info["nr_variants"]
        variant_type = vcf_info["variant_type"]
        vcf_files.append(variant_file)
        # Get the indivuduals that are present in vcf file
        vcf_individuals = vcf_info["individuals"]

    nr_sv_variants = None
    sv_individuals = None
    if sv_file:
        vcf_info = check_vcf(sv_file, "sv")
        nr_sv_variants = vcf_info["nr_variants"]
        vcf_files.append(sv_file)
        sv_individuals = vcf_info["individuals"]

    profiles = None
    matches = None
    if profile_file:
        profiles = get_profiles(adapter, profile_file)
        ###Check if any profile already exists
        matches = profile_match(
            adapter, profiles, hard_threshold=hard_threshold, soft_threshold=soft_threshold
        )

    # If a gq treshold is used the variants needs to have GQ
    for _vcf_file in vcf_files:
        # Get a cyvcf2.VCF object
        vcf = get_vcf(_vcf_file)

        if gq_treshold and not vcf.contains("GQ"):
            LOG.warning("Set gq-treshold to 0 or add info to vcf {0}".format(_vcf_file))
            raise SyntaxError("GQ is not defined in vcf header")

    # Get a ped_parser.Family object from family file
    family = None
    family_id = None
    if family_file:
        LOG.info("Loading family from %s", family_file)
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
        profiles=profiles,
        matches=matches,
        profile_path=profile_file,
    )
    # Build and load a new case, or update an existing one
    load_case(
        adapter=adapter,
        case_obj=case_obj,
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
                gq_treshold=gq_treshold,
                max_window=max_window,
                variant_type=variant_type,
                genome_build=genome_build,
            )
        except Exception as err:
            # If something went wrong do a rollback
            LOG.warning(err)
            delete(
                adapter=adapter,
                case_obj=case_obj,
            )
            raise err
    return nr_inserted


def load_case(adapter, case_obj, update=False):
    """Load a case to the database

    Args:
        adapter: Connection to database
        case_obj: dict
        update(bool): If existing case should be updated

    Returns:
        case_obj(models.Case)
    """
    # Check if the case already exists in database.
    existing_case = adapter.case(case_obj)
    if existing_case:
        if not update:
            raise CaseError("Case {0} already exists in database".format(case_obj["case_id"]))
        case_obj = update_case(case_obj, existing_case)

    # Add the case to database

    adapter.add_case(case_obj, update=update)

    return case_obj


def load_variants(
    adapter,
    vcf_obj,
    case_obj,
    skip_case_id=False,
    gq_treshold=None,
    max_window=3000,
    variant_type="snv",
    genome_build=None,
):
    """Load variants for a family into the database.

    Args:
        adapter (loqusdb.plugins.Adapter): initialized plugin
        case_obj(Case): dict with case information
        nr_variants(int)
        skip_case_id (bool): whether to include the case id on variant level
                             or not
        gq_treshold(int)
        max_window(int): Specify the max size for sv windows
        variant_type(str): 'sv' or 'snv'

    Returns:
        nr_inserted(int)
    """
    if variant_type == "snv":
        nr_variants = case_obj["nr_variants"]
    else:
        nr_variants = case_obj["nr_sv_variants"]

    nr_inserted = 0
    case_id = case_obj["case_id"]
    if skip_case_id:
        case_id = None
    # Loop over the variants in the vcf
    with click.progressbar(vcf_obj, label="Inserting variants", length=nr_variants) as bar:

        variants = (
            build_variant(variant, case_obj, case_id, gq_treshold, genome_build=genome_build)
            for variant in bar
        )

    if variant_type == "sv":
        for sv_variant in variants:
            if not sv_variant:
                continue
            adapter.add_structural_variant(variant=sv_variant, max_window=max_window)
            nr_inserted += 1

    if variant_type == "snv":
        nr_inserted = adapter.add_variants(variants)

    LOG.info("Inserted %s variants of type %s", nr_inserted, variant_type)

    return nr_inserted


def load_profile_variants(adapter, variant_file):
    """

    Loads variants used for profiling

    Args:
        adapter (loqusdb.plugins.Adapter): initialized plugin
        variant_file(str): Path to variant file


    """

    vcf_info = check_vcf(variant_file)
    nr_variants = vcf_info["nr_variants"]
    variant_type = vcf_info["variant_type"]

    if variant_type != "snv":
        LOG.critical("Variants used for profiling must be SNVs only")
        raise VcfError

    vcf = get_vcf(variant_file)

    profile_variants = [build_profile_variant(variant) for variant in vcf]
    adapter.add_profile_variants(profile_variants)
