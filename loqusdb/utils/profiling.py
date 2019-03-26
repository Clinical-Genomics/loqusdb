import logging
import numpy as np
from copy import deepcopy

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
        for a match. If a matching sample is found an exception is raised,
        and the variants will not be loaded into the database.

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
        Given two profiles, determine the ratio of similarity, i.e.
        the hamming distance between the strings.

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


def update_profiles(adapter):

    """
    For all cases having vcf_path, update the profile string for the samples

    Args:
        adapter (MongoAdapter): Adapter to mongodb

    """

    for case in adapter.cases():

        #If the case has a vcf_path, get the profiles and update the
        #case with new profiled individuals.
        if case.get('vcf_path'):

            profiles = get_profiles(adapter, case['vcf_path'])
            profiled_individuals = deepcopy(case['individuals'])

            for individual in profiled_individuals:
                ind_id = individual['ind_id']
                try:
                    profile = profiles[ind_id]
                    individual['profile'] = profile

                except KeyError:
                    LOG.warning(f"sample IDs in vcf does not match for case {case['case_id']}")

            updated_case = deepcopy(case)

            updated_case['individuals'] = profiled_individuals

            adapter.add_case(updated_case, update=True)

def profile_stats(adapter, threshold = 0.9):

    """
    Check for sample duplicates in the database, based on the sample profiles.
    calculates average distances between samples, and std.

    Args:
        adapter (MongoAdapter): Adapter to mongodb
        threshold (float): threshold for ratio of similarity that is needed
                           to assume that the samples are the same.

    """

    profiles = []
    samples = []
    distance_dict = {}

    for case in adapter.cases():

        for individual in case['individuals']:

            #Make sample name <case_id>.<sample_id>
            sample = f"{case['case_id']}.{individual['ind_id']}"

            #Check if sample has a profile
            if individual.get('profile'):
                ind_profile = individual['profile']

                #Store sample profile and sample name in profiles resp. samples
                profiles.append(ind_profile)
                samples.append(sample)

                #The similarities for current samples agains all others
                distance_array = []
                for i in range(len(profiles)):
                    distance = compare_profiles(ind_profile, profiles[i])
                    distance_array.append(distance)

                    #If the similarity is above given threshold, issue warning
                    if distance >= threshold:
                        LOG.warning(f"{sample} is {distance} similar to {samples[i]}")

                distance_dict[sample] = distance_array

    #Make numpy array of all similarities
    distances = []
    for key, value in distance_dict.items():
        #Avoid getting last element in similarities, which is the sample
        #matching to itseld, i.e. 1.
        distances.extend(value[0:-1])

    distances = np.array(distances, dtype=np.float16)

    #Print some stats
    LOG.info(f"Number of duplicates: {np.sum(distances >= threshold)}")
    LOG.info(f"Average similarity between samples: {distances.mean()}")
    LOG.info(f"Standard deviation: {distances.std()}")
    LOG.info(f"Max similarity: {distances.max()}")
