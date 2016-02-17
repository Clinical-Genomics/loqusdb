from pymongo import MongoClient

from loqusdb.plugins import Base

import logging

logger = logging.getLogger(__name__)


class MongoAdapter(Base):
    """docstring for MongoAdapter"""
    def __init__(self, debug=False):
        super(MongoAdapter, self).__init__()
        self.db = None
    
    def connect(self, host='localhost', port=27017, database='loqusdb', client=None):
        """Connect to a mongo database
        
        Args:
            host(str) : The host for the mongo datavase
            port(int) : The port for the mongo datavase
            database(str) : The name of the mongo databse
            client(MongoClient) : For testing only
        """
        logger.info("Accessing host:{0}, port:{1}, database:{2}".format(
            host, port, database
        ))
        if not client:
            client = MongoClient(host, port)
        
        self.db = client[database]
    
    def add_variant(self, variant):
        """Add a variant to the variant collection
        
            If the variant exists we update the count else we insert a new variant
            object.
        
            Args:
                variant (dict): A variant dictionary
        
        """
        logger.debug("Upserting variant: {0}".format(variant.get('_id')))
    
        message = self.db.variant.update(
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
    
    def get_variant(self, variant):
        """Check if a variant exists in the database and return it
    
            Search the variants with the variant id
        
            Args:
                variant (dict): A variant dictionary
        
            Returns:
                variant (dict): A variant dictionary
        """
        return self.db.variant.find_one({'_id': variant.get('_id')})

    def delete_variant(self, variant):
        """Remove variant from database
            
            This means that we take down the observations variable with one.
            If 'observations' == 1 we remove the variant. If variant was homozygote
            we decrease 'homozygote' with one.
            
            Args:
                variant (dict): A variant dictionary            
        """
        mongo_variant = self.get_variant(variant)
        
        if mongo_variant:
            
            if mongo_variant['observations'] == 1:
                logger.debug("Removing variant {0}".format(
                    mongo_variant.get('_id')
                ))
                message = self.db.variant.remove({'_id': variant['_id']})
            else:
                logger.debug("Decreasing observations for {0}".format(
                    mongo_variant.get('_id')
                ))
                message = self.db.variant.update({
                    '_id': mongo_variant['_id']
                    },{
                        '$inc': {
                            'observations': -1,
                            'homozygote': -(variant.get('homozygote', 0))
                        }
                    }, upsert=False)
        return
        
    def add_bulk(self, variants):
        """Insert a bulk of variants
        
            Args:
                variants(Iterable(dict)) : A iterable with variants
        
        """
        
        bulk = self.db.variant.initialize_ordered_bulk_op()
        for variant in variants:
            if variant:
                bulk.find({'_id': variant['_id']}).upsert().update(
                    {
                        '$inc': {
                            'homozygote': variant.get('homozygote', 0),
                            'observations': 1
                        }
                     }
                )
        message = bulk.execute()
        logger.debug("Number of variants inserted: {0}".format(
            message.get('nInserted')
        ))
        logger.debug("Number of variants upserted: {0}".format(
            message.get('nUpserted')
        ))
        return
