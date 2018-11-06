# -*- coding: utf-8 -*-
import logging
import click
from datetime import datetime

from loqusdb.exceptions import CaseError
from loqusdb.utils.delete import delete as delete_command
from loqusdb.utils.case import get_case
from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('delete', short_help="Delete the variants of a family")
@click.option('-f', '--family-file',
                    type=click.Path(exists=True),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family-type', 
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-c' ,'--case-id', 
                type=str, 
                help='If a different case id than the one in ped file should be used'
)
@click.pass_context
def delete(ctx, family_file, family_type, case_id):
    """Delete the variants of a case."""
    if not (family_file or case_id):
        LOG.error("Please provide a family file")
        ctx.abort()
    
    adapter = ctx.obj['adapter']
    
    # Get a ped_parser.Family object from family file
    family = None
    family_id = None
    if family_file:
        with open(family_file, 'r') as family_lines:
            family = get_case(
                family_lines=family_lines, 
                family_type=family_type
            )
            family_id = family.family_id
    
    # There has to be a case_id or a family at this stage.
    case_id = case_id or family_id
    
    if not case_id:
        LOG.warning("Please provide a case id")
        ctx.abort()

    existing_case = adapter.case({'case_id': case_id})
    if not existing_case:
        LOG.warning("Case %s does not exist in database" %case_id)
        context.abort
    

    start_deleting = datetime.now()
    try:
        delete_command(
            adapter=adapter, 
            case_obj=existing_case,
        )
    except (CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()
