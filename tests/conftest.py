import logging
import pytest
from mongomock import MongoClient
from pymongo import MongoClient as RealMongoClient

from loqusdb.plugins import MongoAdapter
from loqusdb.log import init_log

logger = logging.getLogger('.')

init_log(logger, loglevel='DEBUG')

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
def ped_path(request):
    file_path = 'tests/fixtures/recessive_trio.ped'
    return file_path

@pytest.fixture(scope='function')
def funny_ped_path(request):
    file_path = 'tests/fixtures/funny_trio.ped'
    return file_path

class Cyvcf2Variant(object):
    """Class to mock cyvcf2 variants"""
    def __init__(self, variant_line):
        super(Cyvcf2Variant, self).__init__()
        self.variant_line = variant_line
        splitted_line = variant_line.rstrip().split('\t')
        self.CHROM = splitted_line[0]
        self.POS = int(splitted_line[1])
        self.REF = splitted_line[3]
        self.ALT = [splitted_line[4]]
    
    def __str__(self):
        return self.variant_line

def variant_line(chrom='1', pos='10', rs_id='.', ref='A', alt='T', 
    qual='100', filt='INFO', info='.', form='GT:GQ', genotypes=['0/1:60']):
    """Return a vcf formated variant line"""
    variant_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}".format(
        chrom, pos, rs_id, ref, alt, qual, filt, info, form
    )
    
    for gt_call in genotypes:
        variant_line += '\t{0}'.format(gt_call)
    
    variant_line += '\n'
    
    return variant_line

@pytest.fixture(scope='function')
def case(request):
    """Return ped formated case lines"""
    case_lines = [
        "#FamilyID\tSampleID\tFather\tMother\tSex\tPhenotype\n",
        "recessive_trio\tproband\tfather\tmother\t1\t2\n",
        "recessive_trio\tmother\t0\t0\t2\t1\n",
        "recessive_trio\tfather\t0\t0\t1\t1\n"
    ]
    return case_lines

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
def cyvcf2_het_variant(request):
    variant = variant_line()
    variant_object = Cyvcf2Variant(variant)
    return variant_object

@pytest.fixture(scope='function')
def cyvcf2_variant_no_gq(request):
    variant = variant_line(form='GT', genotypes=['0/1'])
    variant_object = Cyvcf2Variant(variant)
    return variant_object

@pytest.fixture(scope='function')
def cyvcf2_hom_variant(request):
    variant = variant_line(genotypes=['1/1:60'])
    variant_object = Cyvcf2Variant(variant)
    return variant_object

@pytest.fixture(scope='function')
def cyvcf2_variant_no_call(request):
    variant = variant_line(genotypes=['./.'])
    variant_object = Cyvcf2Variant(variant)
    return variant_object
