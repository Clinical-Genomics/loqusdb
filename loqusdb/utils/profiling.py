import logging
from copy import deepcopy

import numpy as np
from loqusdb.build_models.variant import get_variant_id
from loqusdb.constants import GENOTYPE_MAP, HAMMING_RANGES
from loqusdb.exceptions import ProfileError

from .vcf import get_file_handle

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
    profiles = {individual: [] for individual in individuals}

    for profile_variant in adapter.profile_variants():

        ref = profile_variant["ref"]
        alt = profile_variant["alt"]

        pos = profile_variant["pos"]
        end = pos + 1
        chrom = profile_variant["chrom"]

        region = f"{chrom}:{pos}-{end}"

        # Find variants in region

        found_variant = False
        for variant in vcf(region):

            variant_id = get_variant_id(variant)

            # If variant id i.e. chrom_pos_ref_alt matches
            if variant_id == profile_variant["_id"]:
                found_variant = True
                # find genotype for each individual in vcf
                for i, individual in enumerate(individuals):

                    genotype = GENOTYPE_MAP[variant.gt_types[i]]
                    if genotype == "hom_alt":
                        gt_str = f"{alt}{alt}"
                    elif genotype == "het":
                        gt_str = f"{ref}{alt}"
                    else:
                        gt_str = f"{ref}{ref}"

                    # Append genotype to profile string of individual
                    profiles[individual].append(gt_str)

                # Break loop if variant is found in region
                break

        # If no call was found for variant, give all samples a hom ref genotype
        if not found_variant:
            for individual in individuals:
                profiles[individual].append(f"{ref}{ref}")

    return profiles


def profile_match(adapter, profiles, hard_threshold=0.95, soft_threshold=0.9):
    """
    given a dict of profiles, searches through all the samples in the DB
    for a match. If a matching sample is found an exception is raised,
    and the variants will not be loaded into the database.

    Args:
        adapter (MongoAdapter): Adapter to mongodb
        profiles (dict(str)): The profiles (given as strings) for each sample in vcf.
        hard_threshold(float): Rejects load if hamming distance above this is found
        soft_threshold(float): Stores similar samples if hamming distance above this is found

    Returns:
        matches(dict(list)): list of similar samples for each sample in vcf.
    """
    matches = {sample: [] for sample in profiles.keys()}
    for case in adapter.cases():

        if case.get("individuals") is None:
            continue

        for individual in case["individuals"]:

            for sample in profiles.keys():

                if individual.get("profile"):

                    similarity = compare_profiles(profiles[sample], individual["profile"])

                    if similarity >= hard_threshold:
                        msg = (
                            f"individual {sample} has a {similarity} similarity "
                            f"with individual {individual['ind_id']} in case "
                            f"{case['case_id']}"
                        )
                        LOG.critical(msg)

                        # Raise some exception
                        raise ProfileError

                    if similarity >= soft_threshold:
                        match = f"{case['case_id']}.{individual['ind_id']}"
                        matches[sample].append(match)

    return matches


def check_duplicates(adapter, profiles, hard_threshold):
    """
    Searches database for duplicates. If duplicate is found, the individual
    is returned.

    Args:
        adapter (MongoAdapter): Adapter to mongodb
        profiles (dict(str)): The profiles (given as strings) for each sample in vcf.
        hard_threshold(float): Rejects load if hamming distance above this is found
    Returns:
        individual (dict): dictionary representation of duplicated individual

    """

    for case in adapter.cases():

        if case.get("individuals") is None:
            continue

        for individual in case["individuals"]:

            for sample in profiles.keys():

                if individual.get("profile"):

                    similarity = compare_profiles(profiles[sample], individual["profile"])

                    if similarity >= hard_threshold:
                        msg = (
                            f"individual {sample} has a {similarity} similarity "
                            f"with individual {individual['ind_id']} in case "
                            f"{case['case_id']}"
                        )
                        LOG.info(msg)
                        return individual


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

    similarity_ratio = matches / length

    return similarity_ratio


def update_profiles(adapter):
    """
    For all cases having vcf_path, update the profile string for the samples

    Args:
        adapter (MongoAdapter): Adapter to mongodb

    """

    for case in adapter.cases():

        # If the case has a vcf_path, get the profiles and update the
        # case with new profiled individuals.
        if case.get("profile_path"):

            profiles = get_profiles(adapter, case["profile_path"])
            profiled_individuals = deepcopy(case["individuals"])

            for individual in profiled_individuals:
                ind_id = individual["ind_id"]
                try:
                    profile = profiles[ind_id]
                    individual["profile"] = profile

                except KeyError:
                    LOG.warning(f"sample IDs in vcf does not match for case {case['case_id']}")

            updated_case = deepcopy(case)

            updated_case["individuals"] = profiled_individuals

            adapter.add_case(updated_case, update=True)


def profile_stats(adapter, threshold=0.9):
    """
    Compares the pairwise hamming distances for all the sample profiles in
    the database. Returns a table of the number of distances within given
    ranges.

    Args:
        adapter (MongoAdapter): Adapter to mongodb
        threshold (float): If any distance is found above this threshold
            a warning will be given, stating the two matching samples.

    Returns:
        distance_dict (dict): dictionary with ranges as keys, and the number
            of distances that are within these ranges as values.

    """
    profiles = []
    samples = []

    # Instatiate the distance dictionary with a count 0 for all the ranges
    distance_dict = {key: 0 for key in HAMMING_RANGES.keys()}

    for case in adapter.cases():

        for individual in case["individuals"]:

            if individual.get("profile"):
                # Make sample name <case_id>.<sample_id>
                sample_id = f"{case['case_id']}.{individual['ind_id']}"
                ind_profile = individual["profile"]

                # Numpy array to hold all the distances for this samples profile
                distance_array = np.array([], dtype=np.float)

                for sample, profile in zip(samples, profiles):

                    # Get distance and append to distance array
                    distance = compare_profiles(ind_profile, profile)
                    distance_array = np.append(distance_array, distance)

                    # Issue warning if above threshold
                    if distance >= threshold:
                        LOG.warning(f"{sample_id} is {distance} similar to {sample}")

                # Check number of distances in each range and add to distance_dict
                for key, range in HAMMING_RANGES.items():
                    # Calculate the number of hamming distances found within the
                    # range for current individual
                    distance_dict[key] += np.sum(
                        (distance_array >= range[0]) & (distance_array < range[1])
                    )

                # Append profile and sample_id for this sample for the next
                # iteration
                profiles.append(ind_profile)
                samples.append(sample_id)

    return distance_dict
