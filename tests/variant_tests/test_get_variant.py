from mongomock import MongoClient
from loqusdb.utils import get_variant

def test_get_variant():
    """Test to insert one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        '_id': 'test',
    }
    db.variant.insert(variant)
    
    mongo_variant = get_variant(db, variant)
    assert mongo_variant['_id'] == 'test'

def test_get_none():
    """Test to get non existing variant"""

    client = MongoClient()
    db = client['loqusdb']

    variant = {
        '_id': 'test',
    }

    assert get_variant(db, variant) == None
