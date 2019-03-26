import logging
import json

from loqusdb.models import ProfileVariant
from .variant import get_variant_id

LOG = logging.getLogger(__name__)

def get_maf(variant):
    """
        if ID CAF exists in INFO column, return the allele frequency for
        the alt allele. The CAF INFO tag from dbSNP is a Comma delimited list of
        allele frequencies based on 1000Genomes.

        Args:
            variant (cyvcf2.Variant)

        Returns:
            maf (float): Minor allele frequency 

    """

    if  not variant.INFO.get('CAF'):
        return None
    maf_list = json.loads(variant.INFO.get('CAF'))
    return maf_list[1]


def build_profile_variant(variant):
    """Returns a ProfileVariant object

    Args:
        variant (cyvcf2.Variant)

    Returns:
        variant (models.ProfileVariant)
    """

    chrom = variant.CHROM
    if chrom.startswith(('chr', 'CHR', 'Chr')):
        chrom = chrom[3:]

    pos = int(variant.POS)

    variant_id = get_variant_id(variant)

    ref = variant.REF
    alt = variant.ALT[0]

    maf = get_maf(variant)

    profile_variant = ProfileVariant(
        variant_id=variant_id,
        chrom=chrom,
        pos=pos,
        ref=ref,
        alt=alt,
        maf=maf,
        id_column = variant.ID
    )

    return profile_variant
