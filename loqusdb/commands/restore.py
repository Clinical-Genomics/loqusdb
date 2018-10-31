# -*- coding: utf-8 -*-
import os
import logging
import subprocess

from datetime import datetime

import click

from . import base_command
from loqusdb.resources import background_path

LOG = logging.getLogger(__name__)

@base_command.command('restore', short_help="Restore database from dump")
@click.option('-f' ,'--filename', 
                help='If custom named file is to be used',
                type=click.Path(exists=True),
)
@click.pass_context
def restore(ctx, filename):
    """Restore the database from a zipped file.
    
    Default is to restore from db dump in loqusdb/resources/
    """
    filename = filename or background_path
    if not os.path.isfile(filename):
        LOG.warning("File {} does not exist. Please point to a valid file".format(filename))
        ctx.abort()
    
    call = ['mongorestore', '--gzip', '--db', 'loqusdb', '--archive={}'.format(filename)]
    
    LOG.info('Restoring database from %s', filename)
    start_time = datetime.now()
    try:
        completed = subprocess.run(call, check=True)
    except subprocess.CalledProcessError as err:
        LOG.warning(err)
        ctx.abort()
    
    LOG.info('Database restored succesfully')
    LOG.info('Time to restore database: {0}'.format(datetime.now()-start_time))
    
    