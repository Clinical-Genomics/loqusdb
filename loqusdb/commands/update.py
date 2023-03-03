import logging
import os
from datetime import datetime

import click
from loqusdb.exceptions import CaseError, VcfError
from loqusdb.utils.update import update_database

from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("update", short_help="Update an existing case with a new type of variants")
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
    "--max-window",
    "-m",
    default=2000,
    show_default=True,
    help="Specify the maximum window size for svs",
)
@click.pass_context
def update(
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

    adapter = ctx.obj["adapter"]

    start_inserting = datetime.now()

    try:
        nr_inserted = update_database(
            adapter=adapter,
            variant_file=variant_path,
            sv_file=variant_sv_path,
            family_file=family_file,
            family_type=family_type,
            skip_case_id=skip_case_id,
            case_id=case_id,
            gq_threshold=gq_threshold,
            max_window=max_window,
        )
    except (SyntaxError, CaseError, IOError, VcfError) as error:
        LOG.warning(error)
        ctx.abort()

    LOG.info("Nr variants inserted: %s", nr_inserted)
    LOG.info("Time to insert variants: {0}".format(datetime.now() - start_inserting))

    if ensure_index:
        adapter.ensure_indexes()
    else:
        adapter.check_indexes()
