# -*- coding: utf-8 -*-
import logging
from datetime import datetime


from loqusdb.utils.vcf import get_vcf
from loqusdb.build_models.variant import build_variant

LOG = logging.getLogger(__name__)


def delete(
    adapter, case_obj, keep_chr_prefix=None, update=False, existing_case=False, genome_build=None
):
    """Delete a case and all of it's variants from the database.

    Args:
        adapter: Connection to database
        case_obj(models.Case)
        update(bool): If we are in the middle of an update
        existing_case(models.Case): If something failed during an update we need to revert
                                    to the original case
        keep_chr_prefix(bool): Retain chr/CHR/Chr prefixes in chromosome IDs when they are present
        genome_build(str): Genome build. Ex. GRCh37 or GRCh38

    """
    # This will overwrite the updated case with the previous one
    if update:
        adapter.add_case(existing_case)
    else:
        adapter.delete_case(case_obj)

    for file_type in ["vcf_path", "vcf_sv_path"]:
        if not case_obj.get(file_type):
            continue
        variant_file = case_obj[file_type]
        # Get a cyvcf2.VCF object
        vcf_obj = get_vcf(variant_file)

        if file_type == "vcf_path":
            LOG.info("deleting variants")
            delete_variants(
                adapter=adapter,
                vcf_obj=vcf_obj,
                keep_chr_prefix=keep_chr_prefix,
                case_obj=case_obj,
                genome_build=genome_build,
            )
        elif file_type == "vcf_sv_path":
            LOG.info("deleting structural variants")
            delete_structural_variants(
                adapter=adapter,
                vcf_obj=vcf_obj,
                case_obj=case_obj,
                keep_chr_prefix=keep_chr_prefix,
                genome_build=genome_build,
            )


def delete_variants(
    adapter, vcf_obj, case_obj, keep_chr_prefix=None, case_id=None, genome_build=None
):
    """Delete variants for a case in the database

    Args:
        adapter(loqusdb.plugins.Adapter)
        vcf_obj(iterable(dict))
        ind_positions(dict)
        case_id(str)
        genome_build(str): Genome build. Ex. GRCh37 or GRCh38

    Returns:
        nr_deleted (int): Number of deleted variants
    """
    case_id = case_id or case_obj["case_id"]
    nr_deleted = 0
    start_deleting = datetime.now()
    chrom_time = datetime.now()
    current_chrom = None
    new_chrom = None

    variant_list = []
    for variant in vcf_obj:
        formated_variant = build_variant(
            variant=variant,
            case_obj=case_obj,
            keep_chr_prefix=keep_chr_prefix,
            case_id=case_id,
            genome_build=genome_build,
        )

        if not formated_variant:
            continue

        variant_list.append(formated_variant)

        new_chrom = formated_variant.get("chrom")
        # When there are enough variants in the variant list
        # They are passed to delete_variants
        if len(variant_list) == 10000:
            adapter.delete_variants(variant_list)
            variant_list.clear()

        nr_deleted += 1

        if not current_chrom:
            LOG.info("Start deleting chromosome {}".format(new_chrom))
            current_chrom = new_chrom
            chrom_time = datetime.now()
            continue

        if new_chrom != current_chrom:
            LOG.info("Chromosome {0} done".format(current_chrom))
            LOG.info(
                "Time to delete chromosome {0}: {1}".format(
                    current_chrom, datetime.now() - chrom_time
                )
            )
            LOG.info("Start deleting chromosome {0}".format(new_chrom))
            current_chrom = new_chrom

    if variant_list:
        adapter.delete_variants(variant_list)
        variant_list.clear()

    return nr_deleted


def delete_structural_variants(
    adapter, vcf_obj, case_obj, genome_build, keep_chr_prefix=None, case_id=None
):
    """Delete structural variants for a case in the database

    Args:
        adapter(loqusdb.plugins.Adapter)
        vcf_obj(iterable(dict))
        ind_positions(dict)
        case_id(str)
        genome_build(str): Genome build. Ex. GRCh37 or GRCh38

    Returns:
        nr_deleted (int): Number of deleted variants"""

    case_id = case_id or case_obj["case_id"]
    nr_deleted = 0
    start_deleting = datetime.now()
    chrom_time = datetime.now()
    current_chrom = None
    new_chrom = None

    for variant in vcf_obj:
        formated_variant = build_variant(
            variant=variant,
            case_obj=case_obj,
            case_id=case_id,
            genome_build=genome_build,
            keep_chr_prefix=keep_chr_prefix,
        )

        if not formated_variant:
            continue

        new_chrom = formated_variant.get("chrom")
        adapter.delete_structural_variant(formated_variant)
        nr_deleted += 1

        if not current_chrom:
            LOG.info("Start deleting chromosome {}".format(new_chrom))
            current_chrom = new_chrom
            chrom_time = datetime.now()
            continue

        if new_chrom != current_chrom:
            LOG.info("Chromosome {0} done".format(current_chrom))
            LOG.info(
                "Time to delete chromosome {0}: {1}".format(
                    current_chrom, datetime.now() - chrom_time
                )
            )
            LOG.info("Start deleting chromosome {0}".format(new_chrom))
            current_chrom = new_chrom

    return nr_deleted
