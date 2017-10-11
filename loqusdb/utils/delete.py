# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from loqusdb.utils import (get_case, get_vcf)
from loqusdb.build_models import (build_case, build_variant)

logger = logging.getLogger(__name__)


def delete(adapter, variant_file, family_file, family_type='ped', case_id=None):
    """Delete a case and all of it's variants from the database"""
    
    vcf = get_vcf(variant_file)

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

    vcf_individuals = vcf.samples
    ind_positions = {}
    for i, ind_id in enumerate(vcf_individuals):
        ind_positions[ind_id] = i

    adapter.delete_case(case_obj)
    
    delete_variants(
        adapter=adapter,
        vcf=vcf,
        ind_positions=ind_positions,
        family_id=family_id,
        individuals=[ind['ind_id'] for ind in case_obj['individuals']]
    )

def delete_variants(adapter, vcf, ind_positions, family_id, individuals):
    """Delete variants for a case in the database
    
    Args:
        adapter (loqusdb.plugins.Adapter)
        vcf (iterable(dict))
        ind_positions(dict)
        family_id (str)
    
    Returns:
        nr_of_deleted (int): Number of deleted variants
    """
    nr_of_deleted = 0
    start_deleting = datetime.now()
    chrom_time = datetime.now()
    current_chrom = None
    new_chrom = None
    
    for variant in vcf:
        formated_variant = get_formated_variant(
            variant=variant,
            ind_positions=ind_positions,
            individuals=individuals,
            family_id=family_id
        )
        
        if formated_variant:
            new_chrom = formated_variant.get('chrom')
            
            adapter.delete_variant(formated_variant)
            nr_of_deleted += 1
            
            if new_chrom != current_chrom:
                if current_chrom:
                    logger.info("Chromosome {0} done".format(current_chrom))
                    logger.info("Time to delete chromosome {0}: {1}".format(
                        current_chrom, datetime.now()-chrom_time))
                    logger.info("Start deleting chromosome {0}".format(new_chrom))
                else:
                    logger.info("Start deleting chromosome {}".format(new_chrom))
            
                current_chrom = new_chrom
                chrom_time = datetime.now()


    return nr_of_deleted
