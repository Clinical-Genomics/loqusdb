import os
import logging
import click

from pprint import pprint as pp

from datetime import datetime

from loqusdb.exceptions import (CaseError, VcfError)
from loqusdb.utils.load import load_database
from loqusdb.utils.vcf import (get_file_handle, check_vcf)

from . import base_command

LOG = logging.getLogger(__name__)


@base_command.command('load', short_help="Load the variants of a family")
@click.argument('variant-file',
                    type=click.Path(exists=True),
                    metavar='<vcf_file>'
)
@click.option('-f', '--family-file',
                    type=click.Path(exists=True),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family-type', 
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                show_default=True,
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-c' ,'--case-id', 
                type=str, 
                help='If a different case id than the one in ped file should be used'
)
@click.option('-s' ,'--skip-case-id', 
                is_flag=True, 
                show_default=True,
                help='Do not store which cases that have a variant'
)
@click.option('--gq-treshold',
    default=20,
    show_default=True,
    help='Treshold to consider variant'
)
@click.pass_context
def load(ctx, variant_file, family_file, family_type, skip_case_id, gq_treshold, case_id):
    """Load the variants of a case

    The loading is based on if the variant is seen in a ny affected individual
    in the family. If no family file is provided all individuals in vcf file will 
    be considered.
    """
    if not (family_file or case_id):
        LOG.warning("Please provide a family file or a case id")
        ctx.abort()
    
    variant_path = os.path.abspath(variant_file)

    adapter = ctx.obj['adapter']
    
    try:
        variant_handle = get_file_handle(variant_path)
        nr_variants = check_vcf(variant_handle)
    except VcfError as error:
        LOG.warning(error)
        ctx.abort()

    LOG.info("Vcf file looks fine")
    LOG.info("Nr of variants in vcf: {0}".format(nr_variants))
    start_inserting = datetime.now()
    
    try:
        nr_inserted = load_database(
            adapter=adapter,
            variant_file=variant_path,
            family_file=family_file,
            family_type=family_type,
            skip_case_id=skip_case_id,
            case_id=case_id,
            gq_treshold=gq_treshold,
            nr_variants=nr_variants,
        )
    except (SyntaxError, CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()
    
    LOG.info("Time to insert variants: {0}".format(
                datetime.now() - start_inserting))
    adapter.check_indexes()
        