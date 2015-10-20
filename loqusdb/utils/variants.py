import logging

logger = logging.getLogger(__name__)

def add_variant(db, variant):
    """Add a variant to the variant collection
        
        If the variant exists we update the count else we insert a new variant
        object.
        
        Args:
            db (MongoClient): A connection to the mongodb
            variant (dict): A variant dictionary
        
    """
    logger.debug("Upserting variant: {0}".format(variant.get('_id')))
    
    message = db.variant.update(
        {'_id': variant['_id']},
        {
            '$inc': {
                'homozygote': variant.get('homozygote', 0),
                'observations': 1
            }
         }, 
         upsert=True
    )
    
    if message.get('updatedExisting'):
        logger.debug("Variant {0} was updated".format(message.get("upserted")))
    else:
        logger.debug("Variant was added to database for first time")
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
    return db.variant.find_one({'_id': variant.get('_id')})

def delete_variant(db, variant):
    """Remove variant from database
        
        This means that we take down the observations variable with one.
        If 'observations' == 1 we remove the variant. If variant was homozygote
        we decrease 'homozygote' with one.
        
        Args:
            db (MongoClient): A connection to the mongodb
            variant (dict): A variant dictionary            
    """
    mongo_variant = get_variant(db, variant)
    
    if mongo_variant:
        
        if mongo_variant['observations'] == 1:
            logger.debug("Removing variant {0}".format(
                mongo_variant.get('_id')
            ))
            message = db.variant.remove({'_id': variant['_id']})
        else:
            logger.debug("Decreasing observations for {0}".format(
                mongo_variant.get('_id')
            ))
            message = db.variant.update({
                '_id': mongo_variant['_id']
                },{
                    '$inc': {
                        'observations': -1,
                        'homozygote': -(variant.get('homozygote', 0))
                    }
                }, upsert=False)
            
            
    return
