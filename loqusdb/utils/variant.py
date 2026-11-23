import logging
import re

LOG = logging.getLogger(__name__)


def format_case_ids(case_ids):
    """Make case ids safe to use as a VCF INFO value

    VCF INFO values can not contain whitespace, ';' or '=', so these are replaced with '_'.

    Args:
        case_ids(list(str))

    Returns:
        str: Comma separated case ids
    """
    cleaned = []
    for case_id in case_ids:
        cleaned.append(re.sub(r"[\s;=,]", "_", str(case_id)))
    return ",".join(cleaned)


def format_info(variant, variant_type="snv", nr_cases=None, add_freq=False, case_ids=None):
    """Format the info field for SNV variants

    Args:
        variant(dict)
        variant_type(str): snv or sv
        nr_cases(int)
        add_freq(bool)
        case_ids(list(str)): Cases the variant was observed in, added as Cases if given

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

    if case_ids:
        vcf_info += f";Cases={format_case_ids(case_ids)}"

    # This is SV specific
    if variant_type == "sv":
        int((variant["pos_left"] + variant["pos_right"]) / 2)
        end = int((variant["end_left"] + variant["end_right"]) / 2)

        if not variant["sv_type"] == "BND":
            vcf_info += f";SVTYPE={variant['sv_type']};END={end};SVLEN={variant['length']}"
        else:
            vcf_info += ";SVTYPE=BND"

    return vcf_info


def format_variant(
    variant, variant_type="snv", nr_cases=None, add_freq=False, include_case_ids=False
):
    """Convert variant information to a VCF formated string

    Args:
        variant(dict)
        variant_type(str)
        nr_cases(int)
        add_freq(bool)
        include_case_ids(bool): Add the cases the variant was observed in to INFO

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

    info = None

    case_ids = variant.get("families") if include_case_ids else None
    info = format_info(
        variant,
        variant_type=variant_type,
        nr_cases=nr_cases,
        add_freq=add_freq,
        case_ids=case_ids,
    )

    return f"{chrom}\t{pos}\t.\t{ref}\t{alt}\t.\t.\t{info}"
