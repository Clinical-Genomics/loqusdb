import logging

import cyvcf2
import pytest

from loqusdb.build_models.case import build_case
from loqusdb.build_models.variant import build_variant
from loqusdb.log import init_log
from loqusdb.models import Case
from loqusdb.plugins.mongo.adapter import MongoAdapter
from loqusdb.utils.load import update_case
from mongomock import MongoClient as MockClient
from ped_parser import FamilyParser
from pymongo import MongoClient

logger = logging.getLogger(".")

init_log(logger, loglevel="DEBUG")

REAL_DATABASE = "loqus-test"
TEST_DATABASE = "test"


class CyvcfVariant(object):
    """Mock a cyvcf variant

    Default is to return a variant with three individuals high genotype
    quality.
    """

    def __init__(
        self,
        chrom="1",
        pos=80000,
        ref="A",
        alt="C",
        end=None,
        gt_quals=[60, 60, 60],
        gt_types=[1, 1, 0],
        var_type="snv",
        var_id=None,
        info_dict={},
    ):
        super(CyvcfVariant, self).__init__()
        self.CHROM = chrom
        self.POS = pos
        self.REF = ref
        self.ALT = [alt]
        self.end = end or pos
        self.gt_quals = gt_quals
        self.gt_types = gt_types
        self.var_type = var_type
        self.INFO = info_dict
        if var_id is None:
            var_id = "."
        self.ID = var_id


@pytest.fixture(scope="function")
def real_db_name(request):
    """Return the name of the real mongo test db"""
    return REAL_DATABASE


@pytest.fixture(scope="function")
def mongo_client(request):
    """Return a mongomock client"""
    client = MockClient()
    return client


@pytest.fixture(scope="function")
def real_mongo_client(request):
    """Return a mongomock client"""
    client = MongoClient()

    def teardown():
        print("\n")
        logger.info("Deleting database")
        client.drop_database(REAL_DATABASE)
        logger.info("Database deleted")

    request.addfinalizer(teardown)

    return client


@pytest.fixture(scope="function")
def mongo_adapter(request, mongo_client):
    """Return a mongo adapter"""
    db_name = TEST_DATABASE
    adapter = MongoAdapter(mongo_client, db_name)

    return adapter


@pytest.fixture(scope="function")
def real_mongo_adapter(request, real_mongo_client):
    """Return a mongo adapter"""
    db_name = REAL_DATABASE
    adapter = MongoAdapter(real_mongo_client, db_name)

    return adapter


@pytest.fixture(scope="function")
def simplest_variant(request):
    variant = {
        "_id": "test",
    }
    return variant


@pytest.fixture(scope="function")
def homozygous_variant(request):
    variant = {"_id": "test", "homozygote": 1, "case_id": "1"}
    return variant


@pytest.fixture(scope="function")
def simple_case(request):
    case = Case("test", "./test.vcf")

    return case


@pytest.fixture(scope="function")
def vcf_path(request):
    file_path = "tests/fixtures/test.vcf"
    return file_path


@pytest.fixture(scope="function")
def sv_vcf_path(request):
    file_path = "tests/fixtures/test.SV.vcf"
    return file_path


@pytest.fixture(scope="function")
def double_vcf_path(request):
    "This will return a vcf with the same variant two times"
    file_path = "tests/fixtures/double_variant.vcf"
    return file_path


@pytest.fixture(scope="function")
def unsorted_vcf_path(request):
    "This will return a vcf with unsorted variants"
    file_path = "tests/fixtures/unsorted.vcf"
    return file_path


@pytest.fixture(scope="function")
def zipped_vcf_path(request):
    "Returns a VCF that is gzipped and have a index companion"
    file_path = "tests/fixtures/test.vcf.gz"
    return file_path


@pytest.fixture(scope="function")
def profile_vcf_path(request):
    "Returns a VCF containing profile variants"
    file_path = "tests/fixtures/profile_snv.vcf"
    return file_path


@pytest.fixture(scope="function")
def ped_path(request):
    file_path = "tests/fixtures/recessive_trio.ped"
    return file_path


@pytest.fixture(scope="function")
def funny_ped_path(request):
    "Returns a ped file with incorrect family relations"
    return "tests/fixtures/funny_trio.ped"


@pytest.fixture(scope="function")
def ind_positions(request):
    return {"proband": 0, "mother": 1, "father": 2}


@pytest.fixture(scope="function")
def case_lines(request, ped_path):
    """Return ped formated case lines"""
    case = []
    with open(ped_path, "r") as f:
        for line in f:
            case.append(line)

    return case


@pytest.fixture(scope="function")
def case_id(request, ped_path):
    """Return ped formated case lines"""
    case_id = None
    with open(ped_path, "r") as f:
        for line in f:
            case_id = line.split("\t")[0]

    return case_id


@pytest.fixture(scope="function")
def vcf_obj(request, vcf_path):
    """return a cyvcf2.VCF obj"""
    return cyvcf2.VCF(vcf_path)


@pytest.fixture(scope="function")
def sv_vcf_obj(request, sv_vcf_path):
    """return a cyvcf2.VCF obj"""
    return cyvcf2.VCF(sv_vcf_path)


@pytest.fixture(scope="function")
def profile_list(request):
    return ["AA", "CC", "GG", "TT"]


@pytest.fixture(scope="function")
def case_obj(request, case_lines, vcf_obj, vcf_path, profile_list):
    """Return a case obj"""
    family_parser = FamilyParser(case_lines, family_type="ped")
    families = list(family_parser.families.keys())
    family = family_parser.families[families[0]]
    vcf_individuals = vcf_obj.samples
    nr_variants = 0
    for nr_variants, variant in enumerate(vcf_obj, 1):
        continue
    return build_case(
        case=family,
        vcf_individuals=vcf_individuals,
        vcf_path=vcf_path,
        nr_variants=nr_variants,
        profiles={individual: profile_list for individual in vcf_individuals},
    )


