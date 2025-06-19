from loqusdb.build_models.variant import build_variant
from loqusdb.constants import GRCH37, GRCH38


def test_format_indel(del_variant, case_obj):
    ## GIVEN a SV deletion
    variant = del_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )
    expected_id = "_".join([variant.CHROM, str(variant.POS), variant.REF, variant.ALT[0]])

    ## THEN assert the sv is parsed correct
    assert formated_variant
    assert formated_variant["variant_id"] == expected_id
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.INFO["END"]
    assert formated_variant["sv_len"] == abs(variant.INFO["SVLEN"])

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "DEL"
    assert formated_variant["case_id"] == case_id
    assert formated_variant["homozygote"] == 0
    assert formated_variant["hemizygote"] == 0


def test_format_indel_chrprefix(chr_del_variant, case_obj):
    ## GIVEN a SV deletion
    variant = chr_del_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id,
        genome_build=GRCH38,
        keep_chr_prefix=True,
    )
    expected_id = "_".join([variant.CHROM, str(variant.POS), variant.REF, variant.ALT[0]])

    ## THEN assert the sv is parsed correct
    assert formated_variant
    assert formated_variant["variant_id"] == expected_id
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.INFO["END"]
    assert formated_variant["sv_len"] == abs(variant.INFO["SVLEN"])

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "DEL"
    assert formated_variant["case_id"] == case_id
    assert formated_variant["homozygote"] == 0
    assert formated_variant["hemizygote"] == 0


def test_format_small_ins(small_insert_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = small_insert_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.POS + abs(variant.INFO["SVLEN"])
    assert formated_variant["sv_len"] == abs(variant.INFO["SVLEN"])

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "INS"


def test_format_small_ins_chrprefix(chr_small_insert_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = chr_small_insert_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id,
        genome_build=GRCH38,
        keep_chr_prefix=True,
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.POS + abs(variant.INFO["SVLEN"])
    assert formated_variant["sv_len"] == abs(variant.INFO["SVLEN"])

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "INS"


def test_format_insertion(insertion_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = insertion_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.INFO["END"]
    assert formated_variant["sv_len"] == 0

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "INS"


def test_format_insertion_chrprefix(chr_insertion_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = chr_insertion_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id,
        genome_build=GRCH38,
        keep_chr_prefix=True,
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.INFO["END"]
    assert formated_variant["sv_len"] == 0

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "INS"


def test_format_dup_tandem(duptandem_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = duptandem_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.INFO["END"]
    assert formated_variant["sv_len"] == abs(variant.INFO["SVLEN"])

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "DUP"


def test_format_dup_tandem_chrprefix(chr_duptandem_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = chr_duptandem_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id,
        genome_build=GRCH38,
        keep_chr_prefix=True,
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == variant.INFO["END"]
    assert formated_variant["sv_len"] == abs(variant.INFO["SVLEN"])

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "DUP"


def test_format_translocation(translocation_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = translocation_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, genome_build=GRCH37
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == "11"
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == 119123896
    assert formated_variant["sv_len"] == float("inf")

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "BND"


def test_format_translocation_chrprefix(chr_translocation_variant, case_obj):
    ## GIVEN a small insertion (This means that the insertion is included in ALT field)
    variant = chr_translocation_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id,
        genome_build=GRCH38,
        keep_chr_prefix=True,
    )

    ## THEN assert the sv is parsed correct
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["end_chrom"] == "11"
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["end"] == 119123896
    assert formated_variant["sv_len"] == float("inf")

    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["sv_type"] == "BND"
