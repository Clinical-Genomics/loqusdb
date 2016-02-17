import pytest
from mongomock import MongoClient
from pymongo import MongoClient as RealMongoClient

from loqusdb.plugins import MongoAdapter

@pytest.fixture(scope='function')
def mongo_client(request):
    """Return a mongomock client"""
    client = MongoClient()
    return client

@pytest.fixture(scope='function')
def real_mongo_client(request):
    """Return a mongo client"""
    client = RealMongoClient()
    
    def teardown():
        client.drop_database('test')
    
    request.addfinalizer(teardown)
    return client

@pytest.fixture(scope='function')
def mongo_adapter(request, mongo_client):
    """Return a mongo adapter"""
    adapter = MongoAdapter()
    adapter.connect(database='test', client=mongo_client)
    return adapter

@pytest.fixture(scope='function')
def simplest_variant(request):
    """Return a simple variant"""
    variant = {
        '_id': 'test',
    }
    return variant

@pytest.fixture(scope='function')
def homozygous_variant(request):
    """Return a homozygous variant"""
    variant = {
        '_id': 'test',
        'homozygote': 1,
    }
    return variant

@pytest.fixture(scope='function')
def simple_case(request):
    """Return a simple case"""
    case = {
        'case_id': 'test',
        'vcf_path': './test.vcf'
    }
    return case

@pytest.fixture(scope='function')
def vcf_path(request):
    """Return the path to a test vcf"""
    file_path = 'tests/fixtures/test.vcf'
    return file_path

@pytest.fixture(scope='function')
def ped_path(request):
    """Return the path to a test vcf"""
    file_path = 'tests/fixtures/recessive_trio.ped'
    return file_path
