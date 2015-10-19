import logging

logger = logging.getLogger(__name__)

def update_variant(db, mongo_variant, homozygote=False):
    """Update the information for a variant that exists in the database
    
    Args:
        db (MongoClient): A connection to the mongodb
        mongo_variant (dict): A mongo variant dictionary. 
                        (this should include an '_id')
        homozygote (bool): If the variant is homozygote
    """
    if homozygote:
        logger.debug("Updating hom calls for variant: {0}".format(
            mongo_variant.get('variant_id')))
        logger.debug("Updating observations for variant: {0}".format(
            mongo_variant.get('variant_id')))
        
        db.variant.update({
            '_id': mongo_variant['_id']
            },{
                '$inc': {
                    'homozygote': 1
                },
                 '$inc': {
                    'observations': 1
                }
            }, upsert=False)
    else:
        logger.debug("Updating observations for variant: {0}".format(
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
        
    """
    logger.debug("Checking if variant {0} exists in database".format(
        variant.get('variant_id')
    ))
    existing_variant = get_variant(db, variant)
    
    if existing_variant:
        update_variant(db, existing_variant, variant.get('homozygote', 0))
    else:
        logger.debug("Adding variant {0} to database".format(
            variant.get("variant_id")
        ))
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

def delete_variant(db, variant):
    """Remove variant from database
        
        This means that we take down the observations variable with one.
        If 'observations' == 1 we remove the variant.
        
        Args:
            db (MongoClient): A connection to the mongodb
            variant (dict): A variant dictionary            
    """
    mongo_variant = get_variant(db, variant)
    if mongo_variant:
        if mongo_variant['observations'] == 1:
            logger.debug("Removing variant {0}".format(
                mongo_variant.get('variant_id')
            ))
            db.variant.remove({'variant_id': variant['variant_id']})
        else:
            logger.debug("Decreasing observations for {0}".format(
                mongo_variant.get('variant_id')
            ))
            db.variant.update({
                '_id': mongo_variant['_id']
                },{
                    '$inc': {
                        'observations': -1
                    }
                }, upsert=False)
            if variant.get('homozygote'):
                logger.debug("Decreasing hom calls for {0}".format(
                    mongo_variant.get('variant_id')
                    ))
        
                db.variant.update({
                    '_id': mongo_variant['_id']
                    },{
                        '$inc': {
                            'homozygote': -1
                        }
                    }, upsert=False)
            
            
    return
