#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine
"""Based on https://github.com/kennethreitz/setup.py"""

import io
import os

from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
from setuptools import find_packages, setup

# Package meta-data.
NAME = "loqusdb"
DESCRIPTION = "Store observations of vcf variants in a mongodb"
URL = "https://github.com/moonso/loqusdb"
EMAIL = "mans.magnusson@scilifelab.com"
AUTHOR = "Måns Magnusson"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "2.6.8"

requirements = [
    requirement.requirement
    for requirement in parse_requirements(filename="./requirements.txt", session=PipSession())
]


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests",)),
    entry_points={
        "console_scripts": ["loqusdb = loqusdb.__main__:base_command"],
    },
    install_requires=requirements,
    include_package_data=True,
    license="MIT",
    keywords=["vcf", "variants"],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
