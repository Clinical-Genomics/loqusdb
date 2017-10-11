# -*- coding: utf-8 -*-
from .dotdict import DotDict


class Case(DotDict):
    """Represent a Case."""
    def __init__(self, case_id, vcf_path, vcfsv_path=None, nr_variants=None):
        super(Case, self).__init__(
            case_id=case_id,
            vcf_path=vcf_path,
            vcfsv_path=vcfsv_path,
            nr_variants=nr_variants,
        )
        self['individuals'] = []
        self._inds = {}
    
    def add_individual(self, individual):
        """Add a individual to the case
        
        Args:
            individual(Individual)
        """
        self['individuals'].append(individual)
        self._inds[individual['ind_id']] = individual
    
    def get_individual(self, ind_id):
        """Return a individual object"""
        return self._inds.get(ind_id)
    


class Individual(DotDict):
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
            mother=mother,
            father=father,
            sex=sex,
            phenotype=phenotype,
            ind_index=ind_index,
        )
