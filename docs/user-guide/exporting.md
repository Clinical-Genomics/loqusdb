# Exporting variants

The variant can be exported with observations to the VCF format. This might come to use when annotating variants for analysis of new cases.
Since SNVs and SVs differs so much there are two different files for these.
Use command:

```
$loqusdb export
```
or for SV variants

```
$loqusdb export --variant-type sv
```
