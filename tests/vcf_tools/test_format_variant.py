from loqusdb.build_models.variant import build_variant, GENOTYPE_MAP


def test_format_variant(het_variant, case_obj):
    ## GIVEN a parsed variant
    variant = het_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant
    formated_variant = build_variant(variant=variant, case_obj=case_obj, case_id=case_id)

    expected_id = "_".join([variant.CHROM, str(variant.POS), variant.REF, variant.ALT[0]])

    ## THEN assert it was built in a correct way
    assert formated_variant
    assert formated_variant["variant_id"] == expected_id
    assert formated_variant["chrom"] == variant.CHROM
    assert formated_variant["pos"] == variant.POS
    assert formated_variant["ref"] == variant.REF
    assert formated_variant["alt"] == variant.ALT[0]
    assert formated_variant["case_id"] == case_id
    assert formated_variant["homozygote"] == 0


def test_format_variant_no_gq(variant_no_gq, case_obj):
    ## GIVEN a variant without GQ
    variant = variant_no_gq
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant using a GQ treshold
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, gq_treshold=20
    )
    ## THEN assert that None is returned since requirements are not fulfilled
    assert formated_variant is None


def test_format_variant_chr_prefix(variant_chr, case_obj):
    ## GIVEN a variant with 'chr' prefix in chromosome name
    variant = variant_chr
    assert variant.CHROM.startswith("chr")
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant using a GQ treshold
    formated_variant = build_variant(
        variant=variant, case_obj=case_obj, case_id=case_id, gq_treshold=20
    )
    ## THEN assert that the 'chr' part has been stripped away
    assert formated_variant["chrom"] == variant.CHROM[3:]


def test_format_variant_no_family_id(het_variant, case_obj):
    ## GIVEN a parsed variant
    variant = het_variant
    case_id = case_obj["case_id"]
    ## WHEN parsing the variant telling that 'case_id' is None
    formated_variant = build_variant(variant=variant, case_obj=case_obj, case_id=None)
    ## THEN assert that case_id was not added
    assert formated_variant.get("case_id") == None
    assert formated_variant["homozygote"] == 0
    assert formated_variant["hemizygote"] == 0


def test_format_homozygote_variant(hom_variant, case_obj):
    ## GIVEN a parsed hom variant
    variant = hom_variant
    case_id = case_obj["case_id"]

    ## WHEN parsing the variant
    formated_variant = build_variant(variant=variant, case_obj=case_obj, case_id=case_id)

    ## THEN assert that the variant has hom count
    assert formated_variant["homozygote"] == 1
    assert formated_variant["hemizygote"] == 0


def test_format_hemizygote_variant(hem_variant, case_obj):
    ## GIVEN a parsed hemizygous variant
    variant = hem_variant
    case_id = case_obj["case_id"]

    ## WHEN parsing the variant
    formated_variant = build_variant(variant=variant, case_obj=case_obj, case_id=case_id)

    ## THEN assert that hemizygote count is 1
    assert formated_variant["homozygote"] == 0
    assert formated_variant["hemizygote"] == 1


def test_format_variant_no_call(variant_no_call, case_obj):
    ## GIVEN a parsed variant with no call in all individuals
    variant = variant_no_call
    case_id = case_obj["case_id"]

    for call in variant.gt_types:
        assert GENOTYPE_MAP[call] in ["no_call", "hom_ref"]

    ## WHEN parsing the variant
    formated_variant = build_variant(variant=variant, case_obj=case_obj, case_id=case_id)

    ## THEN assert that the result is None
    assert formated_variant is None
