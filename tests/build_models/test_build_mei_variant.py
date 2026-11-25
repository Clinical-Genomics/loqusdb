from loqusdb.build_models.variant import build_mei_variant, get_mei_coords, get_mei_type


def test_get_mei_type_from_meinfo(cyvcf2_variant):
    ## GIVEN a RetroSeq style MEI with a generic ALT and the element in MEINFO
    cyvcf2_variant.ALT = ["<INS:ME>"]
    cyvcf2_variant.INFO = {"SVTYPE": "INS", "MEINFO": "ALU,21898411,21898412,NA"}
    ## THEN the element is taken from MEINFO
    assert get_mei_type(cyvcf2_variant) == "INS:ME:ALU"


def test_get_mei_type_from_meinfo_tuple(cyvcf2_variant):
    ## GIVEN MEINFO parsed as a tuple
    cyvcf2_variant.ALT = ["<INS:ME>"]
    cyvcf2_variant.INFO = {"SVTYPE": "INS", "MEINFO": ("l1", "1", "2", "NA")}
    ## THEN the element is upper cased
    assert get_mei_type(cyvcf2_variant) == "INS:ME:L1"


def test_get_mei_type_from_alt(cyvcf2_variant):
    ## GIVEN a MEI with the element in the ALT, and a different element in MEINFO
    cyvcf2_variant.ALT = ["<INS:ME:SVA>"]
    cyvcf2_variant.INFO = {"SVTYPE": "INS", "MEINFO": "ALU,1,2,NA"}
    ## THEN the ALT takes precedence
    assert get_mei_type(cyvcf2_variant) == "INS:ME:SVA"


def test_get_mei_type_from_svtype(cyvcf2_variant):
    ## GIVEN a MELT style record where SVTYPE is the element
    cyvcf2_variant.ALT = ["<INS:ME>"]
    cyvcf2_variant.INFO = {"SVTYPE": "ALU"}
    assert get_mei_type(cyvcf2_variant) == "INS:ME:ALU"


def test_get_mei_type_unknown_element(cyvcf2_variant):
    ## GIVEN a MEI without any element information
    cyvcf2_variant.ALT = ["<INS:ME>"]
    cyvcf2_variant.INFO = {"SVTYPE": "INS"}
    ## THEN the generic type is returned
    assert get_mei_type(cyvcf2_variant) == "INS:ME"


def test_get_mei_coords_point_event(cyvcf2_variant):
    ## GIVEN a MEI with chr prefix and an END that differs from POS
    cyvcf2_variant.CHROM = "chr1"
    cyvcf2_variant.POS = 1000
    cyvcf2_variant.ALT = ["<INS:ME:ALU>"]
    cyvcf2_variant.INFO = {"SVTYPE": "INS", "END": 1300, "SVLEN": 281}
    ## WHEN getting the coordinates
    coords = get_mei_coords(cyvcf2_variant, keep_chr_prefix=False)
    ## THEN the MEI is a point event on the stripped chromosome
    assert coords["chrom"] == coords["end_chrom"] == "1"
    assert coords["pos"] == coords["end"] == 1000
    assert coords["sv_length"] == 281
    assert coords["sv_type"] == "INS:ME:ALU"


def test_build_mei_variant(cyvcf2_variant, case_id):
    ## GIVEN a MEI
    cyvcf2_variant.ALT = ["<INS:ME>"]
    cyvcf2_variant.INFO = {"SVTYPE": "INS", "MEINFO": "HERV,1,2,NA"}
    ## WHEN building the variant
    variant = build_mei_variant(cyvcf2_variant, case_id=case_id)
    ## THEN it is an SV of the element type, belonging to the case
    assert variant["is_sv"] is True
    assert variant["sv_type"] == "INS:ME:HERV"
    assert variant["case_id"] == case_id
    assert variant["end"] == variant["pos"] == cyvcf2_variant.POS
