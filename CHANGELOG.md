# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

About changelog [here](https://keepachangelog.com/en/1.0.0/)

## [2.7.25]
### Fixed
- Update poetry lockfile with current versions of dependencies, fixing some issues that dependabot noticed

## [2.7.24]
### Changed
- Migrate from deprecated setuptools resources to importlib resources

## [2.7.23]
### Fixed
- Automation includes docs publishing

## [2.7.22]
### Changed
- update export logic to better handle chromosomes for genome build GRCh38
  
## [2.7.21]
### Changed
- variant query using the `variant` command will now check the database using alternative representations of the chromosome (with or without the 'chr' prefix) if the variant is not found with the provided representation.

## [2.7.20]
### Added
- Representation of chromsomes from GRCh38

## [2.7.19]
### Added
- Flag to retain chr/CHR/Chr prefixes when they are present

## [2.7.18]
### Added
- `ignore-gq-if-unset` flag to ignore GQ threshold check when GQ or QUAL field is unset for some variants in a VCF file.

## [2.7.17]
### Added
- Flag to skip GQ check on SV files

## [2.7.16]
### Fixed 
- Fixed changelog

## [2.7.15]
### Fixed
- For export, NrCases now reflects the number of cases with variants of the type specified by `--variant-type`

## [2.7.14]
### Added
- GitHub workflow for ChangeLog reminders 
### Fixed
- Fixed bumpversion changelog rule - attempted to anyway (#148)

## [2.7.13]
### Changed
- Update bumpversion config to also update the changelog version on bump (#147)

## [2.7.12]
### Changed
- Update the description of the Frq INFO tag to include information about the number of cases as well. (#144)

## [2.7.11]
### Changed
- Add linters (#143)

## [2.7.10]
### Changed
- Add codeowners (#142)

## [2.7.9]
### Changed
-Fix bump action (#141)

## [2.7.8]
### Changed
- Fix Bump action (#137)

## [2.7.7]
### Fixed
- Update to setuptools >= v.70 to address a security issue in the `package_index` module

## [2.7.6]
### Fixed
- Updated issue templates

## [2.7.4]
## Changed
- When using QUAL values, treat . as 0 quality

## [2.7.3]
### Added
- Basic cli tests touching fixed deprecated code
### Changed
- Unfreezed PyMongo in requirements.txt
- Replaced deprecated pymongo `.count()` function with `count_documents()` in code.

## [2.7.2]
### Fixed
- `Deprecated config in setup.cfg` error when installing the package

## [2.7.1]
### Added
- Script to correct contig name
- Expanded instructions on how to set up an instance and load data into database
### Changed
- GitHub actions run tests using MongoDB versions 3.2, 4.4 and 5.0
### Fixed
- Restore command accepts custom database name
- Restore command uses either database URI or host:port params

## [2.5.2]

### Changed
- Convert version to string
- Use Github Actions for running CI instead of Travis

## [2.5.1]

### Added
- Option to add observation frequencies to exported VCF (--freq)

## [2.5]

### Added
- Profiling feature added. Each sample gets a profile based on the genotypes for
a set of high maf variants.
- High maf variants used in profiling is loaded into DB via CLI
- Reject loading a case if a similar profile already exists for any of the samples
- Statistics of the profiles in DB can be generated through CLI
- use bulk operations when deleting variants
- Compatible with GRCh38
- Option to include case count when querying for a variant

### Fixed
- Use correct fields in index

## [2.3]

### Added
- Use bulk updates when inserting snvs

## [2.2]

### Added
- CLI function to annotate variants
- CLI functionality to dump and restore a database

## [2.1]

### Fixed
- Fix bug with inserting variants

### [2.0]

### Added
- Adds structural variants to loqus
