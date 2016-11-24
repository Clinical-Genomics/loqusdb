# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from loqusdb.vcf_tools import (get_formated_variant, get_vcf)
from loqusdb.utils import (get_family)

logger = logging.getLogger(__name__)


def delete(adapter, variant_file, family_file, family_type='ped', case_id=None):
    """Delete a case and all of it's variants from the database"""
    
    vcf = get_vcf(variant_file)

    with open(family_file, 'r') as family_lines:
        family = get_family(
            family_lines=family_lines, 
            family_type=family_type
        )
    
    family_id = family.family_id
    if case_id:
        family_id = case_id

    individuals = family.individuals
    
    delete_family(
        adapter=adapter,
        family_id=family_id
    )
    
    delete_variants(
        adapter=adapter,
        vcf=vcf,
        family_id=family_id,
        individuals=individuals
    )

def delete_family(adapter, family_id):
    """Delete a case object from the database"""
    case = {'case_id': family_id}
    adapter.delete_case(case)

def delete_variants(adapter, vcf, family_id, individuals):
    """Delete variants for a case in the database
    
        Args:
            adapter (loqusdb.plugins.Adapter)
            vcf (iterable(dict))
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
