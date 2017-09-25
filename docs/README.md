# loqusdb

A tool to setup a local variant database.

Right now **locusdb** uses [mongodb][mongodb] as backend for 
storing variants but there should not be a huge difference to use another
database manager.

## Idea ##

Tool to keep track of *what* variants that have been seen, in what *families* and what *state* they have been observed.
This is **NOT** a tool to create a true frequency database.
**loqusdb** will basically count the number of times we have seen a variant in any individual.
We will also keep track of the variants that have been seen in a homozygous or hemizygous state.

Loqusdb is is used both as a live resource that continuos gets filled with new information and can be queried at any time. One could also create a vcf dump to annotate new variants.

Variants are stored by providing a vcf file and a (ped or ped like)family file.

Loqusdb will first check if the vcf file looks ok.

The tool will then check all variants if they have been observed in any of the individuals in the family.

When the variants are added:

- Either the variant exists, in this case we increase the number of observations with one
- Or this variant has not ben seen before, then the variant is added to database



[mongodb]: https://www.mongodb.org