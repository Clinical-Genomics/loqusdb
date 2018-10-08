# Restore a database

It is possible to load all information from a dumped loqusdb instance.
This command just wraps the mongo command `mongo restore`
Loqusdb is shipped with a database instance that includes structural variants from ~740 1000G individuals.
Those have been called with [manta][manta], [tiddit][tiddit] and [CNVnator][cnvnator] 
and the calls are merged with [svdb][svdb]. 
If no file is pointed at `loqusdb restore` will use this database as default.

```bash
Usage: loqusdb restore [OPTIONS]

  Restore the database from a zipped file.

  Default is to restore from db dump in loqusdb/resources/

Options:
  -f, --filename PATH  If custom named file is to be used
  --help               Show this message and exit.
```

[manta]: https://github.com/Illumina/manta
[tiddit]: https://github.com/SciLifeLab/TIDDIT
[svdb]: https://github.com/J35P312/SVDB
[cnvnator]: https://github.com/abyzovlab/CNVnator