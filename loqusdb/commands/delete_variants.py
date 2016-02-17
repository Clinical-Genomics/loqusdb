import logging
import click
from datetime import datetime

from vcftoolbox import get_vcf_handle

from loqusdb.utils import get_family
from loqusdb.vcf_tools import get_formated_variant
from loqusdb.exceptions import CaseError
from . import base_command

logger = logging.getLogger(__name__)

@base_command.command()
@click.argument('variant_file',
                    nargs=1,
                    type=click.Path(exists=True),
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
@click.option('-i', '--family_id',
                    nargs=1, 
                    type=str,
                    help='The id for the case to add'
)
@click.pass_context
def delete(ctx, variant_file, family_file, family_type, family_id):
    """Delete the variants of a case from the frequency database.
    
    """
    if not family_file or family_id:
        logger.error("Please provide a family file or a case id")
        logger.info("Exiting")
        ctx.abort()
    
    family = get_family(
        family_lines=family_file,
        family_type=family_type
    )
    
    family_id = family.family_id
    
    adapter = ctx.obj['adapter']
    
    case = {
        'case_id': family_id,
    }
    
    try:
        adapter.delete_case(case)
    except CaseError as err:
        logger.warning(err.message)
        ctx.abort()
    
    affected_individuals = family.affected_individuals
    
    if variant_file == '-':
        logger.info("Start parsing variants from stdin")
        variant_file_handle = get_vcf_handle(
            fsock=sys.stdin, 
        )
    else:
        logger.info("Start parsing variants from stdin")
        variant_file_handle = get_vcf_handle(
            infile=variant_file, 
        )
    
    header = []
    nr_of_deleted = 0
    
    start_deleting = datetime.now()
    
    for line in variant_file_handle:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            formated_variant = get_formated_variant(
                variant_line = line,
                header_line = header,
                affected_individuals = affected_individuals
            )
            
            adapter.delete_variant(formated_variant)
            nr_of_deleted += 1
    
    logger.info("Nr of variants deleted: {0}".format(nr_of_deleted))
    logger.info("Time to delete variants: {0}".format(datetime.now() - start_deleting))
    
    
    
