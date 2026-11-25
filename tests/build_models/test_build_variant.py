import pytest

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
    # No SVTYPE and cyvcf2 misclassifying as "snv": only the symbolic ALT is left to infer from.
    del_variant.INFO = {"END": del_variant.end}
    del_variant.var_type = "snv"

    assert infer_sv_type(del_variant) == "DEL"
    assert get_coords(del_variant, True, GRCH37)["sv_type"] == "DEL"


def test_build_variant_from_symbolic_alt(del_variant, case_obj):
    # Same cyvcf2-misclassification scenario, verified end-to-end through build_variant.
    del_variant.INFO = {"END": del_variant.end}
    del_variant.var_type = "snv"

    variant_obj = build_variant(variant=del_variant, case_obj=case_obj, genome_build=GRCH37)

    assert variant_obj["is_sv"] is True
    assert variant_obj["sv_type"] == "DEL"


def test_infer_sv_type_preserves_cyvcf2_svtype(del_variant):
    assert infer_sv_type(del_variant) == "DEL"


@pytest.mark.parametrize("svtype", ["DUP:TANDEM", "TDUP", "IDUP"])
def test_infer_sv_type_collapses_subtyped_svtype(duptandem_variant, svtype):
    # TIDDIT style SVTYPE values collapse to their primary type
    duptandem_variant.INFO["SVTYPE"] = svtype

    assert infer_sv_type(duptandem_variant) == "DUP"


def test_infer_sv_type_collapses_alias_from_symbolic_alt(duptandem_old_tiddit_variant):
    # Without SVTYPE, an old TIDDIT <TDUP> ALT still collapses to DUP
    duptandem_old_tiddit_variant.INFO = {"END": duptandem_old_tiddit_variant.end}

    assert infer_sv_type(duptandem_old_tiddit_variant) == "DUP"


def test_infer_sv_type_from_single_breakend(single_bnd_variant):
    # No SVTYPE, no brackets: only the trailing "." marks this as an unpaired breakend.
    single_bnd_variant.INFO = {}

    assert infer_sv_type(single_bnd_variant) == "BND"


def test_get_coords_for_single_breakend(single_bnd_variant):
    # No partner locus is encoded, so end coordinates fall back to the variant's own position.
    coords = get_coords(single_bnd_variant, True, GRCH37)
    assert coords["pos"] == coords["end"]
    assert coords["end_chrom"] == coords["chrom"]
    assert coords["sv_length"] == float("inf")
    assert coords["sv_type"] == "BND"
