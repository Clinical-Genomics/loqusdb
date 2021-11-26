from loqusdb.build_models.variant import get_coords, build_variant


def test_build_het_variant(het_variant, case_obj):
    variant_obj = build_variant(variant=het_variant, case_obj=case_obj)
    assert variant_obj["chrom"] == het_variant.CHROM
    assert variant_obj["homozygote"] == 0
    assert variant_obj["hemizygote"] == 0


def test_get_coords_for_BND(bnd_variant):
    coords = get_coords(bnd_variant)
    assert coords["pos"] == coords["end"]
    assert coords["sv_length"] == float("inf")
    assert coords["sv_type"] == "BND"
