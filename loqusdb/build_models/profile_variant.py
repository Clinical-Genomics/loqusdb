import logging

from loqusdb.build_models.variant import get_variant_id

from loqusdb.models import ProfileVariant


LOG = logging.getLogger(__name__)


def get_maf(variant):
    """
    Gets the MAF (minor allele frequency) tag from the info field for the
    variant.

    Args:
        variant (cyvcf2.Variant)

    Returns:
        maf (float): Minor allele frequency

    """

    return variant.INFO.get("MAF")


def build_profile_variant(variant, keep_chr_prefix=None):
    """Returns a ProfileVariant object

    Args:
        variant (cyvcf2.Variant)
        keep_chr_prefix(bool): Retain chr/CHR/Chr prefix when present

    Returns:
        variant (models.ProfileVariant)
    """

    chrom = variant.CHROM
    if not keep_chr_prefix:
        if chrom.startswith(("chr", "CHR", "Chr")):
            chrom = chrom[3:]

    pos = int(variant.POS)

    variant_id = get_variant_id(variant, keep_chr_prefix)

    ref = variant.REF
    alt = variant.ALT[0]

    maf = get_maf(variant)

    profile_variant = ProfileVariant(
        variant_id=variant_id, chrom=chrom, pos=pos, ref=ref, alt=alt, maf=maf, id_column=variant.ID
    )

    return profile_variant
