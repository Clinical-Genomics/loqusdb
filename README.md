# loqusdb
[![Publish to PyPI](https://github.com/moonso/loqusdb/actions/workflows/build_and_publish.yml/badge.svg)](https://github.com/moonso/loqusdb/actions/workflows/build_and_publish.yml)
[![Coverage Status](https://coveralls.io/repos/github/moonso/loqusdb/badge.svg?branch=master)](https://coveralls.io/github/moonso/loqusdb?branch=master)
[![PyPI Version][pypi-img]][pypi-url]

Small tool to set up a local variant database.
If you find Loqusdb useful in your work, please cite the [article][publication].

Right now **Locusdb** uses [mongodb][mongodb] as backend for
storing variants, but there should not be a huge difference to use another
database manager.

## Installation ##


`poetry install`

or

```
$git clone https://github.com/moonso/loqusdb
$cd loqusdb
$poetry install
```

## Idea ##

Tool to keep track of what variants that have been seen and in what families they have been observed.
This is **NOT** a tool to create a true frequency database.
It will basically count the number of times we have seen a variant in any individual.
We will also keep track of the variants that have been seen in a homozygous or hemizygous state.

Variants are stored by providing a VCF file and a (ped or ped like) family file.

Loqusdb will first check if the VCF file adheres to the VCF format.

The tool will then check all variants if they have been observed in any of the individuals in the family.

When the variants are added:

- Either the variant exists, in this case we increase the number of observations with one
- Or this variant has not been seen before, then the variant is added to the database


## Command Line Interface ##

```
$ loqusdb
Usage: loqusdb [OPTIONS] COMMAND [ARGS]...

  loqusdb: manage a local variant count database.

Options:
  -db, --database TEXT            Defaults to 'loqusdb' if not specified
  -u, --username TEXT
  -p, --password TEXT
  -a, --authdb TEXT               If authentication should be done against
                                  another database than --database

  -port, --port INTEGER           Specify the port where to look for the mongo
                                  database.  [default: 27017]

  -h, --host TEXT                 Specify the host where to look for the mongo
                                  database.  [default: localhost]

  --uri TEXT                      Specify a mongodb uri
  -c, --config FILENAME           Use a config with db information
  -t, --test                      Used for testing. This will use a mongomock
                                  database.

  -g, --genome-build [GRCh37|GRCh38]
                                  Specify what genome build to use
  -v, --verbose
  --version                       Show the version and exit.
  --help                          Show this message and exit.

Commands:
  annotate  Annotate a VCF with observations
  cases     Display cases in database
  delete    Delete the variants of a family
  dump      Dump the database
  export    Export variants to VCF format
  identity  Search identity collection
  index     Add indexes to database
  load      Load the variants of a family
  migrate   Migrate an old loqusdb instance
  profile   Loads variants to be used in profiling
  restore   Restore database from dump
  update    Update an existing case with a new type of variants
  variants  Display variants in database
  wipe      Wipe a loqusdb instance
```


## Database ##

### Connecting ###

Connection can be specified on command line with `--database`, `--username`, `--password`, `--port`, `--host` and/or `--uri`. Or these options can be sent with a config file that can take the same options:

```yaml
uri: mongodb://loqusdb-username:loqusdb-pwd@localhost:27030/loqusdb-rd?authSource=admin
db_name: loqusdb_test
```
or
```yaml
host: localhost
port: 27030
username: loqusdb-username
password: loqusdb-pwd
authdb: admin
db_name: loqusdb_test
```

### Mongo ###

The collections are defined as follows:

**Case**

```python
{
    'case_id': 'case_id',
    'vcf_path': 'path_to_vcf'
}
```

**Variant**

```python
{
    '_id': 'variant_id',
    'chrom': 'CHROM',
    'start': postition,
    'end': end postition,
    'ref': reference base(s),
    'alt': alternative base(s),
    'homozygote': number_of_homozygotes,
    'hemizygote': number_of_hemizygotes,
    'observations': number_of_observations,
    'families': ['family_id', ...]
}
```

[mongodb]: https://www.mongodb.org
[publication]: https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-020-03609-z
[pypi-img]: https://img.shields.io/pypi/v/loqusdb.svg?style=flat-square
[pypi-url]: https://pypi.python.org/pypi/loqusdb/
