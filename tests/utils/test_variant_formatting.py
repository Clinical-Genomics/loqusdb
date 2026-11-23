from loqusdb.utils.variant import format_case_ids, format_info, format_variant


def test_format_info_snv_counts():
    """Test that SNV INFO contains observation counts"""
    ## GIVEN a variant observed in 3 individuals, one of them homozygous
    variant = {"observations": 3, "homozygote": 1, "hemizygote": 0}

    ## WHEN formatting the INFO field
    info = format_info(variant)

    ## THEN Obs and Hom are included and Hem is omitted since it is zero
    assert info == "Obs=3;Hom=1"


def test_format_info_snv_hemizygote():
    """Test that hemizygote counts are added to INFO"""
    ## GIVEN a variant with hemizygous observations
    variant = {"observations": 2, "hemizygote": 2}

    ## WHEN formatting the INFO field
    info = format_info(variant)

    ## THEN Hem is included
    assert info == "Obs=2;Hem=2"


def test_format_info_with_frequency():
    """Test that observation frequency is added when requested"""
    ## GIVEN a variant observed in 3 of 10 cases
    variant = {"observations": 3}

    ## WHEN formatting the INFO field with frequencies
    info = format_info(variant, nr_cases=10, add_freq=True)

    ## THEN Frq is the observations divided by the number of cases
    assert info == "Obs=3;Frq=0.30000"


def test_format_info_frequency_without_cases():
    """Test that no frequency is added when there are no cases"""
    ## GIVEN a variant and no case count
    variant = {"observations": 3}

    ## WHEN formatting the INFO field with frequencies
    info = format_info(variant, nr_cases=0, add_freq=True)

    ## THEN Frq is not included to avoid dividing by zero
    assert info == "Obs=3"


def test_format_info_sv_deletion():
    """Test that SV INFO contains type, end and length"""
    ## GIVEN a deletion observed in 2 individuals
    variant = {
        "observations": 2,
        "pos_left": 100,
        "pos_right": 200,
        "end_left": 300,
        "end_right": 400,
        "sv_type": "DEL",
        "length": 250,
    }

    ## WHEN formatting the INFO field as an SV
    info = format_info(variant, variant_type="sv")

    ## THEN the midpoint end, type and length are included
    assert info == "Obs=2;SVTYPE=DEL;END=350;SVLEN=250"


def test_format_info_sv_breakend():
    """Test that breakends only get SVTYPE in INFO"""
    ## GIVEN a breakend observed once
    variant = {
        "observations": 1,
        "pos_left": 100,
        "pos_right": 200,
        "end_left": 300,
        "end_right": 400,
        "sv_type": "BND",
        "length": 0,
    }

    ## WHEN formatting the INFO field as an SV
    info = format_info(variant, variant_type="sv")

    ## THEN only SVTYPE=BND is added
    assert info == "Obs=1;SVTYPE=BND"


def test_format_variant_snv():
    """Test that an SNV is converted to a VCF line"""
    ## GIVEN an SNV observed once
    variant = {"chrom": "1", "start": 100, "ref": "A", "alt": "C", "observations": 1}

    ## WHEN formatting the variant
    line = format_variant(variant)

    ## THEN a tab separated VCF record is returned
    assert line == "1\t100\t.\tA\tC\t.\t.\tObs=1"


def test_format_variant_sv_deletion():
    """Test that a deletion is converted to a VCF line with symbolic ALT"""
    ## GIVEN a deletion observed twice
    variant = {
        "chrom": "1",
        "observations": 2,
        "pos_left": 100,
        "pos_right": 200,
        "end_left": 300,
        "end_right": 400,
        "sv_type": "DEL",
        "length": 250,
    }

    ## WHEN formatting the variant as an SV
    line = format_variant(variant, variant_type="sv")

    ## THEN POS is the midpoint, REF is N and ALT is the symbolic allele
    assert line == "1\t150\t.\tN\t<DEL>\t.\t.\tObs=2;SVTYPE=DEL;END=350;SVLEN=250"


def test_format_variant_sv_breakend():
    """Test that a breakend ALT points to the end chromosome"""
    ## GIVEN a translocation breakend observed once
    variant = {
        "chrom": "1",
        "end_chrom": "2",
        "observations": 1,
        "pos_left": 100,
        "pos_right": 200,
        "end_left": 300,
        "end_right": 400,
        "sv_type": "BND",
        "length": 0,
    }

    ## WHEN formatting the variant as an SV
    line = format_variant(variant, variant_type="sv")

    ## THEN ALT is a breakend to the end chromosome and position
    assert line == "1\t150\t.\tN\tN]2:350]\t.\t.\tObs=1;SVTYPE=BND"


def test_format_info_with_case_ids():
    """Test that case ids are added to INFO when given"""
    ## GIVEN a variant observed in two cases
    variant = {"observations": 2}

    ## WHEN formatting the INFO field with case ids
    info = format_info(variant, case_ids=["case1", "case2"])

    ## THEN the cases are listed in the Cases field
    assert info == "Obs=2;Cases=case1,case2"


def test_format_info_without_case_ids():
    """Test that Cases is omitted by default"""
    ## GIVEN a variant with case information stored
    variant = {"observations": 2, "families": ["case1"]}

    ## WHEN formatting the INFO field without requesting case ids
    info = format_info(variant)

    ## THEN no Cases field is added
    assert info == "Obs=2"


def test_format_case_ids_sanitizes_reserved_characters():
    """Test that characters not allowed in INFO values are replaced"""
    ## GIVEN case ids containing whitespace, ';', '=' and ','
    case_ids = ["case 1", "case;2", "case=3", "case,4"]

    ## WHEN formatting the case ids
    formatted = format_case_ids(case_ids)

    ## THEN each reserved character is replaced with an underscore
    assert formatted == "case_1,case_2,case_3,case_4"


def test_format_variant_include_case_ids():
    """Test that a variant line includes its cases when requested"""
    ## GIVEN an SNV observed in one case
    variant = {
        "chrom": "1",
        "start": 100,
        "ref": "A",
        "alt": "C",
        "observations": 1,
        "families": ["case1"],
    }

    ## WHEN formatting the variant with case ids
    line = format_variant(variant, include_case_ids=True)

    ## THEN the case is part of the INFO field
    assert line == "1\t100\t.\tA\tC\t.\t.\tObs=1;Cases=case1"


def test_format_variant_default_hides_case_ids():
    """Test that case ids are not part of the default variant line"""
    ## GIVEN an SNV observed in one case
    variant = {
        "chrom": "1",
        "start": 100,
        "ref": "A",
        "alt": "C",
        "observations": 1,
        "families": ["case1"],
    }

    ## WHEN formatting the variant without case ids
    line = format_variant(variant)

    ## THEN the case is not included
    assert "case1" not in line
