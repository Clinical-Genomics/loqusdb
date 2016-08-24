# -*- coding: utf-8 -*-
import logging

from loqusdb.vcf_tools import (get_formated_variant, get_vcf)
from loqusdb.utils import (get_family)

logger = logging.getLogger(__name__)


def delete(adapter, variant_file, family_file, family_type='ped', 
            bulk_insert=False):
    """Delete a case and all of it's variants from the database"""
    
    vcf = get_vcf(variant_file)

    with open(family_file, 'r') as family_lines:
        family = get_family(
            family_lines=family_lines, 
            family_type=family_type
        )
    
    family_id = family.family_id
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
            vcf (cyvcf2.VCF)
            family_id (str)
        
        Returns:
            nr_of_deleted (int): Number of deleted variants
    """
    nr_of_deleted = 0
    for variant in vcf:
        formated_variant = get_formated_variant(
            variant=variant,
            individuals=individuals,
            family_id=family_id
        )
        
        if formated_variant:
            adapter.delete_variant(formated_variant)
            nr_of_deleted += 1

    return nr_of_deleted
