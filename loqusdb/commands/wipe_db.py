import logging
import click

from . import base_command

logger = logging.getLogger(__name__)

@base_command.command()
@click.option('--wipe_database',
    # click.Choice(['Yes', 'No']),
    prompt='Are you sure you want to wipe the entire database?[Yes/No]'
)
@click.pass_context
def wipe(ctx, wipe_database):
    """Wipe the entire db
    
    """
    if not wipe_database == 'Yes':
        ctx.abort()
    
    adapter = ctx.obj['adapter']
    
    adapter.wipe_db()
    
