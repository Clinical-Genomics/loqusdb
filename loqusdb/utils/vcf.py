import logging
import os

from cyvcf2 import VCF
from loqusdb.build_models.variant import get_variant_id
from loqusdb.exceptions import VcfError

LOG = logging.getLogger(__name__)
VALID_ENDINGS = [".vcf", ".gz", ".bcf"]


def add_headers(vcf_obj, nr_cases=None, sv=False):
    """Add loqus specific information to a VCF header

    Args:
        vcf_obj(cyvcf2.VCF)
    """

    vcf_obj.add_info_to_header(
        {
            "ID": "Obs",
            "Number": "1",
            "Type": "Integer",
            "Description": "The number of observations for the variant",
        }
    )
    if not sv:
        vcf_obj.add_info_to_header(
            {
                "ID": "Hom",
                "Number": "1",
                "Type": "Integer",
                "Description": "The number of observed homozygotes",
            }
        )
        vcf_obj.add_info_to_header(
            {
                "ID": "Hem",
                "Number": "1",
                "Type": "Integer",
                "Description": "The number of observed hemizygotes",
            }
        )
    if nr_cases:
        case_header = "##NrCases={}".format(nr_cases)
        vcf_obj.add_to_header(case_header)
    # head.add_version_tracking("loqusdb", version, datetime.now().strftime("%Y-%m-%d %H:%M"))
    return


def get_file_handle(file_path):
    """Return cyvcf2 VCF object

    Args:
        file_path(str)

    Returns:
        vcf_obj(cyvcf2.VCF)
    """
    LOG.debug("Check if file end is correct")

    if not os.path.exists(file_path):
        raise IOError("No such file:{0}".format(file_path))

    if os.path.splitext(file_path)[-1] not in VALID_ENDINGS:
        raise IOError("Not a valid vcf file name: {}".format(file_path))

    return VCF(file_path)


def get_vcf(file_path):
    """Yield variants from a vcf file

    Args:
        file_path(str)

    Yields:
        vcf_obj(cyvcf2.VCF): An iterable with cyvcf2.Variant

    """

    vcf_obj = get_file_handle(file_path)

    return vcf_obj


def check_sorting(previous_chrom, previous_pos, current_chrom, current_pos):
    """docstring for check_sorting"""
    pass


def check_vcf(vcf_path, expected_type="snv"):
    """Check if there are any problems with the vcf file

    Args:
        vcf_path(str)
        expected_type(str): 'sv' or 'snv'

    Returns:
        vcf_info(dict): dict like
        {
            'nr_variants':<INT>,
            'variant_type': <STR> in ['snv', 'sv'],
            'individuals': <LIST> individual positions in file
        }
    """
    LOG.info("Check if vcf is on correct format...")

    vcf = VCF(vcf_path)
    individuals = vcf.samples
    variant_type = None

    previous_pos = None
    previous_chrom = None

    posititon_variants = set()

    nr_variants = 0
    for nr_variants, variant in enumerate(vcf, 1):

        # Check the type of variant
        current_type = "sv" if variant.var_type == "sv" else "snv"
        if not variant_type:
            variant_type = current_type

        # Vcf can not include both snvs and svs
        if variant_type != current_type:
            raise VcfError("Vcf includes a mix of snvs and svs")

        current_chrom = variant.CHROM
        current_pos = variant.POS

        # We start with a simple id that can be used by SV:s
        variant_id = "{0}_{1}".format(current_chrom, current_pos)
        # For SNVs we can create a proper variant id with chrom_pos_ref_alt
        if variant_type == "snv":
            variant_id = get_variant_id(variant)

        # Initiate variables
        if not previous_chrom:
            previous_chrom = current_chrom
            previous_pos = current_pos
            posititon_variants = {variant_id}
            continue

        # Update variables if new chromosome
        if current_chrom != previous_chrom:
            previous_chrom = current_chrom
            previous_pos = current_pos
            posititon_variants = {variant_id}
            continue

        if variant_type == "snv":
            # Check if variant is unique
            if current_pos == previous_pos:
                if variant_id in posititon_variants:
                    raise VcfError("Variant {0} occurs several times" " in vcf".format(variant_id))
                else:
                    posititon_variants.add(variant_id)
            # Check if vcf is sorted
            else:
                if not current_pos >= previous_pos:
                    raise VcfError("Vcf if not sorted in a correct way")
                previous_pos = current_pos
                # Reset posititon_variants since we are on a new position
                posititon_variants = {variant_id}

    if variant_type != expected_type:
        raise VcfError(
            "VCF file does not only include {0}s, please check vcf {1}".format(
                expected_type.upper(), vcf_path
            )
        )

    LOG.info("Vcf file %s looks fine", vcf_path)
    LOG.info("Nr of variants in vcf: {0}".format(nr_variants))
    LOG.info("Type of variants in vcf: {0}".format(variant_type))

    return {
        "nr_variants": nr_variants,
        "variant_type": variant_type,
        "individuals": individuals,
    }
