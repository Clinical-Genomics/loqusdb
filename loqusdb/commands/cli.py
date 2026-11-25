import logging

import click
import coloredlogs
import yaml
from loqusdb import __version__
from loqusdb.constants import GRCH37, GRCH38
from mongo_adapter import get_client
from mongo_adapter.exceptions import Error as DB_Error
from pymongo import uri_parser

from loqusdb.plugins.mongo.adapter import MongoAdapter

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LOG = logging.getLogger(__name__)


@click.group()
@click.option(
    "-db",
    "--database",
    help="Defaults to 'loqusdb' if not specified",
)
@click.option("-u", "--username", type=str)
@click.option("-p", "--password", type=str)
@click.option(
    "-a",
    "--authdb",
    type=str,
    help="If authentication should be done against another database than --database",
)
@click.option(
    "-port",
    "--port",
    default=27017,
    show_default=True,
    help="Specify the port where to look for the mongo database.",
)
@click.option(
    "-h",
    "--host",
    default="localhost",
    show_default=True,
    help="Specify the host where to look for the mongo database.",
)
@click.option("--uri", help="Specify a mongodb uri")
@click.option("-c", "--config", type=click.File("r"), help="Use a config with db information")
@click.option(
    "-t", "--test", is_flag=True, help="Used for testing. This will use a mongomock database."
)
@click.option(
    "-g",
    "--genome-build",
    default="GRCh37",
    show_default=True,
    type=click.Choice([GRCH37, GRCH38]),
    help="Specify what genome build to use",
)
@click.option(
    "--keep-chr-prefix",
    is_flag=True,
    default=False,
    show_default=True,
    help="Retain the 'chr/Chr/CHR' prefix for chromosomes if it is present",
)
@click.option("-v", "--verbose", is_flag=True)
@click.version_option(__version__)
@click.pass_context
def cli(
    ctx,
    database,
    username,
    password,
    authdb,
    port,
    host,
    uri,
    verbose,
    config,
    test,
    genome_build,
    keep_chr_prefix,
):
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

    uri = configs.get("uri") or uri
    if test:
        uri = "mongomock://"
    try:
        client = get_client(
            host=configs.get("host") or host,
            port=configs.get("port") or port,
            username=configs.get("username") or username,
            password=configs.get("password") or password,
            authdb=authdb or database or "loqusdb",
            uri=uri,
        )
    except DB_Error as err:
        LOG.warning(err)
        ctx.abort()

    database = configs.get("db_name") or database

    if not database:
        database = "loqusdb"
        if uri:
            uri_info = uri_parser.parse_uri(uri)
            database = uri_info.get("database")

    adapter = MongoAdapter(client, db_name=database)

    genome_build = genome_build or configs.get("genome_build")
    keep_chr_prefix = keep_chr_prefix or configs.get("keep_chr_prefix")

    ctx.obj = {}
    ctx.obj["db"] = database
    if uri:
        ctx.obj["uri"] = uri
    else:
        ctx.obj["port"] = port
        ctx.obj["host"] = host
    ctx.obj["adapter"] = adapter
    ctx.obj["version"] = __version__
    ctx.obj["genome_build"] = genome_build
    ctx.obj["keep_chr_prefix"] = keep_chr_prefix
