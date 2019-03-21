import logging
import numpy as np

from .vcf import get_file_handle

from loqusdb.build_models.variant import get_variant_id

from loqusdb.exceptions import ProfileError

from loqusdb.constants import GENOTYPE_MAP

LOG = logging.getLogger(__name__)

def get_profiles(adapter, vcf_file):

    """Given a vcf, get a profile string for each sample in the vcf
    based on the profile variants in the database

    Args:
        adapter(MongoAdapter): Adapter to mongodb
        vcf_file(str): Path to vcf file

    Returns:
        profiles (dict(str)): The profiles (given as strings) for each sample
                              in vcf.

    """
    vcf = get_file_handle(vcf_file)
    individuals = vcf.samples
    profiles = {individual: '' for individual in individuals}

    for profile_variant in adapter.profile_variants():

        ref = profile_variant['ref']
        alt = profile_variant['alt']

        pos = profile_variant['pos']
        end = pos + 1
        chrom = profile_variant['chrom']

        region = f"{chrom}:{pos}-{end}"

        #Find variants in region

        found_variant = False
        for variant in vcf(region):

            variant_id = get_variant_id(variant)

            #If variant id i.e. chrom_pos_ref_alt matches
            if variant_id == profile_variant['_id']:
                found_variant = True
                #find genotype for each individual in vcf
                for i, individual in enumerate(individuals):

                    genotype = GENOTYPE_MAP[variant.gt_types[i]]
                    if genotype == 'hom_alt':
                        gt_str = f"{alt}{alt}"
                    elif genotype == 'het':
                        gt_str = f"{ref}{alt}"
                    else:
                        gt_str = f"{ref}{ref}"

                    #Append genotype to profile string of individual
                    profiles[individual] += gt_str

                #Break loop if variant is found in region
                break

        #If no call was found for variant, give all samples a hom ref genotype
        if not found_variant:
            for individual in individuals: profiles[individual] += f"{ref}{ref}"


    return profiles

def profile_match(adapter, profiles, threshold=0.9):

    """
        given a dict of profiles, searches through all the samples in the DB
        for a match.

        Args:
            adapter (MongoAdapter): Adapter to mongodb
            profiles (dict(str)): The profiles (given as strings) for each sample
                                  in vcf.
            threshold (float): threshold for ratio of similarity that is needed
                               to assume that the samples are the same.
    """

    for case in adapter.cases():

        for individual in case['individuals']:

            for sample in profiles.keys():

                if individual.get('profile'):

                    similarity = compare_profiles(
                        profiles[sample], individual['profile']
                    )

                    if similarity >= threshold:

                        msg = (
                                f"individual {sample} has a {similarity} similarity "
                                f"with individual {individual['ind_id']} in case "
                                f"{case['case_id']}"
                        )
                        LOG.critical(msg)

                        #Raise some exception
                        raise ProfileError

def compare_profiles(profile1, profile2):

    """
        Given two profiles, determine the ratio of similarity

        Args:
            profile1/2 (str): profile string
        Returns:
            similarity_ratio (float): the ratio of similiarity (0-1)
    """

    length = len(profile1)

    profile1 = np.array(list(profile1))
    profile2 = np.array(list(profile2))

    similarity_array = profile1 == profile2

    matches = np.sum(similarity_array)

    similarity_ratio = matches/length

    return similarity_ratio
