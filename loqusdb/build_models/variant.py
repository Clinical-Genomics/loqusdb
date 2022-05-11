import logging
from collections import namedtuple

from loqusdb.constants import CHROM_TO_INT, GENOTYPE_MAP, GRCH37, PAR
from loqusdb.models import Variant

LOG = logging.getLogger(__name__)

Position = namedtuple("Position", "chrom pos")


# These are coordinate for the pseudo autosomal regions in GRCh37


def check_par(chrom, pos, genome_build=None):
    """Check if a coordinate is in the PAR region

    Args:
        chrom(str)
        pos(int)

    Returns:
        par(bool)
    """
    if genome_build is None:
        genome_build = GRCH37
    return any(
        pos >= interval[0] and pos <= interval[1] for interval in PAR[genome_build].get(chrom, [])
    )


def get_variant_id(variant):
    """Get a variant id on the format chrom_pos_ref_alt"""
    chrom = variant.CHROM
    if chrom.lower().startswith("chr"):
        chrom = chrom[3:]
    return "_".join([str(chrom), str(variant.POS), str(variant.REF), str(variant.ALT[0])])


def is_greater(a, b):
    """Check if position a is greater than position b
    This will look at chromosome and position.

    For example a position where chrom = 2 and pos = 300 is greater than a position where
    chrom = 1 and pos = 1000

    If any of the chromosomes is outside [1-22,X,Y,MT] we can not say which is biggest.

    Args:
        a,b(Position)

    Returns:
        bool: True if a is greater than b
    """

    a_chrom = CHROM_TO_INT.get(a.chrom, 0)
    b_chrom = CHROM_TO_INT.get(b.chrom, 0)

    if a_chrom == 0 or b_chrom == 0:
        return False

    if a_chrom > b_chrom:
        return True

    return a_chrom == b_chrom and a.pos > b.pos


def get_coords(variant):
    """Returns a dictionary with position information

    Args:
        variant(cyvcf2.Variant)

    Returns:
        coordinates(dict)
    """
    coordinates = {
        "chrom": None,
        "end_chrom": None,
        "sv_length": None,
        "sv_type": None,
        "pos": None,
        "end": None,
    }
    chrom = variant.CHROM
    if chrom.startswith(("chr", "CHR", "Chr")):
        chrom = chrom[3:]
    coordinates["chrom"] = chrom
    end_chrom = chrom

    pos = int(variant.POS)
    alt = variant.ALT[0]

    # Get the end position
    # This will be None for non-svs
    end_pos = variant.INFO.get("END")
    end = int(end_pos) if end_pos else int(variant.end)
    coordinates["end"] = end

    sv_type = variant.INFO.get("SVTYPE")
    length = variant.INFO.get("SVLEN")
    sv_len = abs(length) if length else end - pos
    # Translocations will sometimes have a end chrom that differs from chrom
    if sv_type == "BND":
        other_coordinates = alt.strip("ATCGN").strip("[]").split(":")
        end_chrom = other_coordinates[0]
        if end_chrom.startswith(("chr", "CHR", "Chr")):
            end_chrom = end_chrom[3:]

        end = int(other_coordinates[1])

        # Set 'infinity' to length if translocation
        sv_len = float("inf")

    # Insertions often have length 0 in VCF
    if sv_len == 0 and alt != "<INS>":
        sv_len = len(alt)

    if (pos == end) and (sv_len > 0) and sv_len != float("inf"):
        end = pos + sv_len

    position = Position(chrom, pos)
    end_position = Position(end_chrom, end)

    # If 'start' is greater than 'end', switch positions
    if is_greater(position, end_position):
        end_chrom = position.chrom
        end = position.pos

        chrom = end_position.chrom
        pos = end_position.pos

    coordinates["end_chrom"] = end_chrom
    coordinates["pos"] = pos
    coordinates["end"] = end
    coordinates["sv_length"] = sv_len
    coordinates["sv_type"] = sv_type

    return coordinates


def build_variant(variant, case_obj, case_id=None, gq_treshold=None, genome_build=None):
    """Return a Variant object

    Take a cyvcf2 formated variant line and return a models.Variant.

    If criterias are not fullfilled, eg. variant have no gt call or quality
    is below gq treshold then return None.

    Args:
        variant(cyvcf2.Variant)
        case_obj(Case): We need the case object to check individuals sex
        case_id(str): The case id
        gq_treshold(int): Genotype Quality treshold

    Return:
        formated_variant(models.Variant): A variant dictionary
    """
    variant_obj = None

    sv = False
    # Let cyvcf2 tell if it is a Structural Variant or not
    if variant.var_type == "sv":
        sv = True

    # chrom_pos_ref_alt
    variant_id = get_variant_id(variant)

    ref = variant.REF
    # ALT is an array in cyvcf2
    # We allways assume splitted and normalized VCFs
    alt = variant.ALT[0]

    coordinates = get_coords(variant)
    chrom = coordinates["chrom"]
    pos = coordinates["pos"]

    # These are integers that will be used when uploading
    found_homozygote = 0
    found_hemizygote = 0

    # Only look at genotypes for the present individuals
    if sv:
        found_variant = True
    else:
        found_variant = False
        for ind_obj in case_obj["individuals"]:
            ind_id = ind_obj["ind_id"]
            # Get the index position for the individual in the VCF
            ind_pos = ind_obj["ind_index"]
            gq = int(variant.gt_quals[ind_pos])
            if gq_treshold and gq < gq_treshold:
                continue

            genotype = GENOTYPE_MAP[variant.gt_types[ind_pos]]

            if genotype in ["het", "hom_alt"]:
                LOG.debug("Found variant")
                found_variant = True

                # If variant in X or Y and individual is male,
                # we need to check hemizygosity
                if (
                    chrom in ["X", "Y"]
                    and ind_obj["sex"] == 1
                    and not check_par(chrom, pos, genome_build=genome_build)
                ):
                    LOG.debug("Found hemizygous variant")
                    found_hemizygote = 1

                if genotype == "hom_alt":
                    LOG.debug("Found homozygote alternative variant")
                    found_homozygote = 1

    if found_variant:
        variant_obj = Variant(
            variant_id=variant_id,
            chrom=chrom,
            pos=pos,
            end=coordinates["end"],
            ref=ref,
            alt=alt,
            end_chrom=coordinates["end_chrom"],
            sv_type=coordinates["sv_type"],
            sv_len=coordinates["sv_length"],
            case_id=case_id,
            homozygote=found_homozygote,
            hemizygote=found_hemizygote,
            is_sv=sv,
            id_column=variant.ID,
        )

    return variant_obj
