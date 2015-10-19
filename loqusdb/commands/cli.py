import click

from loqusdb.log import LEVELS, init_log
from loqusdb import logger, __version__
from . import load_command, delete_command, wipe_command

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
@click.option('-l', '--logfile',
                    type=click.Path(exists=False),
                    help=u"Path to log file. If none logging is "\
                          "printed to stderr."
)
@click.option('-v', '--verbose', count=True, default=1)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, mongo_db, username, password, port, host, verbose, logfile):
    """loqusdb: manage a local variant count database."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose,1), "INFO")
    init_log(
        logger = logger, 
        filename = logfile, 
        loglevel = loglevel
    )
    
    ctx.db = mongo_db
    ctx.user = username
    ctx.password = password
    ctx.port = port
    ctx.host = host


cli.add_command(load_command)
cli.add_command(delete_command)
cli.add_command(wipe_command)