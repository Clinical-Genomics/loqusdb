# Loading a case

Variants are loaded in a case context, this way it becomes possible to trace back where we have observed a variation.
VCF files usually does not hold family information, this is why we use a [ped][ped] file.

When loading a case for the first time one could do any of the following:

1. **Load a case with a SNV file**
1. **Load a case with a SV file**
1. **Load a case with a SNV file and a SV file**

It is possible to add a file after a case is loaded with `loqusdb update`


A case is loaded with:

```
$loqusdb load --help
Usage: loqusdb load [OPTIONS]

  Load the variants of a case

  A variant is loaded if it is observed in any individual of a case If no
  family file is provided all individuals in vcf file will be considered.

Options:
  --variant-file <vcf_file>       Load a VCF with SNV/INDEL Variants
  --sv-variants <sv_vcf_file>     Load a VCF with Structural Variants
  -f, --family-file <ped_file>
  -t, --family-type [ped|alt|cmms|mip]
                                  If the analysis use one of the known setups,
                                  please specify which one.  [default: ped]
  -c, --case-id TEXT              If a different case id than the one in ped
                                  file should be used
  -s, --skip-case-id              Do not store case information on variants
                                  [default: False]
  --ensure-index                  Make sure that the indexes are in place
  --gq-treshold INTEGER           Treshold to consider variant  [default: 20]
  -m, --max-window INTEGER        Specify the maximum window size for svs
                                  [default: 2000]
  --check-profile PATH            Apply sample profiling for the samples,
                                  using the variants in this vcf
  --hard-threshold FLOAT          profile hamming distance to rejecting load
                                  (0-1)
  --soft-threshold FLOAT          profile hamming distance to store similar
                                  individuals (0-1)
  --help                          Show this message and exit.
```

Loqusdb will check that the individuals in ped file exists in vcf file and then add all the variants to database.
**If no .ped file is provided when loading a case in loqusdb, then variants for all samples found in the VCF file(s) will be loaded. In this case it will be necessary to provide a case name for this group of samples by using the `--case-id` option**.

# Command line example 

A few demo files could be used to test a loqusdb instance. They are included in the tests folder, under [fixtures][fixtures].

To load all variants for a case by providing both a VCF file containing SNV variants and a VCF file containing SV variants, use the following command:

`loqusdb --uri mongodb://<user>:<password>@<host>:<port> --database <database_name> --load --variant-file tests/fixtures/643594.clinical.vcf.gz --sv-variants tests/fixtures/643594.clinical.SV.vcf --case-id 643594`

where `643594` in the command above is an arbitrary name assigned to the group of samples present in the VCF file.


[fixtures]: https://github.com/Clinical-Genomics/loqusdb/tree/master/tests/fixtures
[ped]: http://zzz.bwh.harvard.edu/plink/data.shtml#ped
