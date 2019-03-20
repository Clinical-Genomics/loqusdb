import click
import logging

from loqusdb.utils.vcf import get_file_handle
from loqusdb.build_models import build_profile_variant

from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('profile', short_help = "Loads variants to be used in profiling")
@click.argument('vcf_file', type = click.Path(exists=True))
@click.pass_context
def load_profile(ctx, vcf_file):

    adapter = ctx.obj['adapter']

    vcf = get_file_handle(vcf_file)

    profile_variants = [build_profile_variant(variant) for variant in vcf]

    adapter.add_profile_variants(profile_variants)

    
