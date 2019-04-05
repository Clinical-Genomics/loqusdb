#Profile samples

To ensure that there are no sample duplicates in the database, the profiling
feature can be used. Profiling of samples is based on a list of SNPs,
having a high minor allele frequency (MAF). Each sample loaded into the database will
assessed for its genotype on these variant positions. This list of SNPs are chosen
and loaded to the database by the user.

The user can load a custom set of high MAF SNPs that will be used in
profiling.

Upon loading a new case, the user choses to activate the profiling feature
with the --check-profile option when [loading](./loading.md). Here the user
provides a VCF file that contains variant calls for each of the predefined
high-MAF SNPs. If no call is found for a SNP, the sample will be assumed to
be homozygous for the reference allele at this position. The user may define
a --hard-threshold, meaning if any existing profile has a similarity greater
than this (based on the hamming distance between compared profiles) to any of
the loaded samples, the case will not be loaded. Similarly a --soft-threshold
can be set, meaning if any similarity greater than this is found, the case may
still be loaded, but the similar samples in the database will be stated for the
loaded samples. 


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
