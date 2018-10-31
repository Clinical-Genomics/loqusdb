# -*- coding: utf-8 -*-
import os
import logging
import subprocess

from datetime import datetime

import click

from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('dump', short_help="Dump the database")
@click.option('-f' ,'--filename', 
                help='If custom named file is to be used',
                type=click.Path(exists=False)
)
@click.pass_context
def dump(ctx, filename):
    """Dump the database to a zipped file.
    
    Default filename is loqusdb.<todays date>.gz (e.g loqusdb.19971004.gz)
    """
    
    if not filename:
        filename = "loqusdb.{}.gz".format(datetime.now().strftime('%Y%m%d'))
    
    if os.path.isfile(filename):
        LOG.warning("File {} already exists. Please remove file or change name with '--filename'".format(filename))
        ctx.abort()
    
    call = ['mongodump', '--gzip', '--db', 'loqusdb', '--archive={}'.format(filename)]
    
    LOG.info('dumping database...')
    start_time = datetime.now()
    try:
        completed = subprocess.run(call, check=True)
    except subprocess.CalledProcessError as err:
        LOG.warning(err)
        LOG.info("Deleting dump..")
        os.path.remove(filename)
        ctx.abort()
    
    LOG.info('Database dumped succesfully')
    LOG.info('Time to dump database: {0}'.format(datetime.now()-start_time))
    
    