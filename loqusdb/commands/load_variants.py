import os
import logging
import click

from datetime import datetime

from vcftoolbox import get_vcf_handle

from loqusdb.exceptions import CaseError
from loqusdb.vcf_tools import get_formated_variant
from loqusdb.utils import get_family

from . import base_command

logger = logging.getLogger(__name__)

@base_command.command()
@click.argument('variant_file',
                    nargs=1,
                    type=click.Path(),
                    metavar='<vcf_file> or -'
)
@click.option('-f', '--family_file',
                    nargs=1, 
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
    
    try:
        family = get_family(
            family_lines = family_file, 
            family_type = family_type
        )
    except SyntaxError as err:
        logger.warning(err.message)
        ctx.abort()
    
    family_id = family.family_id
    
    affected_individuals = family.affected_individuals
    
    if not affected_individuals:
        logger.error("No affected individuals could be found in ped file")
        ctx.abort()

    logger.info("Found affected individuals in ped file: {0}".format(
        ', '.join(affected_individuals)
    ))
    
    adapter = ctx.obj['adapter']
    
    case = {
        'case_id': family_id,
        'vcf_path': os.path.abspath(variant_file)
    }
    
    try:
        adapter.add_case(case)
    except CaseError as e:
        logger.error(e.message)
        ctx.abort()
    
    if variant_file == '-':
        logger.info("Start parsing variants from stdin")
        variant_file = get_vcf_handle(
            fsock=sys.stdin, 
        )
    else:
        logger.info("Start parsing variants from stdin")
        variant_file = get_vcf_handle(
            infile=variant_file, 
        )
    
    
    #This is the header line with mandatory vcf fields
    header = []
    nr_of_variants = 0
    nr_of_inserted = 0
    
    start_inserting = datetime.now()
    start_ten_thousand = datetime.now()
    
    variants = []
    for line in variant_file:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            nr_of_variants += 1
            
            formated_variant = get_formated_variant(
                variant_line = line,
                header_line = header,
                affected_individuals = affected_individuals
            )
            
            if formated_variant:
                nr_of_inserted += 1
                if bulk_insert:
                    variants.append(formated_variant)
                else:
                    adapter.add_variant(variant=formated_variant)
            
            if nr_of_variants % 10000 == 0:
                logger.info("{0} of variants processed".format(nr_of_variants))
                logger.info("Time to insert last 10000: {0}".format(
                    datetime.now()-start_ten_thousand))
                start_ten_thousand = datetime.now()
                
            if nr_of_variants % 100000 == 0:
                if bulk_insert:
                    adapter.add_bulk(variants)
                    variants = []
    
    if bulk_insert:
        adapter.add_bulk(variants)
    
    logger.info("Nr of variants in vcf: {0}".format(nr_of_variants))
    logger.info("Nr of variants inserted: {0}".format(nr_of_inserted))
    logger.info("Time to insert variants: {0}".format(datetime.now() - start_inserting))
    
    
