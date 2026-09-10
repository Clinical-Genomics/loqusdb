from loqusdb.build_models.variant import build_variant, get_coords, infer_sv_type
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


def test_infer_sv_type_from_symbolic_alt(del_variant):
    del_variant.INFO = {"END": del_variant.end}
    del_variant.var_type = "snv"

    assert infer_sv_type(del_variant) == "DEL"
    assert get_coords(del_variant, True, GRCH37)["sv_type"] == "DEL"


def test_build_variant_from_symbolic_alt(del_variant, case_obj):
    del_variant.INFO = {"END": del_variant.end}
    del_variant.var_type = "snv"

    variant_obj = build_variant(variant=del_variant, case_obj=case_obj, genome_build=GRCH37)

    assert variant_obj["is_sv"] is True
    assert variant_obj["sv_type"] == "DEL"


def test_infer_sv_type_preserves_cyvcf2_svtype(del_variant):
    assert infer_sv_type(del_variant) == "DEL"
