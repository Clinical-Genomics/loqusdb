#!/usr/bin/env python
# encoding: utf-8
"""
run_loqusdb.py

Script manipulating the frequency database

Created by Måns Magnusson on 2015-09-30.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.
"""

from __future__ import (print_function)

import click
import logging
from pkg_resources import iter_entry_points

from loqusdb import __version__, logger
from loqusdb.log import init_log, LEVELS


###         This is the main script         ###

@click.group()
@click.option('-l', '--logfile',
                    type=click.Path(exists=False),
                    help=u"Path to log file. If none logging is "\
                          "printed to stderr."
)
@click.option('-v', '--verbose', 
                count=True,
                default=0,
                help=u"Increase output verbosity. Can be used multiple times, eg. -vv"
)
@click.version_option(__version__)
def cli(logfile, verbose):
    """Tool for manipulating a local variant frequency database
    
    """
    init_log(
        logger = logger, 
        filename = logfile, 
        loglevel = loglevel
    )

for entry_point in iter_entry_points('loqusdb.subcommands'):
    cli.add_command(entry_point.load())

if __name__ == '__main__':
    cli()
