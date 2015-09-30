from mongomock import MongoClient
from loqusdb.utils import update_variant

def test_update_one_variant():
    """Test to update one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant_1 = {
        'variant_id': 'test',
        'observations': 1
    }
    
    db.variant.insert(variant_1)
    
    mongo_variant = db.variant.find_one()
    
    update_variant(db, mongo_variant)

    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['variant_id'] == 'test'
    assert mongo_variant['observations'] == 2

