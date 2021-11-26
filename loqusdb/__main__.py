#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
loqusdb.__main__
~~~~~~~~~~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``loqusdb`` (if installed)
or ``python -m loqusdb`` (no install required).
"""
import sys

from loqusdb.commands import base_command

if __name__ == "__main__":
    # exit using whatever exit code the CLI returned
    sys.exit(base_command())
