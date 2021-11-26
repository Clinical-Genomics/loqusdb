# -*- coding: utf-8 -*-


class Variant(dict):
    """Represent a Variant.

    snv/indels and svs differ quite a lot, we are here representing them with the same object.
    snv/indels will miss some of the information
    """

    def __init__(
        self,
        chrom,
        pos,
        end,
        ref,
        alt,
        variant_id=None,
        end_chrom=None,
        sv_type=None,
        sv_len=None,
        case_id=None,
        observations=0,
        homozygote=0,
        hemizygote=0,
        is_sv=False,
        id_column=None,
    ):
        super(Variant, self).__init__(
            _id=variant_id,
            variant_id=variant_id,
            chrom=chrom,
            pos=pos,
            end=end,
            ref=ref,
            alt=alt,
            end_chrom=end_chrom,
            sv_type=sv_type,
            sv_len=sv_len,
            case_id=case_id,
            observations=observations,
            homozygote=homozygote,
            hemizygote=hemizygote,
            is_sv=is_sv,
            id_column=id_column,
        )
