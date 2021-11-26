import logging
import os
from datetime import datetime

import click
from loqusdb.utils.annotate import annotate_snvs, annotate_svs
from loqusdb.utils.vcf import add_headers, get_file_handle
from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("annotate", short_help="Annotate a VCF with observations")
@click.argument(
    "variant-file",
    type=click.Path(exists=True),
    metavar="<vcf_file>",
)
@click.option("--sv", is_flag=True)
@click.pass_context
def annotate(ctx, variant_file, sv):
    """Annotate the variants in a VCF"""
    adapter = ctx.obj["adapter"]

    variant_path = os.path.abspath(variant_file)

    expected_type = "sv" if sv else "snv"

    nr_cases = adapter.nr_cases(sv_cases=True)
    LOG.info("Found {0} {1} cases in database".format(nr_cases, expected_type))

    vcf_obj = get_file_handle(variant_path)
    add_headers(vcf_obj, nr_cases=nr_cases, sv=sv)
    # Print the headers
    for header_line in vcf_obj.raw_header.split("\n"):
        if len(header_line) == 0:
            continue
        click.echo(header_line)

    start_inserting = datetime.now()

    if sv:
        annotated_variants = annotate_svs(adapter, vcf_obj)
    else:
        annotated_variants = annotate_snvs(adapter, vcf_obj)
    # try:
    for variant in annotated_variants:
        click.echo(str(variant).rstrip())
