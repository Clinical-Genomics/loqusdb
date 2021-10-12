# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

About changelog [here](https://keepachangelog.com/en/1.0.0/)

## [unreleased]
### Added
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
