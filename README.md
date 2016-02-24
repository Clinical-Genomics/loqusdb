# loqusdb [![Build Status][travis-image]][travis-url] 

Small tool to setup a local variant database.

Right now **locusdb** uses [mongodb][mongodb] as backend for 
storing variants but there should not be a huge difference to use another
database manager.

## Idea ##

We want to keep track of the variants that have been seen in affected individuals.
This is not a tool for solving the problem with frequencies.
It will basically count the number if times we have seen a variant in affected individuals.
Since we have a fairly large number of affected individuals we will be able to use this tool to ignore variants that have been seen many times.
We will also keep track of the variants that have been seen in a homozygous state in affected individuals. 

Variants are stored by providing a vcf file and a family file or a family id.

The tool will select one affected individual per family and insert counts for the variants of this individual.

When the variants are added:

- Either the variant exists, in this case we increase the number of observations with one
- Or this variant has not ben seen before, then the variant is added to database


## Command Line Interface ##





[travis-url]: https://travis-ci.org/moonso/loqusdb?branch=master
[travis-image]: https://img.shields.io/travis/moonso/loqusdb/master.svg?style=flat-square
[mongodb]: https://www.mongodb.org
