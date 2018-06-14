# -*- coding: utf-8 -*-

class Case(dict):
    """Represent a Case."""
    def __init__(self, case_id, vcf_path, vcfsv_path=None, nr_variants=None):
        super(Case, self).__init__(
            case_id=case_id,
            vcf_path=vcf_path,
            vcfsv_path=vcfsv_path,
            nr_variants=nr_variants,
        )
        self['individuals'] = []
        self['sv_individuals'] = []
        self['_inds'] = {}
        self['_sv_inds'] = {}
    
    def add_individual(self, individual, ind_type='snv'):
        """Add a individual to the case
        
        Args:
            individual(Individual)
            ind_type(str): 'snv' or 'sv'
        """
        if ind_type == 'snv':
            self['individuals'].append(individual)
            self['_inds'][individual['ind_id']] = individual
        else:
            self['sv_individuals'].append(individual)
            self['_sv_inds'][individual['ind_id']] = individual
            
    
    def get_individual(self, ind_id, ind_type='snv'):
        """Return a individual object"""
        if ind_type == 'snv':
            return self['_inds'].get(ind_id)
        else:
            return self['_sv_inds'].get(ind_id)
    


class Individual(dict):
    """Individual representation."""
    def __init__(self, ind_id, case_id=None, mother=None,
                 father=None, sex=None, phenotype=None, ind_index=None):
        """Construct a individual object

            Args:
                ind_id (str): The individual id
                case_id (str): What case it belongs to
                mother (str): The mother id
                father (str): The father id
                sex (str): Sex in ped format
                phenotype (str): Phenotype in ped format
                ind_index (int): Column in the vcf.
        """
        super(Individual, self).__init__(
            ind_id=ind_id,
            name=ind_id,
            case_id=case_id,
            ind_index=ind_index,
            sex=sex,
        )
