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

### Filtering on observations

To export only variants observed in at most a given number of individuals, use `--max-obs`.
For example, to export variants with `Obs <= 5`:

```
$loqusdb export --max-obs 5
```

The same option works for SVs, for example `$loqusdb export --variant-type sv --max-obs 5`.
The filter is applied in the database query, so common variants are not read at all.

### Including case IDs

By default the exported VCF does not contain case IDs. To add the cases each variant was observed in, use `--include-case-ids`:

```
$loqusdb export --include-case-ids
```

The cases are written to the INFO field as `Cases=`, for example `Obs=2;Cases=case1,case2`. Characters that are not allowed in VCF INFO values (whitespace, `;`, `=` and `,`) are replaced with `_`.

Only the most recent cases are kept for each variant. Variants store up to 50 case IDs, so `Obs` can be higher than the number of listed cases.
