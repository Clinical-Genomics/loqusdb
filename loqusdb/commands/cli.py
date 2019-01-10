import logging
import click
import coloredlogs

from pprint import pprint as pp

import yaml

from mongomock import MongoClient as MockClient

from pymongo import uri_parser

from mongo_adapter import get_client
from mongo_adapter.exceptions import Error as DB_Error

from loqusdb.log import LEVELS, init_log
from loqusdb import __version__
from loqusdb.plugins import MongoAdapter

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

LOG = logging.getLogger(__name__)

@click.group()
@click.option('-db', '--database',
                help="Defaults to 'loqusdb' if not specified",
)
@click.option('-u', '--username',
                type=str
)
@click.option('-p', '--password',
                type=str
)
@click.option('-a', '--authdb',
                type=str,
                help="If authentication should be done against another database than --database"
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
@click.option('--uri',
                help='Specify a mongodb uri'
)
@click.option('-c', '--config',
                type=click.File('r'),
                help='Use a config with db information'
)
@click.option('-t', '--test',
                is_flag=True,
                help='Used for testing. This will use a mongomock database.'
)
@click.option('-v', '--verbose', is_flag=True)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, database, username, password, authdb, port, host, uri, verbose, config, test):
    """loqusdb: manage a local variant count database."""
    loglevel = "INFO"
    if verbose:
        loglevel = "DEBUG"
    coloredlogs.install(level=loglevel)
    LOG.info("Running loqusdb version %s", __version__)

    configs = {}
    if config:
        try:
            configs = yaml.safe_load(config)
        except yaml.YAMLError as err:
            LOG.warning(err)
            ctx.abort()
    
    uri = configs.get('uri') or uri
    if test:
        uri = "mongomock://"
    try:
        client = get_client(
            host=configs.get('host') or host,
            port=configs.get('port') or port,
            username=configs.get('username') or username,
            password=configs.get('password') or password,
            authdb=authdb or database or 'loqusdb',
            uri=uri,
        )
    except DB_Error as err:
        LOG.warning(err)
        ctx.abort()
    
    database = configs.get('db_name') or database
    
    if not database:
        database = 'loqusdb'
        if uri:
            uri_info = uri_parser.parse_uri(uri)
            database = uri_info.get('database')

    adapter = MongoAdapter(client, db_name=database)

    ctx.obj = {}
    ctx.obj['db'] = database
    ctx.obj['user'] = username
    ctx.obj['password'] = password
    ctx.obj['port'] = port
    ctx.obj['host'] = host
    ctx.obj['adapter'] = adapter
    ctx.obj['version'] = __version__
