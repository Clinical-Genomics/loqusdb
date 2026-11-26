# -*- coding: utf-8 -*-
import logging

import click
from loqusdb.exceptions import CaseError
from loqusdb.utils.case import get_case
from loqusdb.utils.delete import delete as delete_command

from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("delete", short_help="Delete the variants of a family")
@click.option("-f", "--family-file", type=click.Path(exists=True), metavar="<ped_file>")
@click.option(
    "-t",
    "--family-type",
    type=click.Choice(["ped", "alt", "cmms", "mip"]),
    default="ped",
    help="If the analysis use one of the known setups, please specify which one.",
)
@click.option(
    "-c",
    "--case-id",
    type=str,
    help="If a different case id than the one in ped file should be used",
)
@click.option(
    "--gq-threshold",
    type=click.IntRange(min=0),
    metavar="INTEGER",
    help="Replay the original small-variant GQ threshold. Omit it or use 0 for no threshold.",
)
@click.option("--qual-gq", is_flag=True, help="Use QUAL instead of GQ, as in the original load.")
@click.option(
    "--ignore-gq-if-unset",
    is_flag=True,
    help="Accept missing GQ or QUAL, as in the original load.",
)
@click.pass_context
def delete(ctx, family_file, family_type, case_id, gq_threshold, qual_gq, ignore_gq_if_unset):
    """Delete the variants of a case."""
    if not (family_file or case_id):
        LOG.error("Please provide a family file")
        ctx.abort()

    adapter = ctx.obj["adapter"]
    keep_chr_prefix = ctx.obj["keep_chr_prefix"]

    # Get a ped_parser.Family object from family file
    family = None
    family_id = None
    if family_file:
        with open(family_file, "r") as family_lines:
            family = get_case(family_lines=family_lines, family_type=family_type)
            family_id = family.family_id

    # There has to be a case_id or a family at this stage.
    case_id = case_id or family_id

    if not case_id:
        LOG.warning("Please provide a case id")
        ctx.abort()

    existing_case = adapter.case({"case_id": case_id})
    if not existing_case:
        LOG.warning("Case %s does not exist in database" % case_id)
        return

    genome_build = ctx.obj["genome_build"]
    try:
        delete_command(
            adapter=adapter,
            case_obj=existing_case,
            genome_build=genome_build,
            keep_chr_prefix=keep_chr_prefix,
            gq_threshold=gq_threshold,
            qual_gq=qual_gq,
            ignore_gq_if_unset=ignore_gq_if_unset,
        )
    except (CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()
