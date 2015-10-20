from mongomock import MongoClient
from loqusdb.utils import delete_variant

def test_remove_one_variant():
    """Test to update one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        '_id': 'test',
        'observations': 1
    }
    
    db.variant.insert(variant)
    
    delete_variant(db, variant)

    assert db.variant.find_one() == None

def test_downcount_one_variant():
    """Test to update one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        '_id': 'test',
        'observations': 2
    }
    
    db.variant.insert(variant)
    
    delete_variant(db, variant)
    
    mongo_variant = db.variant.find_one()

    assert mongo_variant['observations'] == 1
    

def test_remove_non_existing():
    """Test to update one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        '_id': 'test',
        'observations': 1
    }
    
    delete_variant(db, variant)

    assert db.variant.find_one() == None
