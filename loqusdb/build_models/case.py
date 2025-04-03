import logging

from loqusdb.exceptions import CaseError
from loqusdb.models import Case, Individual

LOG = logging.getLogger(__name__)


def get_individual_positions(individuals: list[str]) -> dict[str, int]:
    """Return a dictionary with individual positions."""
    ind_pos = {}
    if individuals:
        for i, ind in enumerate(individuals):
            ind_pos[ind] = i
    return ind_pos


def build_case(
    case,
    vcf_individuals=None,
    case_id=None,
    vcf_path=None,
    sv_individuals=None,
    vcf_sv_path=None,
    nr_variants=None,
    nr_sv_variants=None,
    profiles=None,
    matches=None,
    profile_path=None,
):
    """Build a Case from the given information.

    Args:
        case(ped_parser.Family): A family object
        vcf_individuals(list): Show the order of inds in vcf file
        case_id(str): If another name than the one in family file should be used
        vcf_path(str)
        sv_individuals(list): Show the order of inds in vcf file
        vcf_sv_path(str)
        nr_variants(int)
        nr_sv_variants(int)
        profiles(dict): The profiles for each sample in vcf
        matches(dict(list)): list of similar samples for each sample in vcf.

    Returns:
        case_obj(models.Case)
    """
    # Create a dict that maps the ind ids to the position they have in vcf
    individual_positions = get_individual_positions(vcf_individuals)
    sv_individual_positions = get_individual_positions(sv_individuals)

    family_id = None
    if case:
        if not case.affected_individuals:
            LOG.warning("No affected individuals could be found in ped file")
        family_id = case.family_id

    # If case id is given manually we use that one
    case_id = case_id or family_id
    if case_id is None:
        raise CaseError

    case_obj = Case(
        case_id=case_id,
    )

    if vcf_path:
        case_obj["vcf_path"] = vcf_path
        case_obj["nr_variants"] = nr_variants

    if vcf_sv_path:
        case_obj["vcf_sv_path"] = vcf_sv_path
        case_obj["nr_sv_variants"] = nr_sv_variants

    if profile_path:
        case_obj["profile_path"] = profile_path

    ind_objs = []
    if case:
        if individual_positions:
            _ind_pos = individual_positions
        else:
            _ind_pos = sv_individual_positions

        for ind_id in case.individuals:
            individual = case.individuals[ind_id]
            try:
                # If a profile dict exists, get the profile for ind_id
                profile = profiles[ind_id] if profiles else None
                # If matching samples are found, get these samples for ind_id
                similar_samples = matches[ind_id] if matches else None
                ind_obj = Individual(
                    ind_id=ind_id,
                    case_id=case_id,
                    ind_index=_ind_pos[ind_id],
                    sex=individual.sex,
                    profile=profile,
                    similar_samples=similar_samples,
                )
                ind_objs.append(dict(ind_obj))
            except KeyError:
                raise CaseError("Ind %s in ped file does not exist in VCF", ind_id)
    else:
        # If there where no family file we can create individuals from what we know
        for ind_id in individual_positions:
            profile = profiles[ind_id] if profiles else None
            similar_samples = matches[ind_id] if matches else None
            ind_obj = Individual(
                ind_id=ind_id,
                case_id=case_id,
                ind_index=individual_positions[ind_id],
                profile=profile,
                similar_samples=similar_samples,
            )
            ind_objs.append(dict(ind_obj))

    # Add individuals to the correct variant type
    for ind_obj in ind_objs:
        if vcf_sv_path:
            case_obj["sv_individuals"].append(dict(ind_obj))
            case_obj["_sv_inds"][ind_obj["ind_id"]] = dict(ind_obj)
        if vcf_path:
            case_obj["individuals"].append(dict(ind_obj))
            case_obj["_inds"][ind_obj["ind_id"]] = dict(ind_obj)

    return case_obj
