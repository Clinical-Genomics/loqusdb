import os
import logging
import click

from pprint import pprint as pp

from datetime import datetime

from loqusdb.exceptions import (VcfError)
from loqusdb.utils.load import load_database
from loqusdb.utils.vcf import (get_file_handle, check_vcf, add_headers)

from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('annotate', short_help="Annotate a VCF with observations")
@click.argument('variant-file',
                    type=click.Path(exists=True),
                    metavar='<vcf_file>',
)
@click.pass_context
def annotate(ctx, variant_file):
    """Annotate the variants in a VCF

    """

    variant_path = os.path.abspath(variant_file)
    
    vcf_obj = get_file_handle(variant_path)
    add_headers(vcf_obj)
    for header_line in vcf_obj.raw_header.split('\n'):
        if len(header_line) == 0:
            continue
        click.echo(header_line)
    ctx.abort()
    nr_cases = adapter.cases().count()
    LOG.info("Found {0} cases in database".format(nr_cases))

    adapter = ctx.obj['adapter']

    start_inserting = datetime.now()
    
    try:
        nr_inserted = load_database(
            adapter=adapter,
            variant_file=variant_path,
            sv_file=variant_sv_path,
            family_file=family_file,
            family_type=family_type,
            skip_case_id=skip_case_id,
            case_id=case_id,
            gq_treshold=gq_treshold,
            max_window=max_window,
        )
    except (SyntaxError, CaseError, IOError) as error:
        LOG.warning(error)
        ctx.abort()
    
    LOG.info("Nr variants inserted: %s", nr_inserted)
    LOG.info("Time to insert variants: {0}".format(
                datetime.now() - start_inserting))
    
    if ensure_index:
        adapter.ensure_indexes()
    else:
        adapter.check_indexes()
    
