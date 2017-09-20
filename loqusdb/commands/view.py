# -*- coding: utf-8 -*-
import logging
import click

from . import base_command

logger = logging.getLogger(__name__)

@base_command.command('cases', short_help="Display cases in database")
@click.option('-c' ,'--case-id', 
                help='Search for case'
)
@click.pass_context
def cases(ctx, case_id):
    """Display all cases in the database."""
    
    adapter = ctx.obj['adapter']
    
    if case_id:
        case = adapter.case(case_id)
        if case:
            click.echo(case)
        else:
            logger.info("Case {0} does not exist in database".format(case_id))
    else:
        i = 0
        for case in adapter.cases():
            i += 1
            click.echo(case)
        if i == 0:
            logger.info("No cases found in database")

@base_command.command('variants', short_help="Display variants in database")
@click.option('--variant-id', 
                help='Search for a variant'
)
@click.option('-c', '--chromosome', 
                help='Search for all variants in a chromosome'
)
@click.option('-s', '--start',
                help='Start of region',
                type=int
)
@click.option('-e', '--end', 
                help='End of region',
                type=int
)
@click.pass_context
def variants(ctx, variant_id, chromosome, start, end):
    """Display variants in the database."""
    
    adapter = ctx.obj['adapter']
    if (start or end):
        if not (chromosome and start and end):
            logger.warning("Regions must be specified with chromosome, start and end")
            ctx.abort()
    
    if variant_id:
        variant = adapter.get_variant({'_id':variant_id})
        if variant:
            click.echo(variant)
        else:
            logger.info("Variant {0} does not exist in database".format(variant_id))
    else:
        i = 0
        result = adapter.get_variants(
            chromosome=chromosome, 
            start=start, 
            end=end
        )
        for variant in result:
            i += 1
            click.echo(variant)
        if i == 0:
            logger.info("No variants found in database")

@base_command.command('index', short_help="Add indexes to database")
@click.pass_context
def index(ctx):
    """Index the database."""
    adapter = ctx.obj['adapter']
    adapter.ensure_indexes()
