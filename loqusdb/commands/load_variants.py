import os
import logging
import click
import sys

from vcftoolbox import get_vcf_handle

from loqusdb.exceptions import CaseError
from loqusdb.vcf_tools import get_formated_variant
from loqusdb.utils import get_family
from loqusdb.utils import load_variants

from . import base_command

logger = logging.getLogger(__name__)


@base_command.command()
@click.argument('variant_file',
                    nargs=1,
                    type=click.Path(),
                    metavar='<vcf_file> or -'
)
@click.option('-f', '--family_file',
                    nargs=1, 
                    type=click.File('r'),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family_type', 
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-b' ,'--bulk_insert', 
                is_flag=True, 
                help='Insert bulks of variants for better performance'
)
@click.pass_context
def load(ctx, variant_file, family_file, family_type, bulk_insert):
    """Load the variants of a case

    The loading is based on if the variant is seen in a ny affected individual
    in the family.
    """
    if not family_file:
        logger.error("Please provide a family file")
        ctx.abort()

    if variant_file == '-':
        logger.info("Parsing variants from stdin")
        variant_file = get_vcf_handle(fsock=sys.stdin)
    else:
        logger.info("Start parsing variants from stdin")
        variant_path = os.path.abspath(variant_file)
        variant_file = get_vcf_handle(infile=variant_file)

    try:
        family = get_family(family_lines=family_file, family_type=family_type)
    except SyntaxError as error:
        logger.warning(error.message)
        ctx.abort()

    if not family.affected_individuals:
        logger.error("No affected individuals could be found in ped file")
        ctx.abort()
    logger.info("Found affected individuals in ped file: {0}"
                .format(', '.join(family.affected_individuals)))

    adapter = ctx.obj['adapter']
    try:
        load_variants(adapter, family.family_id, family.affected_individuals,
                      variant_file, bulk_insert=bulk_insert,
                      vcf_path=variant_path)
    except CaseError as error:
        logger.error(error.message)
        ctx.abort()
