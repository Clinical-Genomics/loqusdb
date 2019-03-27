import click
import logging

from loqusdb.utils.load import load_profile_variants

from loqusdb.utils.profiling import (update_profiles, profile_stats)


from . import base_command

LOG = logging.getLogger(__name__)


def validate_profile_threshold(ctx, param, value):
    if not (0 <= value <= 1):
        raise ValueError('threshold must be between 0-1')

    return value

@base_command.command('profile', short_help = "Loads variants to be used in profiling")
@click.option('--variant-file',
    type = click.Path(exists=True),
    help = "a vcf containing the SNPs that is used in profiling")
@click.option('--update',
    is_flag=True,
    help = "updates the profiles of all the sample in the database")
@click.option('--stats',
    is_flag=True,
    help="Checks some statistics of the profiles in the database")
@click.option('--profile-threshold',
    type=float,
    default=0.9,
    callback=validate_profile_threshold,
    help="Used with --stats option to determine the number of matching profiles with a similarity greater than given threshold")
@click.pass_context
def load_profile(ctx, variant_file, update, stats, profile_threshold):

    """
        Command for profiling of samples. User may upload variants used in profiling
        from a vcf, update the profiles for all samples, and get some stats
        from the profiles in the database.

        Profiling is used to monitor duplicates in the database. The profile is
        based on the variants in the 'profile_variant' collection, assessing
        the genotypes for each sample at the position of these variants.
    """

    adapter = ctx.obj['adapter']

    if variant_file:
        load_profile_variants(adapter, variant_file)

    if update:
        update_profiles(adapter)

    if stats:

        distance_dict = profile_stats(adapter, threshold=profile_threshold)
        click.echo(table_from_dict(distance_dict))

def table_from_dict(dictionary):


    table_str = "Distances within ranges:\n"

    for key, value in dictionary.items():

        table_str += f"{key:15} | {value}\n"

    return table_str
