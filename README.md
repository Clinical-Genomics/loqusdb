# loqusdb [![Build Status][travis-image]][travis-url] 

Small tool to setup a local variant database.

Right now **locusdb** uses [mongodb][mongodb] as backend for 
storing variants but there should not be a huge difference to use another
database manager.

## Installation ##

`pip install loqusdb`

or

```
$git clone https://github.com/moonso/loqusdb
$cd loqusdb
$pip install --editable .
```

## Idea ##

Tool to keep track of what variants that have been seen and in what families they have been observed.
This is **NOT** a tool to create a true frequency database.
It will basically count the number of times we have seen a variant in any individual.
We will also keep track of the variants that have been seen in a homozygous or hemizygous state.

Variants are stored by providing a vcf file and a (ped or ped like)family file.

Loqusdb will first check if the vcf file looks ok.

The tool will then check all variants if they have been observed in any of the individuals in the family.

When the variants are added:

- Either the variant exists, in this case we increase the number of observations with one
- Or this variant has not ben seen before, then the variant is added to database


## Command Line Interface ##

```
$ loqusdb
Usage: loqusdb [OPTIONS] COMMAND [ARGS]...

  loqusdb: manage a local variant count database.

Options:
  -db, --database TEXT   [default: loqusdb]
  -u, --username TEXT
  -p, --password TEXT
  -port, --port INTEGER  Specify the port where to look for the mongo
                         database.  [default: 27017]
  -h, --host TEXT        Specify the host where to look for the mongo
                         database.  [default: localhost]
  -b, --backend [mongo]  Specify what backend to use.  [default: mongo]
  -c, --conn_host TEXT   Used for testing.  [default: mongodb://]
  -l, --logfile PATH     Path to log file. If none logging is printed to
                         stderr.
  -v, --verbose
  --version              Show the version and exit.
  --help                 Show this message and exit.

Commands:
  cases     Display cases in database
  delete    Delete the variants of a family
  export    Export variants to VCF format
  index     Add indexes to database
  load      Load the variants of a family
  migrate   Migrate an old loqusdb instance
  variants  Display variants in database
  wipe      Wipe a loqusdb instance
```


## Database ##

### Mongo ###

The collections looks like:

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

[travis-url]: https://travis-ci.org/moonso/loqusdb?branch=master
[travis-image]: https://img.shields.io/travis/moonso/loqusdb/master.svg?style=flat-square
[mongodb]: https://www.mongodb.org
