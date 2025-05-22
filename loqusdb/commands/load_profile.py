import json
import logging

import click
from loqusdb.resources import MAF_PATH
from loqusdb.utils.load import load_profile_variants
from loqusdb.utils.profiling import check_duplicates, get_profiles, profile_stats, update_profiles

from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


def validate_profile_threshold(ctx, param, value):
    if not (0 <= value <= 1):
        raise ValueError("threshold must be between 0-1")

    return value


@base_command.command("profile", short_help="Loads variants to be used in profiling")
@click.option("-l", "--load", is_flag=True, help="Load variants that should be used for profiling")
@click.option(
    "-v",
    "--variant-file",
    type=click.Path(exists=True),
    help="Variants from file to be used in profiling. To be used in combination "
    "with the --load flag",
)
@click.option(
    "--update", is_flag=True, help="updates the profiles of all the sample in the database"
)
@click.option(
    "--stats", is_flag=True, help="Checks some statistics of the profiles in the database"
)
@click.option(
    "--profile-threshold",
    type=float,
    default=0.9,
    callback=validate_profile_threshold,
    help="Used with --stats option to determine the number of matching"
    " profiles with a similarity greater than given threshold",
)
@click.option(
    "--check-vcf",
    type=click.Path(exists=True),
    help="A vcf for a case. The profile from this vcf will be checked "
    "against the profiles in the database",
)
@click.pass_context
def load_profile(ctx, load, variant_file, update, stats, profile_threshold, check_vcf):
    """
    Command for profiling of samples. User may upload variants used in profiling
    from a vcf, update the profiles for all samples, and get some stats
    from the profiles in the database.

    Profiling is used to monitor duplicates in the database. The profile is
    based on the variants in the 'profile_variant' collection, assessing
    the genotypes for each sample at the position of these variants.
    """

    adapter = ctx.obj["adapter"]
    keep_chr_prefix = ctx.obj["keep_chr_prefix"]

    LOG.info("Running loqusdb profile")

    if check_vcf:
        LOG.info(f"Check if profile in {check_vcf} has match in database")
        vcf_file = check_vcf
        profiles = get_profiles(adapter, vcf_file, keep_chr_prefix)
        duplicate = check_duplicates(adapter, profiles, profile_threshold)

        if duplicate is not None:
            duplicate = json.dumps(duplicate)
            click.echo(duplicate)
        else:
            LOG.info("No duplicates found in the database")

    if load:
        genome_build = ctx.obj["genome_build"]
        vcf_path = MAF_PATH[genome_build]
        if variant_file is not None:
            vcf_path = variant_file
        LOG.info(f"Loads variants in {vcf_path} to be used in profiling")
        load_profile_variants(adapter, vcf_path, keep_chr_prefix)

    if update:
        LOG.info("Updates profiles in database")
        update_profiles(adapter, keep_chr_prefix)

    if stats:
        LOG.info("Prints profile stats")
        distance_dict = profile_stats(adapter, threshold=profile_threshold)
        click.echo(table_from_dict(distance_dict))


def table_from_dict(dictionary):
    table_str = "Distances within ranges:\n"

    for key, value in dictionary.items():
        table_str += f"{key:15} | {value}\n"

    return table_str
