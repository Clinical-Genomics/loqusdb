from loqusdb.build_models.variant import get_coords, build_variant
from loqusdb.constants import GRCH37, GRCH38


def test_build_het_variant(het_variant, case_obj):
    variant_obj = build_variant(variant=het_variant, case_obj=case_obj, genome_build=GRCH37)
    assert variant_obj["chrom"] == het_variant.CHROM
    assert variant_obj["homozygote"] == 0
    assert variant_obj["hemizygote"] == 0


def test_get_coords_for_BND(bnd_variant):
    coords = get_coords(bnd_variant, True, GRCH37)
    assert coords["pos"] == coords["end"]
    assert coords["sv_length"] == float("inf")
    assert coords["sv_type"] == "BND"


def test_build_het_variant_grch38(het_variant, case_obj):
    variant_obj = build_variant(variant=het_variant, case_obj=case_obj, genome_build=GRCH38)
    assert variant_obj["chrom"] == het_variant.CHROM
    assert variant_obj["homozygote"] == 0
    assert variant_obj["hemizygote"] == 0


def test_get_coords_for_BND_grch38(bnd_variant):
    coords = get_coords(bnd_variant, True, GRCH38)
    assert coords["pos"] == coords["end"]
    assert coords["sv_length"] == float("inf")
    assert coords["sv_type"] == "BND"
