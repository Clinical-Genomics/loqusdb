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
@click.option('--ensure-index', 
                is_flag=True, 
                help='Make sure that the indexes are in place'
)
@click.option('--gq-treshold',
    default=20,
    show_default=True,
    help='Treshold to consider variant'
)
@click.option('--max-window', '-m',
    default=2000,
    show_default=True,
    help='Specify the maximum window size for svs'
)
@click.pass_context
def load(ctx, variant_file, family_file, family_type, skip_case_id, gq_treshold, case_id, 
         ensure_index, max_window):
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
        # Open the file regardless of compression
        variant_handle = get_file_handle(variant_path)
        vcf_info = check_vcf(variant_handle)
        nr_variants = vcf_info['nr_variants']
        variant_type = vcf_info['variant_type']
    except VcfError as error:
        LOG.warning(error)
        ctx.abort()

    LOG.info("Vcf file looks fine")
    LOG.info("Nr of variants in vcf: {0}".format(nr_variants))
    LOG.info("Type of variants in vcf: {0}".format(variant_type))
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
            variant_type=variant_type,
            max_window=max_window,
        )
    except (SyntaxError, CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()
    
    LOG.info("Time to insert variants: {0}".format(
                datetime.now() - start_inserting))
    if ensure_index:
        adapter.ensure_indexes()
    else:
        adapter.check_indexes()
    
        
        