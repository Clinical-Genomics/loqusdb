import os
import logging
import click

from loqusdb.exceptions import CaseError
from loqusdb.utils import load_database

from . import base_command

logger = logging.getLogger(__name__)


@base_command.command()
@click.argument('variant_file',
                    type=click.Path(exists=True),
                    metavar='<vcf_file>'
)
@click.option('-f', '--family_file',
                    type=click.Path(exists=True),
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
        logger.warning("Please provide a family file")
        ctx.abort()

    variant_path = os.path.abspath(variant_file)

    adapter = ctx.obj['adapter']
    
    try:
        load_database(
            adapter=adapter,
            variant_file=variant_path,
            family_file=family_file,
            family_type=family_type,
            bulk_insert=bulk_insert
        )
    except (SyntaxError, CaseError, IOError) as error:
        logger.warning(error.message)
        ctx.abort()
        