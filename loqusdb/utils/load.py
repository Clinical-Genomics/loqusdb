# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from loqusdb.vcf_tools import (get_formated_variant, get_vcf)
from loqusdb.utils import (get_family)
from loqusdb.exceptions import CaseError

logger = logging.getLogger(__name__)

def load_database(adapter, variant_file, family_file, family_type='ped',
                  skip_case_id=False, gq_treshold=None, case_id=None):
    """Load the database with a case and its variants
            
            Args:
                  adapter
                  variant_file(str)
                  family_file(str)
                  family_type(str)
                  skip_case_id(bool)
 
    """

    vcf = get_vcf(variant_file)
    
    with open(family_file, 'r') as family_lines:
        family = get_family(
            family_lines=family_lines, 
            family_type=family_type
        )

    family_id = family.family_id
    
    if case_id:
        family_id = case_id

    if not family.affected_individuals:
        logger.warning("No affected individuals could be found in ped file")
    
    logger.info("Found affected individuals in ped file: {0}"
                .format(', '.join(family.affected_individuals)))

    load_family(
        adapter=adapter,
        case_id=family_id,
        vcf_path=variant_file
    )

    load_variants(  
        adapter=adapter, 
        family_id=family_id, 
        individuals=family.individuals,
        vcf=vcf, 
        skip_case_id=skip_case_id,
        gq_treshold=gq_treshold,
    )
    

def load_variants(adapter, family_id, individuals, vcf, skip_case_id=False, gq_treshold=None):
    """Load variants for a family into the database.

    Args:
        adapter (loqusdb.plugins.Adapter): initialized plugin
        family_id (str): unique family identifier
        inidividuals (List[str]): list to match individuals
        vcf (iterable(dict)): An iterable variant dictionaries
        skip_case_id (bool): whether to include the case id on variant level 
                             or not
    """
    gq_treshold = gq_treshold or 20
    nr_of_variants = 0
    nr_of_inserted = 0

    start_inserting = datetime.now()
    chrom_time = datetime.now()
    current_chrom = None
    new_chrom = None

    if skip_case_id:
        family_id = None

    # Loop over the variants in the vcf
    for variant in vcf:
            
        nr_of_variants += 1
        
        #Creates a variant that is ready to insert into the database
        formated_variant = get_formated_variant(
                        variant=variant,
                        individuals=individuals,
                        family_id=family_id,
                        gq_treshold=gq_treshold,
                    )

        if formated_variant:
            nr_of_inserted += 1
            adapter.add_variant(variant=formated_variant)
            
            new_chrom = formated_variant.get('chrom')

            if new_chrom != current_chrom:
                if current_chrom:
                    logger.info("Chromosome {0} done".format(current_chrom))
                    logger.info("Time to load chromosome {0}: {1}".format(
                        current_chrom, datetime.now()-chrom_time))
                    logger.info("Start parsing chromosome {0}".format(new_chrom))
                else:
                    logger.info("Start parsing chromosome {}".format(new_chrom))
            
                current_chrom = new_chrom
                chrom_time = datetime.now()

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
    case = {'case_id': case_id, 'vcf_path': vcf_path}
    adapter.add_case(case)
