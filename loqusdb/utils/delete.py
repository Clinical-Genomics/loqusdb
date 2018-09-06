# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from .vcf import get_vcf
from .case import get_case
from loqusdb.build_models import (build_case, build_variant)

LOG = logging.getLogger(__name__)


def delete(adapter, variant_file, family_file, family_type='ped', case_id=None, case_obj=False, skip_case=False):
    """Delete a case and all of it's variants from the database.
    
    Args:
        adapter: Connection to database
        variant_file(str): Path to variant file
        family_file(str): Path to family file
        family_type(str): Format of family file
        case_id(str): If different case id than the one in family file should be used
        case_obj(models.Case)
        skip_case(bool): If update then change existing case in database to case_obj
    
    """
    # Get a cyvcf2.VCF object
    vcf_obj = get_vcf(variant_file)

    # Parse the family file infromation
    family = None
    family_id = None
    if family_file:
        with open(family_file, 'r') as family_lines:
            family = get_case(
                family_lines=family_lines, 
                family_type=family_type
            )
            family_id = family.family_id

    case_id = case_id or family_id

    case_obj = build_case(
        case=family,
        vcf_individuals=vcf_obj.samples,
        case_id=case_id,
    )
    
    if not skip_case:
        adapter.delete_case(case_obj)
    
    delete_variants(
        adapter=adapter,
        vcf_obj=vcf_obj,
        case_obj=case_obj,
        case_id=case_id,
    )

def delete_variants(adapter, vcf_obj, case_obj, case_id=None):
    """Delete variants for a case in the database
    
    Args:
        adapter(loqusdb.plugins.Adapter)
        vcf_obj(iterable(dict))
        ind_positions(dict)
        case_id(str)
    
    Returns:
        nr_deleted (int): Number of deleted variants
    """
    case_id = case_id or case_obj['case_id']
    nr_deleted = 0
    start_deleting = datetime.now()
    chrom_time = datetime.now()
    current_chrom = None
    new_chrom = None
    
    for variant in vcf_obj:
        formated_variant = build_variant(
            variant=variant,
            case_obj=case_obj,
            case_id=case_id,
        )
        
        if not formated_variant:
            continue
        
        new_chrom = formated_variant.get('chrom')
        adapter.delete_variant(formated_variant)
        nr_deleted += 1
        
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
            current_chrom = new_chrom


    return nr_deleted
