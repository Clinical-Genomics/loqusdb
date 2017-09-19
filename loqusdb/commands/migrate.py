import os
import logging
import click

from datetime import datetime

from . import base_command

logger = logging.getLogger(__name__)


@base_command.command()
@click.pass_context
def migrate(ctx,):
    """Migrate an old loqusdb instance to 1.0
    """
    adapter = ctx.obj['adapter']

    logger.info("Time to migrate variants: {0}".format(
                datetime.now() - start_inserting))
    
        