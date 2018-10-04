# -*- coding: utf-8 -*-
import os
import logging
import subprocess

from datetime import datetime

import click

from . import base_command

LOG = logging.getLogger(__name__)

@base_command.command('restore', short_help="Restore database from dump")
@click.option('-f' ,'--filename', 
                help='If custom named file is to be used',
                type=click.Path(exists=True),
                required=True
)
@click.pass_context
def restore(ctx, filename):
    """Restore the database from a zipped file.
    
    """
    
    if not os.path.isfile(filename):
        LOG.warning("File {} does not exist. Please point to a valid file".format(filename))
        ctx.abort()
    
    call = ['mongorestore', '--gzip', '--db', 'loqusdb', '--archive={}'.format(filename)]
    
    LOG.info('Restoring database...')
    start_time = datetime.now()
    try:
        completed = subprocess.run(call, check=True)
    except subprocess.CalledProcessError as err:
        LOG.warning(err)
        ctx.abort()
    
    LOG.info('Database restored succesfully')
    LOG.info('Time to restore database: {0}'.format(datetime.now()-start_time))
    
    