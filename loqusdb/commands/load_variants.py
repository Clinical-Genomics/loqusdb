import sys
import os
import logging
import click

from vcftoolbox import (get_variant_dict, get_info_dict, Genotype, 
get_variant_id)

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

    analysis_individual = list(affected_individuals)[0]
    
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
    for line in variant_file:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            nr_of_variants += 1
            variant = get_variant_dict(
                variant_line = line, 
                header_line = header
            )
            found_variant = False
            found_homozygote = False
            
            for ind_id in affected_individuals:
                gt_call = dict(zip(
                    variant['FORMAT'].split(':'),
                    variant[ind_id].split(':'))
                )
                genotype = Genotype(**gt_call)
                if genotype.has_variant:
                    logger.debug("Found variant in affected")
                    found_variant = True
                if genotype.homo_alt:
                    logger.debug("Found homozygote alternative variant in affected")
                    found_homozygote = True
            
            if found_variant:
                nr_of_inserted += 1
                mongo_variant = {
                    'variant_id': get_variant_id(variant),
                    'homozygote': 0
                }
                if found_homozygote:
                    mongo_variant['homozygote'] = 1
                
                add_variant(
                    db=db,
                    variant=mongo_variant
                )
    logger.info("Nr of variants in vcf: {0}".format(nr_of_variants))
    logger.info("Nr of variants inserted: {0}".format(nr_of_inserted))
    
    
