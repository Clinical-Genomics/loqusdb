import logging
import click
import tempfile

from datetime import datetime

from vcftoolbox import (HeaderParser, print_headers, print_variant)

from loqusdb import CHROMOSOME_ORDER
from loqusdb.utils.variant import format_variant

from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('export', short_help="Export variants to VCF format")
@click.option('-o', '--outfile',
    type=click.File('w'),
    help='Specify the path to a file where results should be stored.'
)
@click.option('-t','--variant-type',
    type=click.Choice(['sv','snv']),
    default='snv',
    show_default=True,
    help="If svs or snvs should be exported"
)
@click.pass_context
def export(ctx, outfile, variant_type):
    """Export the variants of a loqus db
        
        The variants are exported to a vcf file
    """
    adapter = ctx.obj['adapter']
    version = ctx.obj['version']
    
    LOG.info("Export the variants from {0}".format(adapter))
    nr_cases = 0

    is_sv = variant_type == 'sv'
    existing_chromosomes = set(adapter.get_chromosomes(sv=is_sv))
    
    ordered_chromosomes = []
    for chrom in CHROMOSOME_ORDER:
        if chrom in existing_chromosomes:
            ordered_chromosomes.append(chrom)
            existing_chromosomes.remove(chrom)
    for chrom in existing_chromosomes:
        ordered_chromosomes.append(chrom)
    
    nr_cases = adapter.cases().count()
    LOG.info("Found {0} cases in database".format(nr_cases))

    head = HeaderParser()
    head.add_fileformat("VCFv4.3")
    head.add_meta_line("NrCases", nr_cases)
    head.add_info("Obs", '1', 'Integer', "The number of observations for the variant")
    head.add_info("Hom", '1', 'Integer', "The number of observed homozygotes")
    head.add_info("Hem", '1', 'Integer', "The number of observed hemizygotes")
    head.add_version_tracking("loqusdb", version, datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    if variant_type == 'sv':
        head.add_info("END", '1', 'Integer', "End position of the variant")
        head.add_info("SVTYPE", '1', 'String', "Type of structural variant")
        head.add_info("SVLEN", '1', 'Integer', "Length of structural variant")
        
        
    for chrom in ordered_chromosomes:
        length = adapter.get_max_position(chrom)
        head.add_contig(contig_id=chrom, length=str(length))

    print_headers(head, outfile=outfile)
    
    for chrom in ordered_chromosomes:
        if variant_type == 'snv':
            LOG.info("Collecting all SNV variants")
            variants = adapter.get_variants(chromosome=chrom)
        else:
            LOG.info("Collecting all SV variants")
            variants = adapter.get_sv_variants(chromosome=chrom)
        LOG.info("{} variants found".format(variants.count()))
        for variant in variants:
            variant_line = format_variant(variant, variant_type=variant_type)
            # chrom = variant['chrom']
            # pos = variant['start']
            # ref = variant['ref']
            # alt = variant['alt']
            # observations = variant['observations']
            # homozygotes = variant['homozygote']
            # hemizygotes = variant['hemizygote']
            # info = "Obs={0}".format(observations)
            # if homozygotes:
            #     info += ";Hom={0}".format(homozygotes)
            # if hemizygotes:
            #     info += ";Hem={0}".format(hemizygotes)
            # variant_line = "{0}\t{1}\t.\t{2}\t{3}\t.\t.\t{4}\n".format(
            #     chrom, pos, ref, alt, info)
            print_variant(variant_line=variant_line, outfile=outfile)
