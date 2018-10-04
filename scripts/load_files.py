import logging
import click
import coloredlogs
import subprocess
from pathlib import Path
from copy import deepcopy
from datetime import datetime

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

LOG = logging.getLogger(__name__)

@click.command()
@click.option('-d', '--directory', 
    default='.',
    help="Specify the path to a directory if VCFs"
)
@click.option('--uri',
                help='Specify a mongodb uri'
)
@click.option('-v', '--verbose', is_flag=True)
@click.option('-c', '--count', is_flag=True, help="Count the variant files")
@click.pass_context
def cli(ctx, directory, uri, verbose, count):
    """Load all files in a directory."""
    # configure root logger to print to STDERR
    loglevel = "INFO"
    if verbose:
        loglevel = "DEBUG"
    coloredlogs.install(level=loglevel)
    
    p = Path(directory)
    
    if not p.is_dir():
        LOG.warning("{0} is not a valid directory".format(directory))
        ctx.abort()
    
    start_time = datetime.now()
    base_call = ['loqusdb']
    if uri:
        base_call.append('--uri')
        base_call.append(uri)
    base_call.append('load')
    
    nr_files = 0
    for nr_files,file_name in enumerate(list(p.glob('*.vcf')),1):
        call = deepcopy(base_call)
        case_id = file_name.stem.split('.')[0]
        call.append('--sv-variants')
        call.append(str(file_name))
        call.append('--case-id')
        call.append(case_id)
        if count:
            continue
        subprocess.run(call)
    LOG.info("%s files inserted", nr_files)
    LOG.info("Time to insert files: {}".format(datetime.now()-start_time))


if __name__=='__main__':
    cli()
