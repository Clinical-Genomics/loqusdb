# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from .vcf import get_vcf
from .case import get_case
from loqusdb.build_models import (build_case, build_variant)

LOG = logging.getLogger(__name__)


def delete(adapter, variant_file, family_file, family_type='ped', case_id=None):
    """Delete a case and all of it's variants from the database
    
    Args:
        adapter: Connection to database
        variant_file(str): Path to variant file
        family_file(str): Path to family file
        family_type(str): Format of family file
        nr_variants(int): number of variants in vcf
        skip_case_id(bool): If no case information should be added to variants
        gq_treshold(int): If only quality variants should be considered
        case_id(str): If different case id than the one in family file should be used
    
    """
    # Get a cyvcf2.VCF object
    vcf_obj = get_vcf(variant_file)

    # Parse the family file infromation
    with open(family_file, 'r') as family_lines:
        family = get_case(
            family_lines=family_lines, 
            family_type=family_type
        )

    case_id = case_id or family.family_id

    case_obj = build_case(
        case=family, 
        case_id=case_id
        )

    vcf_individuals = vcf_obj.samples
    ind_positions = {}
    for i, ind_id in enumerate(vcf_individuals):
        ind_positions[ind_id] = i

    adapter.delete_case(case_obj)
    
    delete_variants(
        adapter=adapter,
        vcf_obj=vcf_obj,
        ind_positions=ind_positions,
        case_id=case_id,
        individuals=[ind['ind_id'] for ind in case_obj['individuals']]
    )

def delete_variants(adapter, vcf_obj, ind_positions, case_id, individuals):
    """Delete variants for a case in the database
    
    Args:
        adapter(loqusdb.plugins.Adapter)
        vcf_obj(iterable(dict))
        ind_positions(dict)
        case_id(str)
    
    Returns:
        nr_of_deleted (int): Number of deleted variants
    """
    nr_of_deleted = 0
    start_deleting = datetime.now()
    chrom_time = datetime.now()
    current_chrom = None
    new_chrom = None
    
    for variant in vcf_obj:
        formated_variant = build_variant(
            variant=variant,
            ind_positions=ind_positions,
            individuals=individuals,
            case_id=case_id,
        )
        
        if not formated_variant:
            continue
        
        new_chrom = formated_variant.get('chrom')
        adapter.delete_variant(formated_variant)
        nr_of_deleted += 1
        
        if not current_chrom:
            LOG.info("Start deleting chromosome {}".format(new_chrom))
            current_chrom = new_chrom
            chrom_time = datetime.now()
            continue
        
        if new_chrom != current_chrom:
            LOG.info("Chromosome {0} done".format(current_chrom))
            LOG.info("Time to delete chromosome {0}: {1}".format(
                current_chrom, datetime.now()-chrom_time))
            LOG.info("Start deleting chromosome {0}".format(new_chrom))


    return nr_of_deleted
