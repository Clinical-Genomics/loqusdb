import logging

import click

from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("identity", short_help="Search identity collection")
@click.option("-v", "--variant-id", help="Search for a variant ID.")
@click.pass_context
def identity(ctx, variant_id):
    """Check how well SVs are working in the database"""
    if not variant_id:
        LOG.warning("Please provide a variant id")
        ctx.abort()

    adapter = ctx.obj["adapter"]

    LOG.info("Search variants {0}".format(adapter))

    variant_count: int = adapter.db.identity.count_documents({"variant_id": variant_id})
    if variant_count == 0:
        LOG.info(f"No hits for variant {variant_id}")
        return

    for res in result:
        click.echo(res)
