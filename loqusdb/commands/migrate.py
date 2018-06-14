import logging
import click

from datetime import datetime

from loqusdb.utils.migrate import migrate_database
from . import base_command

LOG = logging.getLogger(__name__)


@base_command.command('migrate', short_help="Migrate an old loqusdb instance")
@click.pass_context
def migrate(ctx,):
    """Migrate an old loqusdb instance to 1.0
    """
    adapter = ctx.obj['adapter']
    
    start_time = datetime.now()
    
    nr_updated = migrate_database(adapter)
    
    LOG.info("All variants updated, time to complete migration: {}".format(
        datetime.now() - start_time))
    LOG.info("Nr variants that where updated: %s", nr_updated)