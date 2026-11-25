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

or for mobile element insertions, one file per element

```
$loqusdb export --variant-type mei --freq --mei-type ALU -o loqusdb_alu.vcf
$loqusdb export --variant-type mei --freq --mei-type L1 -o loqusdb_l1.vcf
```

MEIs are exported as generic `<INS:ME>` records, with the element in `MEINFO` (e.g.
`MEINFO=ALU,.,.,.`). This matches the per element MEI frequency databases used with
`svdb --query`, which only matches records with identical ALT types, e.g.

```
svdb --query --bnd_distance 150 --overlap -1 --in_occ Obs --in_frq Frq \
  --out_occ loqusdb_alu_obs --out_frq loqusdb_alu_frq --db loqusdb_alu.vcf --query_vcf case_mei.vcf
```
