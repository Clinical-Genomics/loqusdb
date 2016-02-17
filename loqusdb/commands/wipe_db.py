import logging
import click

from . import base_command

logger = logging.getLogger(__name__)

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@base_command.command()
@click.option('--yes',
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt='Are you sure you want to wipe the entire database?'
)
@click.pass_context
def wipe(ctx):
    """Wipe the entire db
    
    """
    adapter = ctx.obj['adapter']
    
    adapter.wipe_db()
    
