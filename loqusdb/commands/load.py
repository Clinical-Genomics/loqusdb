import os
import logging
import click
import sys

from cyvcf2 import VCF

from loqusdb.exceptions import CaseError
from loqusdb.vcf_tools import get_formated_variant
from loqusdb.utils import (get_family, load_variants)

from . import base_command

logger = logging.getLogger(__name__)


@base_command.command()
@click.argument('variant_file',
                    type=click.Path(),
                    metavar='<vcf_file>'
)
@click.option('-f', '--family_file',
                    type=click.File('r'),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family_type', 
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
@click.option('-b' ,'--bulk_insert', 
                is_flag=True, 
                help='Insert bulks of variants for better performance'
)
@click.pass_context
def load(ctx, variant_file, family_file, family_type, bulk_insert):
    """Load the variants of a case

    The loading is based on if the variant is seen in a ny affected individual
    in the family.
    """
    if not family_file:
        logger.error("Please provide a family file")
        ctx.abort()

    logger.info("Start parsing variants from: {0}".format(variant_file))
    variant_path = os.path.abspath(variant_file)
    vcf = VCF(variant_file)
        
    try:
        family = get_family(
            family_lines=family_file, 
            family_type=family_type
        )
    except SyntaxError as error:
        logger.warning(error.message)
        ctx.abort()

    if not family.affected_individuals:
        logger.warning("No affected individuals could be found in ped file")
    
    logger.info("Found affected individuals in ped file: {0}"
                .format(', '.join(family.affected_individuals)))
    
    logger.debug("Check if individuals from ped file exists in vcf...")
    if not set(vcf.samples).intersection(set(family.individuals)):
        logger.warning("Individuals in ped file does not exist in variant file")
        ctx.abort()

    adapter = ctx.obj['adapter']
    
    try:
        load_case(
            adapter=adapter,
            case=family
        )
    except CaseError as error:
        logger.error(error.message)
        ctx.abort()

    try:
        load_variants(  
            adapter=adapter, 
            family_id=family.family_id, 
            individuals=family.individuals,
            vcf=vcf, 
            bulk_insert=bulk_insert,
            vcf_path=variant_path
        )
    except CaseError as error:
        logger.error(error.message)
        ctx.abort()
