import click

from loqusdb.log import LEVELS, init_log
from loqusdb import logger, __version__
from loqusdb.plugins import MongoAdapter

@click.group()
@click.option('-db', '--database',
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
@click.option('-b', '--backend',
                default='mongo',
                type=click.Choice(['mongo', 'sql']),
                help='Specify what backend to use.'
)
@click.option('-l', '--logfile',
                    type=click.Path(exists=False),
                    help=u"Path to log file. If none logging is "\
                          "printed to stderr."
)
@click.option('-v', '--verbose', count=True, default=1)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, database, username, password, port, host, verbose, logfile, backend):
    """loqusdb: manage a local variant count database."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(min(verbose,1), "INFO")
    init_log(
        logger = logger, 
        filename = logfile, 
        loglevel = loglevel
    )
    
    adapter = MongoAdapter()
    adapter.connect(
        host=host, 
        port=port, 
        database=database, 
    )
    
    ctx.obj = {}
    ctx.obj['db'] = database
    ctx.obj['user'] = username
    ctx.obj['password'] = password
    ctx.obj['port'] = port
    ctx.obj['host'] = host
    ctx.obj['adapter'] = adapter
