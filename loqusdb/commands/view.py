# -*- coding: utf-8 -*-
import logging
import json

import click

from pprint import pprint as pp

from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('cases', short_help="Display cases in database")
@click.option('-c' ,'--case-id', 
                help='Search for case'
)
@click.option('--to-json', is_flag=True)
@click.pass_context
def cases(ctx, case_id, to_json):
    """Display cases in the database."""
    
    adapter = ctx.obj['adapter']
    cases = []
    
    if case_id:
        case_obj = adapter.case({'case_id':case_id})
        if not case_obj:
            LOG.info("Case {0} does not exist in database".format(case_id))
            return
        case_obj['_id'] = str(case_obj['_id'])
        cases.append(case_obj)
    else:
        cases = adapter.cases()
        if cases.count() == 0:
            LOG.info("No cases found in database")
            context.abort()
    
    if to_json:
        click.echo(json.dumps(cases))
        return

    click.echo("#case_id\tvcf_path")

    for case_obj in cases:
        click.echo("{0}\t{1}".format(case_obj.get('case_id'), case_obj.get('vcf_path')))

@base_command.command('variants', short_help="Display variants in database")
@click.option('--variant-id', 
                help='Search for a variant'
)
@click.option('-c', '--chromosome', 
                help='Search for all variants in a chromosome'
)
@click.option('--end-chromosome', 
                help='Search for all variants that ends on chromosome'
)
@click.option('-s', '--start',
                help='Start of region',
                type=int
)
@click.option('-e', '--end', 
                help='End of region',
                type=int
)
@click.option('-t', '--variant-type', 
                help='Variant type to search for',
                type=click.Choice(['sv', 'snv']),
                default='snv'
)
@click.option('--sv-type', 
                help='Type of svs to search for',
)
# @click.option('--sort-key',
#                 help='Specify what field to sort on',
# )
@click.pass_context
def variants(ctx, variant_id, chromosome, end_chromosome, start, end, variant_type, 
             sv_type):
    """Display variants in the database."""
    if sv_type:
        variant_type = 'sv'
    
    adapter = ctx.obj['adapter']
    
    if (start or end):
        if not (chromosome and start and end):
            LOG.warning("Regions must be specified with chromosome, start and end")
            return
    
    if variant_id:
        variant = adapter.get_variant({'_id':variant_id})
        if variant:
            click.echo(variant)
        else:
            LOG.info("Variant {0} does not exist in database".format(variant_id))
        return
    
    if variant_type == 'snv':
        result = adapter.get_variants(
            chromosome=chromosome, 
            start=start, 
            end=end
        )
    else:
        LOG.info("Search for svs")
        result = adapter.get_sv_variants(
            chromosome=chromosome, 
            end_chromosome=end_chromosome, 
            sv_type=sv_type, 
            pos=start, 
            end=end
        )
        
    i = 0
    for variant in result:
        i += 1
        pp(variant)
    
    LOG.info("Number of variants found in database: %s", i)

@base_command.command('index', short_help="Add indexes to database")
@click.option('--view', 
    is_flag=True,
    help='Only display existing indexes',
)
@click.pass_context
def index(ctx, view):
    """Index the database."""
    adapter = ctx.obj['adapter']
    if view:
        click.echo(adapter.indexes())
        return
    adapter.ensure_indexes()
