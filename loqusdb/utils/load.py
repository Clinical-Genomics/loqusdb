# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import click

from pprint import pprint as pp

from loqusdb.utils import (get_case, get_vcf)
from loqusdb.build_models import (build_case, build_variant)
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
    
    if gq_treshold:
        if not vcf.contains('GQ'):
            logger.warning('Set gq-treshold to 0 or add info to vcf')
            raise SyntaxError('GQ is not defined in vcf header')

    vcf_individuals = vcf.samples
    
    with open(family_file, 'r') as family_lines:
        family = get_case(
            family_lines=family_lines, 
            family_type=family_type
        )
    
    case_obj = build_case(
        family=family, 
        case_id=case_id,
        vcf_path=variant_file,
    )
    
    ind_positions = {}
    for i, ind_id in enumerate(vcf_individuals):
        ind_positions[ind_id] = i
        
    for ind in case_obj:
        ind_id = ind.ind_id
        if ind_id not in ind_positions:
            raise CaseError("Ind {0} in ped file does not exist in VCF".format(ind_id))

    adapter.add_case(case_obj)

    try:
        load_variants(  
            adapter=adapter, 
            case_id=case_obj['case_id'], 
            individuals=[ind['ind_id'] for ind in case_obj['individuals']],
            vcf_obj=vcf,
            ind_positions=ind_positions,
            nr_variants=nr_variants,
            skip_case_id=skip_case_id,
            gq_treshold=gq_treshold,
        )
    except Exception as err:
        logger.warning(err)
        # delete_all(
        #     adapter=adapter,
        #     variant_file=variant_file,
        #     family_file=family_file,
        #     family_type=family_type,
        #     case_id=case_id
        # )
        raise err

    

def load_variants(adapter, case_id, individuals, vcf_obj, ind_positions, 
                  nr_variants=None, skip_case_id=False, gq_treshold=None):
    """Load variants for a family into the database.

    Args:
        adapter (loqusdb.plugins.Adapter): initialized plugin
        case_id (str): unique family identifier
        inidividuals (List[str]): list to match individuals
        vcf (cyvcf2.VCF): An iterable with cyvcf2.Variants
        ind_positions(dict): dict with {<ind_id>: <pos>} in vcf
        nr_variants(int)
        skip_case_id (bool): whether to include the case id on variant level 
                             or not
        gq_treshold(int)
    """
    if skip_case_id:
        case_id = None
    # Loop over the variants in the vcf
    with click.progressbar(vcf_obj, label="Inserting variants",length=nr_variants) as bar:
        for variant in bar:
            #Creates a variant that is ready to insert into the database
            formated_variant = build_case(
                    variant=variant,
                    individuals=individuals,
                    ind_positions=ind_positions,
                    case_id=case_id,
                    gq_treshold=gq_treshold,
                )
            # We need to check if there was any information returned
            # The variant could be excluded based on low gq or no calls in family
            if not formated_variant:
                continue
            if variant_type == 'sv':
                adapter.add_structural_variant(variant=formated_variant)
            else:
                adapter.add_variant(variant=formated_variant)

