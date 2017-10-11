import logging
from loqusdb.plugins import BaseVariantMixin

from pymongo import (ASCENDING, DESCENDING)

LOG = logging.getLogger(__name__)

class VariantMixin(BaseVariantMixin):
    
    def add_variant(self, variant):
        """Add a variant to the variant collection
        
            If the variant exists we update the count else we insert a new variant
            object.
        
            Args:
                variant (dict): A variant dictionary
        
        """
        LOG.debug("Upserting variant: {0}".format(variant.get('variant_id')))
        
        # If no family_id is used the list will be populated with None
        message = self.db.variant.update(
            {'_id': variant['variant_id'],},
            {
                '$inc': {
                    'homozygote': variant.get('homozygote', 0),
                    'hemizygote': variant.get('hemizygote', 0),
                    'observations': 1
                },
                '$push': {
                    'families': {
                        '$each': [variant.get('case_id')],
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

        if message.get('updatedExisting'):
            LOG.debug("Variant %s was updated", message.get("upserted"))
        else:
            LOG.debug("Variant was added to database for first time")
        return

    def add_structural_variant(self, variant):
        """Add a variant to the structural variants collection
        
        The process of adding an SV variant differs quite a bit from the 
        more straight forward case of SNV/INDEL.
        Here we need to search if the variant mathes any of the existing
        clusters. Then we need to choose the closest cluster and update
        the boundaries for that cluster.
        
        Args:
            variant (dict): A variant dictionary
        
        """
        # This will return the cluster most similar to variant or None
        cluster = self.get_structural_variant(variant)
        if cluster is None:
            # Insert variant to get a _id
            _id = self.db.structural_variant.insert({
                'chrom': variant['chrom'],
                'end_chrom': variant['end_chrom'],
                'sv_type': variant['sv_type'],
            })
            
            cluster = {
                '_id': _id,
                'pos_sum': 0,
                'end_sum': 0,
                'nr_events': 0,
                'sv_type': variant['sv_type'],
            }
        
        nr_events = cluster['nr_events']
        
        pos_mean = (cluster['pos_sum'] + variant['pos']) // (nr_events + 1)
        end_mean = (cluster['end_sum'] + variant['end'])// (nr_events + 1)
        
        # We need to calculate the new cluster length
        if cluster['sv_type'] != 'BND':
            cluster_len = end_mean - pos_mean
        else:
            cluster_len = float('inf')
        
        # If the length of SV is shorter than 500 the variant 
        # is considered precise
        # Otherwise the interval size is closest whole 100 number
        
        # The max size of a interval is 2000
        interval_size = min(round(cluster_len/10, -2), 2000)
        
        message = self.db.structural_variant.update(
            {'_id': cluster['_id'],},
            {
                '$inc': {
                    'nr_events': 1,
                    'pos_sum': variant['pos'],
                    'end_sum': variant['end'],
                },
                '$push': {
                    'families': {
                        '$each': [variant.get('family_id')],
                        '$slice': -50,
                        }
                },
                '$set': {
                    'pos_left': max(pos_mean - interval_size, 0),
                    'pos_right': pos_mean + interval_size,
                    'end_left': max(end_mean - interval_size, 0),
                    'end_right': end_mean + interval_size,
                }
             }, 
             upsert=True
        )

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

    def get_structural_variant(self, variant):
        """Check if there are any overlapping sv clusters
    
            Search the sv variants with chrom start end_chrom end and sv_type
        
            Args:
                variant (dict): A variant dictionary
        
            Returns:
                variant (dict): A variant dictionary
        """
        res = self.db.structural_variant.find({
            'chrom': variant['chrom'],
            'end_chrom': variant['end_chrom'],
            'sv_type': variant['sv_type'],
            'pos_left': {'$gte': variant['pos']},
            'pos_right': {'$lte': variant['pos']},
            'end_left': {'$gte': variant['end']},
            'end_right': {'$lte': variant['end']},
        })
        nr_hits = res.count()
        if nr_hits == 0:
            LOG.debug("Multiple SV hits")
            return None
        # We count the distance to mean on both ends to see which variant is closest
        for hit in res:
            distance = (abs(variant['pos'] - (pos_left+pos_right)/2) + 
                        abs(variant['end'] - (end_left+end_right)/2))
        return None

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
        LOG.debug("Find all variants {}".format(query))
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
                LOG.debug("Removing variant {0}".format(
                    mongo_variant.get('_id')
                ))
                message = self.db.variant.remove({'_id': variant['_id']})
            else:
                LOG.debug("Decreasing observations for {0}".format(
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
                            'families': variant.get('case_id')
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