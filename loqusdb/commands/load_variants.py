import sys
import os
import logging
import click

from vcftoolbox import (get_variant_dict, get_info_dict, Genotype)

from loqusdb.utils import (get_db, add_variant, add_case, get_family)
from loqusdb.exceptions import CaseError

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
        
    analysis_individual = None
    
    family_id = family.family_id
    
    affected_individuals = family.affected_individuals
    
    if not affected_individuals:
        logger.error("No affected individuals could be found in ped file")
        logger.info("Exiting")
        sys.exit(1)
    
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
    for line in variant_file:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            variant = get_variant_dict(
                variant_line = line, 
                header_line = header
            )
            gt_call = dict(zip(
                variant['FORMAT'].split(':'),
                variant[analysis_individual].split(':'))
            )
            genotype = Genotype(**gt_call)
            print(genotype.__dict__)
            # print(line.rstrip())
            # add_variant(db, get_formated_variant(line))
            
    
    
