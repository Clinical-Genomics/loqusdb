import sys
import logging
import click

from loqusdb.utils import (get_db, delete_case, delete_variant, get_family)

logger = logging.getLogger(__name__)

@click.command()
@click.option('--wipe_database',
    # click.Choice(['Yes', 'No']),
    prompt='Are you sure you want to wipe the entire database?[Yes/No]'
)
@click.pass_context
def wipe(ctx, wipe_database):
    """Wipe the entire db
    
    """
    if not wipe_database == 'Yes':
        sys.exit()
    logger.info('Trying to access collection {0}'.format(ctx.parent.db))
    
    db = get_db(
        host=ctx.parent.host, 
        port=ctx.parent.port, 
        database=ctx.parent.db
    )
    
    logger.debug('Connection successful')
    
    case_collection = db['case']
    logger.info("Dropping collection 'case'")
    case_collection.drop()
    logger.debug("Case collection dropped")
    
    logger.info("Dropping collection 'variant'")
    variant_collection = db['variant']
    variant_collection.drop()
    logger.debug("Variants dropped.")
    
