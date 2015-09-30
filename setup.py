try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
import pkg_resources

# For making things look nice on pypi:
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, RuntimeError):
    long_description = 'Tool for annotating patterns of genetic inheritance in Variant Call Format (VCF) files.'


# with open('README.txt') as file:
#     long_description = file.read()

setup(name='loqusdb',
    version='0.1',
    description='Store frequencies of vcf variants in a mongodb',
    author = 'Mans Magnusson',
    author_email = 'mans.magnusson@scilifelab.se',
    url = 'http://github.com/moonso/loqusdb',
    license = 'MIT License',
    install_requires=[
        'click',
        'pymongo',
        'pytest',
        'mongomock',
    ],
    packages=find_packages(exclude=('tests*', 'docs', 'examples')),
    
    entry_points= {
        "console_scripts" : [
        "loqusdb = loqusdb.commands.run_loqusdb:cli",
        ],
        "loqusdb.subcommands": [
            "load = loqusdb.commands.load_variants:cli"
        ]
    },
    keywords = ['vcf', 'variants'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    long_description = long_description,
)