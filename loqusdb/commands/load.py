import logging
import os
from datetime import datetime

import click

from loqusdb.commands.cli import cli as base_command
from loqusdb.exceptions import CaseError
from loqusdb.utils.load import load_database

LOG = logging.getLogger(__name__)


def validate_profile_threshold(ctx, param, value):
    if not (0 <= value <= 1):
        raise ValueError("threshold must be between 0-1")

    return value


@base_command.command("load", short_help="Load the variants of a family")
@click.option(
    "--variant-file",
    type=click.Path(exists=True),
    metavar="<vcf_file>",
    help="Load a VCF with SNV/INDEL Variants",
)
@click.option(
    "--sv-variants",
    type=click.Path(exists=True),
    metavar="<sv_vcf_file>",
    help="Load a VCF with Structural Variants",
)
@click.option("-f", "--family-file", type=click.Path(exists=True), metavar="<ped_file>")
@click.option(
    "-t",
    "--family-type",
    type=click.Choice(["ped", "alt", "cmms", "mip"]),
    default="ped",
    show_default=True,
    help="If the analysis use one of the known setups, please specify which one.",
)
@click.option(
    "-c",
    "--case-id",
    type=str,
    help="If a different case id than the one in ped file should be used",
)
@click.option(
    "-s",
    "--skip-case-id",
    is_flag=True,
    show_default=True,
    help="Do not store case information on variants",
)
@click.option("--ensure-index", is_flag=True, help="Make sure that the indexes are in place")
@click.option("--gq-threshold", default=20, show_default=True, help="Threshold to consider variant")
@click.option(
    "--qual-gq",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use QUAL tag instead of GQ value for quality filter",
)
@click.option(
    "--max-window",
    "-m",
    default=2000,
    show_default=True,
    help="Specify the maximum window size for svs",
)
@click.option(
    "--check-profile",
    type=click.Path(exists=True),
    help="Apply sample profiling for the samples, using the variants in this vcf",
)
@click.option(
    "--hard-threshold",
    type=float,
    default=0.95,
    callback=validate_profile_threshold,
    help="profile hamming distance to rejecting load (0-1)",
)
@click.option(
    "--soft-threshold",
    type=float,
    default=0.95,
    callback=validate_profile_threshold,
    help="profile hamming distance to store similar individuals (0-1)",
)
@click.option(
    "--snv-gq-only",
    is_flag=True,
    default=False,
    show_default=True,
    help="Apply GQ threshold only to SNV variants",
)
@click.option(
    "--ignore-gq-if-unset",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore GQ threshold if GQ (or the QUAL field for --qual-gq) is unset in VCF",
)
@click.pass_context
def load(
    ctx,
    variant_file,
    sv_variants,
    family_file,
    family_type,
    skip_case_id,
    gq_threshold,
    case_id,
    ensure_index,
    max_window,
    check_profile,
    hard_threshold,
    soft_threshold,
    qual_gq,
    snv_gq_only,
    ignore_gq_if_unset,
):
    """Load the variants of a case

    A variant is loaded if it is observed in any individual of a case
    If no family file is provided all individuals in vcf file will be considered.
    """
    if not (family_file or case_id):
        LOG.warning("Please provide a family file or a case id")
        ctx.abort()

    if not (variant_file or sv_variants):
        LOG.warning("Please provide a VCF file")
        ctx.abort()

    variant_path = None
    if variant_file:
        variant_path = os.path.abspath(variant_file)

    variant_sv_path = None
    if sv_variants:
        variant_sv_path = os.path.abspath(sv_variants)

    variant_profile_path = None
    if check_profile:
        variant_profile_path = os.path.abspath(check_profile)

    adapter = ctx.obj["adapter"]
    genome_build = ctx.obj["genome_build"]
    keep_chr_prefix = ctx.obj["keep_chr_prefix"]
    start_inserting = datetime.now()

    try:
        nr_inserted = load_database(
            adapter=adapter,
            variant_file=variant_path,
            sv_file=variant_sv_path,
            family_file=family_file,
            family_type=family_type,
            skip_case_id=skip_case_id,
            case_id=case_id,
            gq_threshold=gq_threshold,
            snv_gq_only=snv_gq_only,
            keep_chr_prefix=keep_chr_prefix,
            qual_gq=qual_gq,
            max_window=max_window,
            profile_file=variant_profile_path,
            hard_threshold=hard_threshold,
            soft_threshold=soft_threshold,
            genome_build=genome_build,
            ignore_gq_if_unset=ignore_gq_if_unset,
        )
    except (SyntaxError, CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()

    LOG.info("Nr variants inserted: %s", nr_inserted)
    LOG.info("Time to insert variants: {0}".format(datetime.now() - start_inserting))

    if ensure_index:
        adapter.ensure_indexes()
    else:
        adapter.check_indexes()
