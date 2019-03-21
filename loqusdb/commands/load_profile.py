import click
import logging

from loqusdb.utils.load import load_profile_variants


from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('profile', short_help = "Loads variants to be used in profiling")
@click.argument('vcf_file', type = click.Path(exists=True))
@click.pass_context
def load_profile(ctx, vcf_file):

    adapter = ctx.obj['adapter']

    load_profile_variants(adapter, vcf_file)
