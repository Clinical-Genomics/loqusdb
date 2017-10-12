# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import click

from pprint import pprint as pp

from .vcf import get_vcf
from .case import get_case
from .delete import delete
from loqusdb.build_models import (build_case, build_variant)
from loqusdb.exceptions import CaseError

LOG = logging.getLogger(__name__)

def load_database(adapter, variant_file, family_file, nr_variants=None, 
                  family_type='ped', skip_case_id=False, gq_treshold=None, 
                  case_id=None):
    """Load the database with a case and its variants
            
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
    vcf = get_vcf(variant_file)
    
    if gq_treshold:
        if not vcf.contains('GQ'):
            LOG.warning('Set gq-treshold to 0 or add info to vcf')
            raise SyntaxError('GQ is not defined in vcf header')

    # Get a ped_parser.Family object from family file
    with open(family_file, 'r') as family_lines:
        family = get_case(
            family_lines=family_lines, 
            family_type=family_type
        )

    case_id = case_id or family.family_id
    

    # Get the indivuduals that are present in vcf file
    vcf_individuals = vcf.samples
    # Convert infromation to a loqusdb Case object
    case_obj = build_case(
        case=family, 
        case_id=case_id,
        vcf_path=variant_file,
        vcf_individuals=vcf_individuals
    )

    # Add the case to database
    try:
        adapter.add_case(case_obj)
    except CaseError as err:
        raise err

    # If case was succesfully added we can store the variants
    try:
        load_variants(  
            adapter=adapter, 
            case_obj=case_obj, 
            vcf_obj=vcf,
            nr_variants=nr_variants,
            skip_case_id=skip_case_id,
            gq_treshold=gq_treshold,
        )
    except Exception as err:
        # If something went wrong do a rollback
        LOG.warning(err)
        delete(
            adapter=adapter,
            variant_file=variant_file,
            family_file=family_file,
            family_type=family_type,
            case_id=case_id,
        )
        raise err

def load_variants(adapter, vcf_obj, case_obj, nr_variants=None, skip_case_id=False, 
                  gq_treshold=None):
    """Load variants for a family into the database.

    Args:
        adapter (loqusdb.plugins.Adapter): initialized plugin
        vcf_obj (cyvcf2.VCF): An iterable with cyvcf2.Variants
        case_obj(Case): dict with case information
        nr_variants(int)
        skip_case_id (bool): whether to include the case id on variant level 
                             or not
        gq_treshold(int)
    """
    case_id = case_obj['case_id']
    if skip_case_id:
        case_id = None
    # Loop over the variants in the vcf
    with click.progressbar(vcf_obj, label="Inserting variants",length=nr_variants) as bar:
        for variant in bar:
            #Creates a variant that is ready to insert into the database
            formated_variant = build_variant(
                    variant=variant,
                    case_obj=case_obj,
                    case_id=case_id,
                    gq_treshold=gq_treshold,
                )
            # We need to check if there was any information returned
            # The variant could be excluded based on low gq or no calls in family
            if not formated_variant:
                continue
            if formated_variant['is_sv']:
                adapter.add_structural_variant(variant=formated_variant)
            else:
                adapter.add_variant(variant=formated_variant)

