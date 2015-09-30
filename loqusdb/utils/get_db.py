from pymongo import MongoClient

import logging

logger = logging.getLogger(__name__)


def get_db(host='localhost', port=27017, database='loqusdb'):
    """Get connection to the mongodb
    
        Args:
            host (str): The mongodb host
            port (int): The port to use
        
        Returns:
            db (MongoClient): A connection to the mongodb
    """
    logger.info("Accessing host:{0}, port:{1}, database:{2}".format(
        host, port, database
    ))
    client = MongoClient(host, port)
    db = client[database]
    return db

def update_variant(db, mongo_variant):
    """Update the information for a variant that exists in the database
    
    Args:
        db (MongoClient): A connection to the mongodb
        variant (dict): A variant dictionary
    """
    logger.debug("Updating variant: {0}".format(
        mongo_variant.get('variant_id')))
    
    db.variant.update({
        '_id': mongo_variant['_id']
        },{
            '$inc': {
                'observations': 1
            }
        }, upsert=False)
    
    return

def add_variant(db, variant):
    """Add a variant to the variant collection
        
        If the variant exists we update the count else we insert a new variant
        object.
        
        Args:
            db (MongoClient): A connection to the mongodb
            variant (dict): A variant dictionary
        Returns:
            variant_mongo_id (str): The mongodb id for the variant
        
    """
    logger.debug("Checking if variant {0} exists in database".format(
        variant.get('variant_id')
    ))
    existing_variant = get_variant(db, variant)
    
    if existing_variant:
        update_variant(db, existing_variant)
    else:
        variant['observations'] = 1
        variant_mongo_id = db.variant.insert_one(variant).inserted_id
    
    return

def get_variant(db, variant):
    """Check if a variant exists in the database
    
        Search the variants with the variant id
        
        Args:
            db (MongoClient): A connection to the mongodb
            variant (dict): A variant dictionary
        
        Returns:
            variant (dict): A variant dictionary
    """
    variant_id = variant['variant_id']
    return db.variant.find_one({'variant_id': variant_id})