@pytest.fixture(scope="function")
def sv_case_obj(request, case_lines, sv_vcf_obj, sv_vcf_path):
    """Return a case obj"""
    family_parser = FamilyParser(case_lines, family_type="ped")
    families = list(family_parser.families.keys())
    family = family_parser.families[families[0]]
    vcf_individuals = sv_vcf_obj.samples
    nr_variants = 0
    for nr_variants, variant in enumerate(sv_vcf_obj, 1):
        continue
    return build_case(
        case=family,
        sv_individuals=vcf_individuals,
        vcf_sv_path=sv_vcf_path,
        nr_sv_variants=nr_variants,
    )


@pytest.fixture(scope="function")
def complete_case_obj(request, case_obj, sv_case_obj):
    """Return a case obj with both sv and snv information"""
    return update_case(case_obj, sv_case_obj)


@pytest.fixture(scope="function")
def family_obj(request, case_lines):
    """Return a case obj"""
    family_parser = FamilyParser(case_lines, family_type="ped")
    families = list(family_parser.families.keys())
    return family_parser.families[families[0]]


@pytest.fixture(scope="function")
def case_id(request, case_lines):
    """Return a case id"""
    family_parser = FamilyParser(case_lines, family_type="ped")
    families = list(family_parser.families.keys())
    family = family_parser.families[families[0]]
    return family.family_id


@pytest.fixture(scope="function")
def individuals(request, case_obj):
    """Return a case obj"""

    return case_obj.individuals


@pytest.fixture(scope="function")
def two_cases(request):
    """Return ped formated case lines"""
    return [
        "#FamilyID\tSampleID\tFather\tMother\tSex\tPhenotype\n",
        "1\tproband\t0\t0\t1\t2\n",
        "2\tproband\t0\t0\t2\t1\n",
    ]


## Variant fixtures:

# chrom='1',
# pos=80000,
# ref='A',
# alt='C',
# end=None,
# gt_quals=[60, 60, 60],
# gt_types=[1, 1, 0],
# var_type='snv',
# info_dict={}

### Variant objects


@pytest.fixture(scope="function")
def variant_obj(request, het_variant, ind_positions, individuals):
    return build_variant(
        variant=het_variant,
        individuals=individuals,
        ind_positions=ind_positions,
        case_id="test",
        gq_treshold=None,
    )


### CYVCF2 variants
### SNVs:
@pytest.fixture(scope="function")
def hem_variant(request):
    return CyvcfVariant(chrom="X", pos=60000)


@pytest.fixture(scope="function")
def variant_chr(request):
    return CyvcfVariant(chrom="chrX", pos=60000)


@pytest.fixture(scope="function")
def par_variant(request):
    return CyvcfVariant(chrom="X", pos=60001)


@pytest.fixture(scope="function")
def het_variant(request):
    return CyvcfVariant()


@pytest.fixture(scope="function")
def bnd_variant(request):
    return CyvcfVariant(
        chrom="1",
        pos=80000,
        alt="N[1:80000[",
        ref="N",
        end=80000,
        info_dict={"SVTYPE": "BND"},
    )


@pytest.fixture(scope="function")
def variant_no_gq(request):
    return CyvcfVariant(gt_quals=[-1, -1, -1])


@pytest.fixture(scope="function")
def hom_variant(request):
    return CyvcfVariant(gt_types=[3, 1, 1])


@pytest.fixture(scope="function")
def variant_no_call(request):
    return CyvcfVariant(gt_types=[2, 2, 2])


### SVs:
@pytest.fixture(scope="function")
def del_variant(request):
    return CyvcfVariant(
        chrom="1",
        ref="G",
        alt="<DEL>",
        pos=1285001,
        end=1287000,
        var_type="sv",
        info_dict={"END": 1287000, "SVLEN": -20000, "SVTYPE": "DEL"},
    )


@pytest.fixture(scope="function")
def small_insert_variant(request):
    return CyvcfVariant(
        chrom="1",
        ref="G",
        alt="GGGACGGGGGTTCTGAGATAAGCAAGCCCCCACCAGGTGAGACCGGCGGAGCTGTGGCCACCGAGGTCCCGGGAGCTGGTGCT",
        pos=3021145,
        end=3021145,
        var_type="sv",
        info_dict={"END": 3021145, "SVLEN": 82, "SVTYPE": "INS"},
    )


@pytest.fixture(scope="function")
def insertion_variant(request):
    return CyvcfVariant(
        chrom="1",
        ref="A",
        alt="<INS>",
        pos=3177306,
        end=3177306,
        var_type="sv",
        info_dict={"END": 3177306, "SVLEN": None, "SVTYPE": "INS"},
    )


@pytest.fixture(scope="function")
def duptandem_variant(request):
    return CyvcfVariant(
        chrom="1",
        ref="A",
        alt="<DUP:TANDEM>",
        pos=3092626,
        end=3092849,
        var_type="sv",
        info_dict={"END": 3092849, "SVLEN": 223, "SVTYPE": "DUP"},
    )


@pytest.fixture(scope="function")
def translocation_variant(request):
    return CyvcfVariant(
        chrom="1",
        ref="N",
        alt="N[11:119123896[",
        pos=3754913,
        end=3754913,
        var_type="sv",
        info_dict={"END": None, "SVLEN": None, "SVTYPE": "BND"},
    )
