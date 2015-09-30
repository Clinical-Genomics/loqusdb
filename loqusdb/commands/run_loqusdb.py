#!/usr/bin/env python
# encoding: utf-8
"""
run_loqusdb.py

Script manipulating the frequency database

Created by Måns Magnusson on 2015-09-30.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.
"""

from __future__ import (print_function)

import sys
import os
import click
import logging

from locusdb import __version__, logger
from locusdb.log import init_log, LEVELS


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
    """Tool for manipulating a variant frequency database
    
    """
    loglevel = LEVELS.get(min(verbose,2), "WARNING")
    init_log(
        logger = logger, 
        filename = logfile, 
        loglevel = loglevel
    )


if __name__ == '__main__':
    cli()
