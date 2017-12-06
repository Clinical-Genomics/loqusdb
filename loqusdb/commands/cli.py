import logging
import click
import coloredlogs

from mongomock import MongoClient as MockClient

from mongo_adapter import get_client
from mongo_adapter.exceptions import Error as DB_Error

from loqusdb.log import LEVELS, init_log
from loqusdb import __version__
from loqusdb.plugins import MongoAdapter

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

LOG = logging.getLogger(__name__)

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
@click.option('-t', '--test',
                is_flag=True,
                help='Used for testing.'
)
@click.option('-v', '--verbose', count=True, default=1)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, database, username, password, port, host, verbose, test):
    """loqusdb: manage a local variant count database."""
    # configure root logger to print to STDERR
    loglevel = LEVELS.get(max(verbose,1), "INFO")
    coloredlogs.install(level=loglevel)
    if test:
        client = MockClient()
    else:
        try:
            client = get_client(
                host=host, 
                port=port, 
                username=username,
                password=password,
            )
        except DB_Error as err:
            LOG.warning(err)
            ctx.abort()

    # mongo uri looks like:
    # mongodb://[username:password@]host1[:port1][,host2[:port2],...
    # [,hostN[:portN]]][/[database][?options]]
    if password:
        pwd = '******'
    else:
        pwd = None
    LOG.info('uri=mongodb//:{0}:{1}@{2}:{3}/{4}'.format(
        username, pwd, host, port, database
    ))

    adapter = MongoAdapter(client, db_name = database)
    
    ctx.obj = {}
    ctx.obj['db'] = database
    ctx.obj['user'] = username
    ctx.obj['password'] = password
    ctx.obj['port'] = port
    ctx.obj['host'] = host
    ctx.obj['adapter'] = adapter
    ctx.obj['version'] = __version__
