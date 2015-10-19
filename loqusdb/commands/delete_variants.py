import sys
import logging
import click

from ped_parser import FamilyParser

from loqusdb.utils import (get_db, delete_case, delete_variant, get_family)

logger = logging.getLogger(__name__)

@click.command()
@click.option('-v', '--variant_file',
                    nargs=1,
                    type=click.File('r'),
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
@click.option('-i', '--family_id',
                    nargs=1, 
                    type=str,
                    help='The id for the case to add'
)
@click.pass_context
def delete(ctx, variant_file, family_file, family_type, family_id):
    """Delete the variants of a case from the frequency database.
    
    """
    if not family_file or family_id:
        logger.error("Please provide a family file or a case id")
        logger.info("Exiting")
        sys.exit()
    
    family = get_family(
        family_file=family_file,
        family_type=family_type
    )
    
    family_id = family.family_id

    db = get_db(
        host=ctx.parent.host, 
        port=ctx.parent.port, 
        database=ctx.parent.db
    )
    
    case = {
        'case_id': family_id,
    }
    
    delete_case(db, case)
    
    # for line in variant_file:
    #     if not line.startswith('#'):
    #         delete_variant(db, get_formated_variant(line))
    
    
    
