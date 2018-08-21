#Load a case

Variants are loaded in a case context, this is so that we can trace back where we have observed a variation. VCF files usually does not hold family information, this is why we use a [ped][ped] file.
A case is loaded with:

```
$loqusdb load <VCF> -f <FAM_file>
```

loqusdb will check that the individuals in ped file exists in vcf file and then add all the variants to database.


[ped]: http://zzz.bwh.harvard.edu/plink/data.shtml#ped 