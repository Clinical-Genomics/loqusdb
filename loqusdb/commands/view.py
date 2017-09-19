# -*- coding: utf-8 -*-
import logging
import click

from . import base_command

logger = logging.getLogger(__name__)

@base_command.command()
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

@base_command.command()
@click.option('--variant-id', 
                help='Search for a variant'
)
@click.pass_context
def variants(ctx, variant_id):
    """Display variants in the database."""
    
    adapter = ctx.obj['adapter']
    
    if variant_id:
        variant = adapter.get_variant({'_id':variant_id})
        if variant:
            click.echo(variant)
        else:
            logger.info("Variant {0} does not exist in database".format(variant_id))
    else:
        i = 0
        for variant in adapter.get_variants():
            i += 1
            click.echo(variant)
        if i == 0:
            logger.info("No variants found in database")
