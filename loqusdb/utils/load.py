# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import click

from loqusdb.vcf_tools import (get_formated_variant, get_vcf)
from loqusdb.utils import (get_family)
from loqusdb.exceptions import CaseError

logger = logging.getLogger(__name__)

def load_database(adapter, variant_file, family_file, nr_variants=None, 
                  family_type='ped', skip_case_id=False, gq_treshold=None, 
                  case_id=None):
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
        nr_variants=nr_variants,
        skip_case_id=skip_case_id,
        gq_treshold=gq_treshold,
    )
    

def load_variants(adapter, family_id, individuals, vcf, nr_variants=None, 
                  skip_case_id=False, gq_treshold=None):
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
    
    if skip_case_id:
        family_id = None

    # Loop over the variants in the vcf
    with click.progressbar(vcf, label="Inserting variants",length=nr_variants) as bar:
        for variant in bar:
            #Creates a variant that is ready to insert into the database
            formated_variant = get_formated_variant(
                            variant=variant,
                            individuals=individuals,
                            family_id=family_id,
                            gq_treshold=gq_treshold,
                        )
        
            if formated_variant:
                adapter.add_variant(variant=formated_variant)
    

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
