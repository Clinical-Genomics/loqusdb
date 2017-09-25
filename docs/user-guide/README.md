# loqusdb user guide

loqusdb is a tool to store and query snv/indel variants on a large scale. It can be continuosly updated with new family information and queried with positions or regions.

## Observations

As mentioned loqusdb is not a frequency database that keeps track on all alleles observed in a population. Instead loqusdb is used to keep track of what variants that have been observed, in what state they where observed and in what individuals or families they where observed. loqusdb was developed to aid in rare variant analysies and therefore information about single variants are extremely important. If, for example, there is a potentially disease causing variant in a patient we could ask loqusdb if it was seen before, if loqusdb then tells us that it has been observed in a homozygous state 2 times before we could either exclude the variant or solve 2 more cases.

### Counting observations

Variants are only counted once per family, regardless of how many individuals it was observed in. This is to avoid the situation where a large family could have a great impact on a rare variant.