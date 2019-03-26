#Profile samples

To ensure that there are no sample duplicates in the database, the profiling
feature can be used. Profiling of samples is based on a list of SNPs,
having a high minor allele frequency. Each sample loaded into the database will
assessed for its genotype on these variant positions. This list of SNPs are chosen
and loaded to the database by the user.

Upon loading a new case, the user choses to activate the profiling feature
with the --check-profile flag when [loading](./loading.md).

```
$loqusdb profile --help
Usage: loqusdb profile [OPTIONS]

  Command for profiling of samples. User may upload variants used in
  profiling from a vcf, update the profiles for all samples, and get some
  stats from the profiles in the database.

  Profiling is used to monitor duplicates in the database. The profile is
  based on the variants in the 'profile_variant' collection, assessing the
  genotypes for each sample at the position of these variants.

Options:
  --variant-file PATH        a vcf containing the SNPs that is used in
                             profiling
  --update                   updates the profiles of all the sample in the
                             database
  --stats                    Checks some statistics of the profiles in the
                             database
  --profile-threshold FLOAT  Used with --stats option to determine the number
                             of matching profiles with a similarity greater
                             than given threshold
  --help                     Show this message and exit.

```
