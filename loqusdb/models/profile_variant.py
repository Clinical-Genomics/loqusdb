class ProfileVariant(dict):
    """Represent a profile variant

    These variants will be used to profile samples, based on a samples genotype
    at these positions.
    """

    def __init__(self, variant_id, chrom, pos, ref, alt, maf, id_column=None):
        super(ProfileVariant, self).__init__(
            _id=variant_id, chrom=chrom, pos=pos, ref=ref, alt=alt, maf=maf, id_column=id_column
        )
