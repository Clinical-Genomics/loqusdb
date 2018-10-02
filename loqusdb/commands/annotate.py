import os
import logging
import click

from pprint import pprint as pp

from datetime import datetime

from loqusdb.exceptions import (VcfError)
from loqusdb.utils.load import load_database
from loqusdb.utils.vcf import (get_file_handle, check_vcf, add_headers)
from loqusdb.utils.annotate import (annotate_snvs)

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
    
    # nr_cases = adapter.cases().count()
    # LOG.info("Found {0} cases in database".format(nr_cases))

    adapter = ctx.obj['adapter']

    start_inserting = datetime.now()
    
    # try:
    for variant in annotate_snvs(adapter, vcf_obj):
        click.echo(variant)
    # except (Exception) as error:
    #     LOG.warning(error)
    #     ctx.abort()
    
    
