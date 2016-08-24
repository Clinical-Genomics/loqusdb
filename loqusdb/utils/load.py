# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from cyvcf2 import VCF

from loqusdb.vcf_tools import (get_formated_variant)
from loqusdb.utils import (get_family)

logger = logging.getLogger(__name__)

def load_database(adapter, variant_file, family_file, family_type='ped', bulk_insert=False):
    """Load the database with a case and its variants"""
    
    vcf = VCF(variant_file)
        
    family = get_family(
        family_lines=family_file, 
        family_type=family_type
    )

    if not family.affected_individuals:
        logger.warning("No affected individuals could be found in ped file")
    
    logger.info("Found affected individuals in ped file: {0}"
                .format(', '.join(family.affected_individuals)))
    
    logger.debug("Check if individuals from ped file exists in vcf...")
    if not set(vcf.samples).intersection(set(family.individuals)):
        logger.warning("Individuals in ped file does not exist in variant file")
        ctx.abort()

    load_family(
        adapter=adapter,
        case=family
    )

    load_variants(  
        adapter=adapter, 
        family_id=family.family_id, 
        individuals=family.individuals,
        vcf=vcf, 
        bulk_insert=bulk_insert,
        vcf_path=variant_path
    )
    

def load_variants(adapter, family_id, individuals, vcf, bulk_insert=False):
    """Load variants for a family into the database.

    Args:
        adapter (loqusdb.plugins.Adapter): initialized plugin
        family_id (str): unique family identifier
        inidividuals (List[str]): list to match individuals
        vcf (cyvcf2.VCF): A cyvcf2 vcf object
        bulk_insert (bool): whether to insert in bulk or one-by-one
    """
    # This is the header line with mandatory vcf fields
    header = []
    nr_of_variants = 0
    nr_of_inserted = 0

    start_inserting = datetime.now()
    start_ten_thousand = datetime.now()

    variants = []
    # Loop over the variants in the vcf
    for variant in vcf:
        line = line.rstrip()
        nr_of_variants += 1
        #Creates a variant that is ready to insert into the database
        formated_variant = get_formated_variant(
                        variant=variant,
                        individuals=individuals,
                        family_id=family_id
                    )
            
        if formated_variant:
            nr_of_inserted += 1
            if bulk_insert:
                variants.append(formated_variant)
            else:
                adapter.add_variant(variant=formated_variant)

            if nr_of_variants % 10000 == 0:
                logger.info("{0} of variants processed".format(nr_of_variants))
                logger.info("Time to insert last 10000: {0}".format(
                    datetime.now()-start_ten_thousand))
                start_ten_thousand = datetime.now()

            if nr_of_variants % 100000 == 0:
                if bulk_insert:
                    adapter.add_bulk(variants)
                    variants = []

    if bulk_insert:
        adapter.add_bulk(variants)

    logger.info("Nr of variants in vcf: {0}".format(nr_of_variants))
    logger.info("Nr of variants inserted: {0}".format(nr_of_inserted))
    logger.info("Time to insert variants: {0}".format(datetime.now() -
                                                      start_inserting))

def load_family(adapter, case_id, vcf_path):
    """Load a case to the database
    
        The adapter will check if the case already exists before loading.
    
        Args:
            adapter (loqusdb.plugins.Adapter): initialized plugin
            case_id (str)
            vcf_path (str)
    """
    case = {'case_id': family_id, 'vcf_path': vcf_path}
    adapter.add_case(case)
