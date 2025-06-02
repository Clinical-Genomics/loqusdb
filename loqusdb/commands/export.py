import logging
from datetime import datetime

import click
from loqusdb.constants import CHROMOSOMES, GRCH37, GRCH38
from loqusdb.utils.variant import format_variant
from vcftoolbox import HeaderParser, print_headers, print_variant

from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("export", short_help="Export variants to VCF format")
@click.option(
    "-o",
    "--outfile",
    type=click.File("w"),
    help="Specify the path to a file where results should be stored.",
)
@click.option(
    "-t",
    "--variant-type",
    type=click.Choice(["sv", "snv"]),
    default="snv",
    show_default=True,
    help="If svs or snvs should be exported",
)
@click.option(
    "-f", "--freq", is_flag=True, help="Include observation frequencies in the exported VCF"
)
@click.pass_context
def export(ctx, outfile, variant_type, freq):
    """Export the variants of a loqus db

    The variants are exported to a vcf file
    """
    adapter = ctx.obj["adapter"]
    version = ctx.obj["version"]

    LOG.info("Export the variants from {0}".format(adapter))

    is_sv = variant_type == "sv"
    existing_chromosomes = set(adapter.get_chromosomes(sv=is_sv))

    genome = ctx.obj["genome_build"]
    chromosome_order = CHROMOSOMES[genome]
    keep_chr_prefix = ctx.obj["keep_chr_prefix"]

    ordered_chromosomes = []
    for chrom in chromosome_order:
        if keep_chr_prefix and chrom in existing_chromosomes:
            ordered_chromosomes.append(chrom)
            existing_chromosomes.remove(chrom)
        elif not keep_chr_prefix:
            if genome == GRCH37 and chrom in existing_chromosomes:
                ordered_chromosomes.append(chrom)
                existing_chromosomes.remove(chrom)
            elif genome == GRCH38 and chrom[3:] in existing_chromosomes:
                ordered_chromosomes.append(chrom)
                existing_chromosomes.remove(chrom)
    for chrom in existing_chromosomes:
        ordered_chromosomes.append(chrom)

    if variant_type == "snv":
        nr_cases = adapter.nr_cases(snv_cases=True)
    elif variant_type == "sv":
        nr_cases = adapter.nr_cases(sv_cases=True)
    else:
        raise ValueError(f"Unknown variant_type: {variant_type}, expected 'snv' or 'sv'")

    LOG.info(f"Found {nr_cases} cases in database")

    head = HeaderParser()
    head.add_fileformat("VCFv4.3")
    head.add_meta_line("NrCases", nr_cases)
    if freq:
        head.add_info(
            "Frq",
            "1",
            "Float",
            f"Observation frequency of the variant (not allele frequency) based on {nr_cases} cases",
        )
    head.add_info("Obs", "1", "Integer", "The number of observations for the variant")
    head.add_info("Hom", "1", "Integer", "The number of observed homozygotes")
    head.add_info("Hem", "1", "Integer", "The number of observed hemizygotes")
    head.add_version_tracking("loqusdb", version, datetime.now().strftime("%Y-%m-%d %H:%M"))

    if variant_type == "sv":
        head.add_info("END", "1", "Integer", "End position of the variant")
        head.add_info("SVTYPE", "1", "String", "Type of structural variant")
        head.add_info("SVLEN", "1", "Integer", "Length of structural variant")

    for chrom in ordered_chromosomes:
        length = adapter.get_max_position(chrom)
        head.add_contig(contig_id=chrom, length=str(length))

    print_headers(head, outfile=outfile)

    for chrom in ordered_chromosomes:
        if variant_type == "snv":
            LOG.info("Collecting all SNV variants")
            variants = adapter.get_variants(chromosome=chrom)
        else:
            LOG.info("Collecting all SV variants")
            variants = adapter.get_sv_variants(chromosome=chrom)
        LOG.info(f"{adapter.nr_variants(chromosome=chrom)} variants found")
        for variant in variants:
            variant_line = format_variant(
                variant, variant_type=variant_type, nr_cases=nr_cases, add_freq=freq
            )
            print_variant(variant_line=variant_line, outfile=outfile)
