# -*- coding: utf-8 -*-


class Case(dict):
    """Represent a Case."""

    def __init__(
        self,
        case_id,
        vcf_path=None,
        vcfsv_path=None,
        nr_variants=None,
        nr_sv_variants=None,
        profile_path=None,
    ):
        super(Case, self).__init__(
            case_id=case_id,
            vcf_path=vcf_path,
            vcf_sv_path=vcfsv_path,
            nr_variants=nr_variants,
            nr_sv_variants=nr_sv_variants,
            profile_path=profile_path,
        )
        self["individuals"] = []
        self["sv_individuals"] = []
        self["_inds"] = {}
        self["_sv_inds"] = {}


class Individual(dict):
    """Individual representation."""

    def __init__(
        self,
        ind_id,
        case_id=None,
        mother=None,
        father=None,
        sex=None,
        phenotype=None,
        ind_index=None,
        profile=None,
        similar_samples=None,
    ):
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

        if profile:
            self["profile"] = profile
        if similar_samples:
            self["similar_samples"] = similar_samples
