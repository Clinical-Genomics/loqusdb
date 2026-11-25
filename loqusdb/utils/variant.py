import logging

LOG = logging.getLogger(__name__)


def get_mei_element(mei_type):
    """Return the element of a MEI cluster type, e.g. ALU for INS:ME:ALU, or None if unknown"""
    parts = mei_type.split(":", 2)
    return parts[2] if len(parts) == 3 else None


def normalize_mei_type(mei_type):
    """Return a MEI cluster type from an element or type, e.g. Alu -> INS:ME:ALU"""
    mei_type = mei_type.upper()
    if mei_type.startswith("INS:ME"):
        return mei_type
    return f"INS:ME:{mei_type}"


def format_info(variant, variant_type="snv", nr_cases=None, add_freq=False):
    """Format the info field for SNV variants

    Args:
        variant(dict)
        variant_type(str): snv, sv or mei
        nr_cases(int)

    Returns:
        vcf_info(str): A VCF formated info field
    """

    observations = variant.get("observations", 0)

    homozygotes = variant.get("homozygote")
    hemizygotes = variant.get("hemizygote")

    vcf_info = f"Obs={observations}"
    if homozygotes:
        vcf_info += f";Hom={homozygotes}"
    if hemizygotes:
        vcf_info += f";Hem={hemizygotes}"

    if add_freq and nr_cases and nr_cases > 0:
        frequency = observations / nr_cases
        vcf_info += f";Frq={frequency:.5f}"

    if variant_type == "mei":
        vcf_info += ";SVTYPE=INS"
        # The cluster type is e.g. INS:ME:ALU. The element goes in MEINFO, whose start, end and
        # polarity refer to the element sequence and are unknown to loqusdb
        element = get_mei_element(variant["sv_type"])
        if element:
            vcf_info += f";MEINFO={element},.,.,."

    # This is SV specific
    if variant_type == "sv":
        int((variant["pos_left"] + variant["pos_right"]) / 2)
        end = int((variant["end_left"] + variant["end_right"]) / 2)

        if not variant["sv_type"] == "BND":
            vcf_info += f";SVTYPE={variant['sv_type']};END={end};SVLEN={variant['length']}"
        else:
            vcf_info += ";SVTYPE=BND"

    return vcf_info


def format_variant(variant, variant_type="snv", nr_cases=None, add_freq=False):
    """Convert variant information to a VCF formated string

    Args:
        variant(dict)
        variant_type(str)
        nr_cases(int)

    Returns:
        vcf_variant(str)
    """
    chrom = variant.get("chrom")
    pos = variant.get("start")

    ref = variant.get("ref")
    alt = variant.get("alt")

    if variant_type == "sv":
        pos = int((variant["pos_left"] + variant["pos_right"]) / 2)
        end = int((variant["end_left"] + variant["end_right"]) / 2)
        ref = "N"

        if not variant["sv_type"] == "BND":
            alt = f"<{variant['sv_type']}>"
        else:
            alt = f"N]{variant['end_chrom']}:{end}]"

    if variant_type == "mei":
        pos = int((variant["pos_left"] + variant["pos_right"]) / 2)
        ref = "N"
        # Generic ALT, as in the per element MEI frequency databases used with svdb --query
        alt = "<INS:ME>"

    info = None

    info = format_info(variant, variant_type=variant_type, nr_cases=nr_cases, add_freq=add_freq)

    return f"{chrom}\t{pos}\t.\t{ref}\t{alt}\t.\t.\t{info}"
