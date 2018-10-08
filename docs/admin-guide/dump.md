# Dumping a database

Loqus have a command to dump a database to a zipped file. 
This command just wraps the mongo command dump with some defaults.

```bash
$loqusdb dump --help
Usage: loqusdb dump [OPTIONS]

  Dump the database to a zipped file.

  Default filename is loqusdb.<todays date>.gz (e.g loqusdb.19971004.gz)

Options:
  -f, --filename PATH  If custom named file is to be used
  --help               Show this message and exit.
```