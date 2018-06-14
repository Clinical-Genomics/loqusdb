from loqusdb.build_models import build_variant

def test_build_het_variant(het_variant, case_obj):
    variant_obj = build_variant(
        variant = het_variant,
        case_obj = case_obj
    )
    assert variant_obj['chrom'] == het_variant.CHROM
    assert variant_obj['homozygote'] == 0
    assert variant_obj['hemizygote'] == 0