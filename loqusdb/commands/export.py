import logging
import click
import tempfile

from datetime import datetime

from vcftoolbox import (HeaderParser, print_headers, print_variant)

from loqusdb import __version__, CHROMOSOME_ORDER

from . import base_command

logger = logging.getLogger(__name__)

@base_command.command('export', short_help="Export variants to VCF format")
@click.option('-o', '--outfile',
    type=click.File('w'),
    help='Specify the path to a file where results should be stored.'
)
@click.pass_context
def export(ctx, outfile):
    """Export the variants of a loqus db
        
        The variants are exported to a vcf file
    """
    adapter = ctx.obj['adapter']
    
    logger.info("Export the variants from {0}".format(adapter))
    nr_cases = 0
    
    existing_chromosomes = set(adapter.get_chromosomes())
    
    ordered_chromosomes = []
    for chrom in CHROMOSOME_ORDER:
        if chrom in existing_chromosomes:
            ordered_chromosomes.append(chrom)
            existing_chromosomes.remove(chrom)
    for chrom in existing_chromosomes:
        ordered_chromosomes.append(chrom)
    
    nr_cases = adapter.cases().count()
    logger.info("Found {0} cases in database".format(nr_cases))

    head = HeaderParser()
    head.add_fileformat("VCFv4.3")
    head.add_meta_line("NrCases", nr_cases)
    head.add_info("Obs", '1', 'Integer', "The number of observations for the variant")
    head.add_info("Hom", '1', 'Integer', "The number of observed homozygotes")
    head.add_info("Hem", '1', 'Integer', "The number of observed hemizygotes")
    head.add_version_tracking("loqusdb", __version__, datetime.now().strftime("%Y-%m-%d %H:%M"))
    for chrom in ordered_chromosomes:
        length = adapter.get_max_position(chrom)
        head.add_contig(contig_id=chrom, length=str(length))

    print_headers(head, outfile=outfile)
    
    for chrom in ordered_chromosomes:
        for variant in adapter.get_variants(chromosome=chrom):
            chrom = variant['chrom']
            pos = variant['start']
            ref = variant['ref']
            alt = variant['alt']
            observations = variant['observations']
            homozygotes = variant['homozygote']
            hemizygotes = variant['hemizygote']
            info = "Obs={0}".format(observations)
            if homozygotes:
                info += ";Hom={0}".format(homozygotes)
            if hemizygotes:
                info += ";Hem={0}".format(hemizygotes)
            variant_line = "{0}\t{1}\t.\t{2}\t{3}\t.\t.\t{4}\n".format(
                chrom, pos, ref, alt, info)
            print_variant(variant_line=variant_line, outfile=outfile)
