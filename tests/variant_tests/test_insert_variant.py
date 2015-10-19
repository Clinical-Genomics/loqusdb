from mongomock import MongoClient
from loqusdb.utils import add_variant

def test_insert_one_variant():
    """Test to insert one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        'variant_id': 'test',
    }
    add_variant(db, variant)
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['variant_id'] == 'test'
    assert mongo_variant['observations'] == 1
    assert mongo_variant.get('homozygote',0) == 0

def test_insert_one_variant_twice():
    """Test to insert one variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        'variant_id': 'test',
    }
    add_variant(db, variant)
    add_variant(db, variant)
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['variant_id'] == 'test'
    assert mongo_variant['observations'] == 2

def test_insert_hom_variant():
    """Test to insert a homozygote variant"""
    
    client = MongoClient()
    db = client['loqusdb']
    
    variant = {
        'variant_id': 'test',
        'homozygote': 1,
    }
    add_variant(db, variant)
    
    mongo_variant = db.variant.find_one()
    
    assert mongo_variant['variant_id'] == 'test'
    assert mongo_variant['observations'] == 1
    assert mongo_variant.get('homozygote', 0) == 1
