import click

from loqusdb.log import LEVELS, init_log
from loqusdb import logger
from . import load_command, delete_command

@click.group()
@click.option('-db', '--mongo_db',
                default='loqusdb',
)
@click.option('-u', '--username',
                type=str
)
@click.option('-p', '--password',
                type=str
)
@click.option('-port', '--port',
                default=27017,
                help='Specify the port where to look for the mongo database.'
)
@click.option('-h', '--host',
                default='localhost',
                help='Specify the host where to look for the mongo database.'
)
@click.option('-v', '--verbose', count=True, default=1)
@click.pass_context
def cli(ctx, mongo_db, username, password, port, host, verbose):
    """loqusdb: manage a local variant count database."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose, 3))
    init_log(logger, loglevel=loglevel)
    
    ctx.db = mongo_db
    ctx.user = username
    ctx.password = password
    ctx.port = port
    ctx.host = host


cli.add_command(load_command)
cli.add_command(delete_command)