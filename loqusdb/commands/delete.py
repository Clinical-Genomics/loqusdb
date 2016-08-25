# -*- coding: utf-8 -*-
import logging
import click
from datetime import datetime

from loqusdb.exceptions import CaseError
from loqusdb.utils import delete as delete_variants
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
@click.pass_context
def delete(ctx, variant_file, family_file, family_type):
    """Delete the variants of a case."""
    if not family_file:
        logger.error("Please provide a family file")
        ctx.abort()
    
    adapter = ctx.obj['adapter']

    start_deleting = datetime.now()
    try:
        delete_variants(
            adapter=adapter, 
            variant_file=variant_file, 
            family_file=family_file, 
            family_type=family_type
        )
    except (CaseError, IOError) as error:
        logger.warning(error.message)
        ctx.abort()

    logger.info("Time to delete variants: {0}"
                .format(datetime.now() - start_deleting))
