import logging

from loqusdb.plugins import BaseVariantMixin

from pymongo import (ASCENDING, DESCENDING)

logger = logging.getLogger(__name__)

class VariantMixin(BaseVariantMixin):
    
    def add_variant(self, variant):
        """Add a variant to the variant collection
        
            If the variant exists we update the count else we insert a new variant
            object.
        
            Args:
                variant (dict): A variant dictionary
        
        """
        logger.debug("Upserting variant: {0}".format(variant.get('_id')))
        
        if variant.get('family_id'):
            message = self.db.variant.update(
                {'_id': variant['_id'],},
                {
                    '$inc': {
                        'homozygote': variant.get('homozygote', 0),
                        'hemizygote': variant.get('hemizygote', 0),
                        'observations': 1
                    },
                    '$push': {
                        'families': {
                            '$each': [variant.get('family_id')],
                            '$slice': -50
                            }
                    },
                    '$set': {
                        'chrom': variant.get('chrom'),
                        'start': variant.get('pos'),
                        'end': variant.get('end'),
                        'ref': variant.get('ref'),
                        'alt': variant.get('alt'),
                    }
                 }, 
                 upsert=True
            )
        else:
            message = self.db.variant.update(
                {'_id': variant['_id']},
                {
                    '$inc': {
                        'homozygote': variant.get('homozygote', 0),
                        'hemizygote': variant.get('hemizygote', 0),
                        'observations': 1,
                    }
                 }, 
                 upsert=True
            )

        if message.get('updatedExisting'):
            logger.debug("Variant %s was updated", message.get("upserted"))
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

    def get_variants(self, chromosome=None, start=None, end=None):
        """Return all variants in the database

        Args:
            chromosome (str)
            start (int)
            end (int)
        
    
        Returns:
            variants (Iterable(Variant))
        """
        query = {}
        if chromosome:
            query['chrom'] = chromosome
        if start:
            query['start'] = {'$lte': end}
            query['end'] = {'$gte': start}
        logger.debug("Find all variants {}".format(query))
        return self.db.variant.find(query).sort([('start', ASCENDING)])

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
                            'homozygote': - (variant.get('homozygote', 0)),
                            'hemizygote': - (variant.get('hemizygote', 0)),
                        },
                        '$pull': {
                            'families': variant.get('family_id')
                        }
                    }, upsert=False)
        return


    def get_chromosomes(self):
        """Return a list of all chromosomes found in database"""
        res = self.db.variant.distinct('chrom')
        return res
    
    def get_max_position(self, chrom):
        """Get the last position observed on a chromosome in the database"""
        res = self.db.variant.find({'chrom':chrom}, {'_id':0, 'end':1}).sort([('end', DESCENDING)]).limit(1)
        end = 0
        for variant in res:
            end = variant['end']
        return end