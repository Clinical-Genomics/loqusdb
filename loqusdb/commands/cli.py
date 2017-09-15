import logging
import click
import coloredlogs

from loqusdb.log import LEVELS, init_log
from loqusdb import logger, __version__
from loqusdb.plugins import MongoAdapter

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

logger = logging.getLogger(__name__)

@click.group()
@click.option('-db', '--database',
                default='loqusdb',
                show_default=True,
)
@click.option('-u', '--username',
                type=str
)
@click.option('-p', '--password',
                type=str
)
@click.option('-port', '--port',
                default=27017,
                show_default=True,
                help='Specify the port where to look for the mongo database.'
)
@click.option('-h', '--host',
                default='localhost',
                show_default=True,
                help='Specify the host where to look for the mongo database.'
)
# @click.option('-b', '--backend',
#                 default='mongo',
#                 show_default=True,
#                 type=click.Choice(['mongo',]),
#                 help='Specify what backend to use.'
# )
@click.option('-c', '--conn_host',
                default='mongodb://',
                show_default=True,
                help='Used for testing.'
)
@click.option('-v', '--verbose', count=True, default=1)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, conn_host, database, username, password, port, host, verbose):
    """loqusdb: manage a local variant count database."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(max(verbose,1), "INFO")
    coloredlogs.install(level=loglevel)
    
    # mongo uri looks like:
    #mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    uri = None
    if username and password:
        uri = "{0}{1}:{2}@{3}:{4}/{5}".format(
              conn_host, username, password, host, port, database
              )
        if password:
            pwd = '******'
        else:
            pwd = None
        logger.info('uri={0}{1}:{2}@{3}:{4}/{5}'.format(
            conn_host, username, pwd, host, port, database
        ))
    
    adapter = MongoAdapter()
    adapter.connect(
        host=host, 
        port=port, 
        database=database,
        uri=uri
    )
    
    ctx.obj = {}
    ctx.obj['db'] = database
    ctx.obj['user'] = username
    ctx.obj['password'] = password
    ctx.obj['port'] = port
    ctx.obj['host'] = host
    ctx.obj['adapter'] = adapter
