# loqusdb

Software to setup and manage local variant observations database.

Right now **locusdb** uses [mongodb][mongodb] as backend for 
storing variants but it should be doable to adapt the code to another backend.

## Idea ##

Tool to keep track of *what* variants that have been seen, in what *families* and what *state* they have been observed.
This is **NOT** a tool to create a true frequency database.
**loqusdb** will basically count the number of times we have seen a variant in any individual.
We will also keep track of the variants that have been seen in a [homozygous][homozygote] or [hemizygous][hemizygote] state.

Loqusdb is is used both as a live resource that continuously gets filled with new information and can be queried at any time. 
One could also create a [vcf export][export] to annotate new variants.

Variants are stored by providing a vcf file and a (ped or ped like)family file.

Loqusdb will first check if the vcf file looks ok.

The tool will then check all variants if they have been observed in any of the individuals in the family.

When the variants are added:

- Either the variant exists, in this case we increase the number of observations with one
- Or this variant has not ben seen before, then the variant is added to database

## SNVs and SVs

Previously loqusdb could only handle SNVs and INDELs, from now on it is also capable of handling structural variants.
Since structural variants have a much lower call quality than snvs they need to be regarded as inexact calls. 
These are therefore grouped into clusters with some extensions, intervals, around the endpoints. The interval size is 
a function of the size of the SV.



[mongodb]: https://www.mongodb.org
[homozygote]: https://en.wikipedia.org/wiki/Zygosity#Homozygous
[hemizygote]: https://en.wikipedia.org/wiki/Zygosity#Hemizygous
[export]: user-guide/exporting.md