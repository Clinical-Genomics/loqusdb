import logging
import pytest
from mongomock import MongoClient
from pymongo import MongoClient as RealMongoClient

from ped_parser import FamilyParser

from loqusdb.plugins import MongoAdapter
from loqusdb.log import init_log

logger = logging.getLogger('.')

init_log(logger, loglevel='DEBUG')


class Variant(object):
    """Mock a cyvcf variant
    
    Default is to return a variant with three individuals high genotype 
    quality.
    """
    def __init__(self, chrom='1', pos=80000, ref='A', alt='C', end=None, 
                 gt_quals=[60, 60, 60], gt_types=[1, 1, 0]):
        super(Variant, self).__init__()
        self.CHROM = chrom
        self.POS = pos
        self.REF = ref
        self.ALT = [alt]
        self.end = end or pos
        self.gt_quals = gt_quals
        self.gt_types = gt_types
        

@pytest.fixture(scope='function')
def mongo_client(request):
    """Return a mongomock client"""
    client = MongoClient()
    return client

# @pytest.fixture(scope='function')
# def real_mongo_client(request):
#     """Return a mongo client"""
#     client = RealMongoClient()
#
#     def teardown():
#         client.drop_database('test')
#
#     request.addfinalizer(teardown)
#     return client
#
# @pytest.fixture(scope='function')
# def real_mongo_adapter(request, real_mongo_client):
#     """Return a mongo adapter"""
#     adapter = MongoAdapter()
#     adapter.connect(database='test', client=real_mongo_client)
#     return adapter

@pytest.fixture(scope='function')
def mongo_adapter(request, mongo_client):
    """Return a mongo adapter"""
    adapter = MongoAdapter()
    adapter.connect(database='test', client=mongo_client)
    return adapter

@pytest.fixture(scope='function')
def simplest_variant(request):
    variant = {
        '_id': 'test',
    }
    return variant

@pytest.fixture(scope='function')
def homozygous_variant(request):
    variant = {
        '_id': 'test',
        'homozygote': 1,
        'family_id': '1'
    }
    return variant

@pytest.fixture(scope='function')
def simple_case(request):
    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    return case

@pytest.fixture(scope='function')
def vcf_path(request):
    file_path = 'tests/fixtures/test.vcf'
    return file_path

@pytest.fixture(scope='function')
def double_vcf_path(request):
    file_path = 'tests/fixtures/double_variant.vcf'
    return file_path

@pytest.fixture(scope='function')
def unsorted_vcf_path(request):
    file_path = 'tests/fixtures/unsorted.vcf'
    return file_path

@pytest.fixture(scope='function')
def zipped_vcf_path(request):
    file_path = 'tests/fixtures/test.vcf.gz'
    return file_path

@pytest.fixture(scope='function')
def ped_path(request):
    file_path = 'tests/fixtures/recessive_trio.ped'
    return file_path

@pytest.fixture(scope='function')
def funny_ped_path(request):
    file_path = 'tests/fixtures/funny_trio.ped'
    return file_path

@pytest.fixture(scope='function')
def ind_positions(request):
    return {'proband': 0, 'mother':1, 'father':2}

@pytest.fixture(scope='function')
def case_lines(request, ped_path):
    """Return ped formated case lines"""
    case = []
    with open(ped_path, 'r') as f:
        for line in f:
            case.append(line) 
    
    return case

@pytest.fixture(scope='function')
def case_obj(request, case_lines):
    """Return a case obj"""
    family_parser = FamilyParser(case_lines, family_type='ped')
    families = list(family_parser.families.keys())
    family = family_parser.families[families[0]]
    return family

@pytest.fixture(scope='function')
def case_id(request, case_lines):
    """Return a case obj"""
    family_parser = FamilyParser(case_lines, family_type='ped')
    families = list(family_parser.families.keys())
    family = family_parser.families[families[0]]
    family_id = family.family_id

    return family_id

@pytest.fixture(scope='function')
def individuals(request, case_obj):
    """Return a case obj"""
    
    return case_obj.individuals

@pytest.fixture(scope='function')
def two_cases(request):
    """Return ped formated case lines"""
    case_lines = [
        "#FamilyID\tSampleID\tFather\tMother\tSex\tPhenotype\n",
        "1\tproband\t0\t0\t1\t2\n",
        "2\tproband\t0\t0\t2\t1\n",
    ]
    return case_lines

@pytest.fixture(scope='function')
def hem_variant(request):
    variant_object = Variant(chrom='X', pos=60000)
    return variant_object

@pytest.fixture(scope='function')
def variant_chr(request):
    variant_object = Variant(chrom='chrX', pos=60000)
    return variant_object

@pytest.fixture(scope='function')
def par_variant(request):
    variant_object = Variant(chrom='X', pos=60001)
    return variant_object

@pytest.fixture(scope='function')
def het_variant(request):
    variant_object = Variant()
    return variant_object

@pytest.fixture(scope='function')
def variant_no_gq(request):
    variant_object = Variant(gt_quals=[-1,-1,-1])
    return variant_object

@pytest.fixture(scope='function')
def hom_variant(request):
    variant_object = Variant(gt_types=[3,1,1])
    return variant_object

@pytest.fixture(scope='function')
def variant_no_call(request):
    variant_object = Variant(gt_types=[2, 2, 2])
    return variant_object
