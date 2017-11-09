from pprint import pprint as pp
from loqusdb.build_models.case import build_case

def test_build_case_no_ped():
    ## GIVEN some vcf individuals
    
    vcf_individuals = ['mother', 'proband']
    case_id = 'test'
    
    ## WHEN building a case object
    case_obj = build_case(
        case = None, 
        vcf_individuals=vcf_individuals, 
        case_id=case_id, 
        vcf_path=None, 
        sv_individuals=None, 
        nr_variants=None
    )
    
    ## THEN assert that the case got the right ID
    assert case_obj['case_id'] == case_id
    for ind_obj in case_obj['individuals']:
        assert ind_obj['name'] in vcf_individuals
        assert ind_obj['ind_id'] in vcf_individuals
    

def test_build_case_ped(family_obj):
    ## GIVEN a ped parser family_obj
    vcf_inds = [ind_id for ind_id in family_obj.individuals]
    
    ## WHEN building a case object
    case_obj = build_case(
        case = family_obj, 
        vcf_individuals=vcf_inds, 
        case_id=None, 
        vcf_path=None, 
        sv_individuals=None, 
        nr_variants=None
    )
    
    ## THEN assert that the case has the correct id 
    assert case_obj['case_id'] == family_obj.family_id
    
    for ind_obj in case_obj['individuals']:
        assert ind_obj['ind_id'] in vcf_inds