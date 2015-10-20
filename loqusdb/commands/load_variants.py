import sys
import os
import logging
import click

from datetime import datetime

from loqusdb.utils import (get_db, add_variant, add_case, get_family)
from loqusdb.exceptions import CaseError
from loqusdb.vcf_tools import get_formatted_variant

logger = logging.getLogger(__name__)

@click.command()
@click.argument('variant_file',
                    nargs=1,
                    type=click.File('rb'),
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
@click.pass_context
def load(ctx, variant_file, family_file, family_type):
    """Load the variant frequency database
        
        The loading is based on if the variant is seen in a ny affected individual
        in the family.
    """
    if not family_file:
        logger.error("Please provide a family file")
        logger.info("Exiting")
        sys.exit()
    
    try:
        family = get_family(
            family_file = family_file, 
            family_type = family_type
        )
    except SyntaxError:
        logger.info("Exiting")
        sys.exit(1)
        
    
    family_id = family.family_id
    
    affected_individuals = family.affected_individuals
    
    if not affected_individuals:
        logger.error("No affected individuals could be found in ped file")
        logger.info("Exiting")
        sys.exit(1)

    logger.info("Found affected individuals in ped file: {0}".format(
        ', '.join(affected_individuals)
    ))
    
    db = get_db(
        host=ctx.parent.host, 
        port=ctx.parent.port, 
        database=ctx.parent.db
    )
    
    case = {
        'case_id': family_id,
        'vcf_path': os.path.abspath(variant_file.name)
    }
    
    try:
        add_case(db, case)
    except CaseError as e:
        logger.error(e.message)
        sys.exit(1)
    
    #This is the header line with mandatory vcf fields
    header = []
    nr_of_variants = 0
    nr_of_inserted = 0
    
    start_inserting = datetime.now()
    start_ten_thousand = datetime.now()
    
    for line in variant_file:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            nr_of_variants += 1
            
            formatted_variant = get_formatted_variant(
                variant_line = line,
                header_line = header,
                affected_individuals = affected_individuals
            )
            
            if formatted_variant:
                nr_of_inserted += 1
                add_variant(
                    db=db,
                    variant=formatted_variant
                )
            if nr_of_variants % 10000 == 0:
                logger.info("{0} of variants processed".format(nr_of_variants))
                logger.info("Time to insert last 10000: {0}".format(
                    datetime.now()-start_ten_thousand))
                start_ten_thousand = datetime.now()
    
    logger.info("Nr of variants in vcf: {0}".format(nr_of_variants))
    logger.info("Nr of variants inserted: {0}".format(nr_of_inserted))
    logger.info("Time to insert variants: {0}".format(datetime.now() - start_inserting))
    
    
