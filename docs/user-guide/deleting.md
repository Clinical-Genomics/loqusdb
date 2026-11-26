# Delete a case

When a case is deleted all observations from the case in question will be deleted.
Use the same quality settings as the original small-variant load. For example,
if the case was loaded with the CLI default GQ threshold of 20, run:

```sh
loqusdb delete --case-id CASE_ID --gq-threshold 20
```

You can also identify the case with `-f <FAM_file>`. Pass `--qual-gq` and
`--ignore-gq-if-unset` if the original load used them. Omitting
`--gq-threshold` or passing 0 disables threshold filtering during deletion.
