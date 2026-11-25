import logging
import os
from datetime import datetime

import click
from loqusdb.utils.annotate import annotate_meis, annotate_snvs, annotate_svs
from loqusdb.utils.vcf import add_headers, get_file_handle
from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("annotate", short_help="Annotate a VCF with observations")
@click.argument(
    "variant-file",
    type=click.Path(exists=True),
    metavar="<vcf_file>",
)
@click.option("--sv", is_flag=True, help="Annotate a VCF with structural variants")
@click.option("--mei", is_flag=True, help="Annotate a VCF with mobile element insertions")
@click.pass_context
def annotate(ctx, variant_file, sv, mei):
    """Annotate the variants in a VCF"""
    adapter = ctx.obj["adapter"]
    keep_chr_prefix = ctx.obj["keep_chr_prefix"]

    if sv and mei:
        LOG.warning("Please choose one of --sv and --mei")
        ctx.abort()

    variant_path = os.path.abspath(variant_file)

    expected_type = "mei" if mei else "sv" if sv else "snv"

    nr_cases = adapter.nr_cases(
        snv_cases=expected_type == "snv",
        sv_cases=expected_type == "sv",
        mei_cases=expected_type == "mei",
    )
    LOG.info("Found {0} {1} cases in database".format(nr_cases, expected_type))

    vcf_obj = get_file_handle(variant_path)
    add_headers(vcf_obj, nr_cases=nr_cases, sv=sv or mei)
    # Print the headers
    for header_line in vcf_obj.raw_header.split("\n"):
        if len(header_line) == 0:
            continue
        click.echo(header_line)

    start_inserting = datetime.now()

    if mei:
        annotated_variants = annotate_meis(adapter, vcf_obj, keep_chr_prefix)
    elif sv:
        annotated_variants = annotate_svs(
            adapter, vcf_obj, keep_chr_prefix, genome_build=ctx.obj["genome_build"]
        )
    else:
        annotated_variants = annotate_snvs(adapter, vcf_obj, keep_chr_prefix)
    # try:
    for variant in annotated_variants:
        click.echo(str(variant).rstrip())
