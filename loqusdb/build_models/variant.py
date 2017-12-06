import logging

from pprint import pprint as pp

from loqusdb.models import Variant 
from loqusdb.exceptions import CaseError

LOG = logging.getLogger(__name__)

# These are coordinate for the pseudo autosomal regions in GRCh37
PAR = {
    'Y': [[10001, 2649520], [59034050, 59373566]],
    'X': [[60001, 2699520], [154931044, 155270560]]
}

GENOTYPE_MAP = {0: 'hom_ref', 1: 'het', 2: 'no_call', 3:'hom_alt'}

def check_par(chrom, pos):
    """Check if a coordinate is in the PAR region
    
        Args:
            chrom(str)
            pos(int)
    
        Returns:
            par(bool)
    """
    par = False
    
    for interval in PAR.get(chrom,[]):
        if (pos >= interval[0] and pos <= interval[1]):
            par = True
    
    return par
    

def get_variant_id(variant):
    """Get a variant id on the format chrom_pos_ref_alt"""
    variant_id = '_'.join([
            str(variant.CHROM),
            str(variant.POS),
            str(variant.REF),
            str(variant.ALT[0])
        ]
    )
    return variant_id

def build_variant(variant, case_obj, case_id=None, gq_treshold=None):
    """Return a Variant object
    
        Take a cyvcf2 formated variant line and return a Variant.
    
        If criterias are not fullfilled, eg. variant have no gt call or quality
        is below gq treshold then None.
        
        Args:
            variant(cyvcf2.Variant)
            case_obj(Case)
            case_id(str): The case id
            gq_treshold(int): Gq treshold
        
        Return:
            formated_variant(dict): A variant dictionary
    """
    variant_obj = None

    sv = False
    if variant.var_type == 'sv':
        sv = True

    chrom = variant.CHROM
    if chrom.startswith(('chr', 'CHR', 'Chr')):
        chrom = chrom[3:]
    
    pos = int(variant.POS)
    end_pos = variant.INFO.get('END')

    if end_pos:
        end = int(end_pos)
    else:
        end = int(variant.end)

    variant_id = get_variant_id(variant)

    ref = variant.REF
    alt = variant.ALT[0]

    end_chrom = chrom

    sv_type = variant.INFO.get('SVTYPE')
    length = variant.INFO.get('SVLEN')
    if length:
        sv_len = abs(length)
    else:
        sv_len = end - pos

    if sv_type == 'BND':
        other_coordinates = alt.strip('ACGTN[]').split(':')
        end_chrom = other_coordinates[0]
        if end_chrom.startswith(('chr', 'CHR', 'Chr')):
            end_chrom = end_chrom[3:]

        end = int(other_coordinates[1])

        #Set 'infinity' to length if translocation
        sv_len = float('inf')
        sv_type = 'BND'

    # Insertions often have length 0 in VCF
    if (sv_len == 0 and alt != '<INS>'):
        sv_len = len(alt)

    if (pos == end) and (sv_len > 0):
        end = pos + sv_len

    # These are integers that will be used when uploading
    found_homozygote = 0
    found_hemizygote = 0

    # Only look at genotypes for the present individuals
    if sv:
        found_variant = True
    else:
        found_variant = False
        for ind_obj in case_obj['individuals']:
            ind_id = ind_obj['ind_id']
            # Get the index position for the individual in the VCF
            ind_pos = ind_obj['ind_index']
            gq = int(variant.gt_quals[ind_pos])
            if (gq_treshold and gq < gq_treshold):
                continue

            genotype = GENOTYPE_MAP[variant.gt_types[ind_pos]]

            if genotype in ['het', 'hom_alt']:
                LOG.debug("Found variant")
                found_variant = True

                # If variant in X or Y and individual is male,
                # we need to check hemizygosity
                if chrom in ['X','Y'] and ind_obj['sex'] == 1:
                    if not check_par(chrom, pos):
                        LOG.debug("Found hemizygous variant")
                        found_hemizygote = 1

                if genotype == 'hom_alt':
                    LOG.debug("Found homozygote alternative variant")
                    found_homozygote = 1

    if found_variant:
        variant_obj = Variant(
            variant_id=variant_id,
            chrom=chrom,
            pos=pos,
            end=end,
            ref=ref,
            alt=alt,
            end_chrom=end_chrom,
            sv_type = sv_type,
            sv_len = sv_len,
            case_id = case_id,
            homozygote = found_homozygote,
            hemizygote = found_hemizygote,
            is_sv = sv,
        )

    return variant_obj