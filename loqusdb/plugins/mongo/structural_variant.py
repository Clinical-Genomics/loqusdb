import logging

from pprint import pprint as pp

from loqusdb.plugins import BaseVariantMixin
from loqusdb.models import Identity

from pymongo import (ASCENDING, DESCENDING, UpdateOne)

LOG = logging.getLogger(__name__)

class SVMixin():

    def add_structural_variant(self, variant, max_window = 3000):
        """Add a variant to the structural variants collection
        
        The process of adding an SV variant differs quite a bit from the 
        more straight forward case of SNV/INDEL.
        
        Variants are represented in the database by clusters that are two intervals,
        one interval for start(pos) and one for end. The size of the intervals changes
        according to the size of the variants. The maximum window size is a parameter.
        
        Here we need to search if the variant matches any of the existing
        clusters. Then we need to choose the closest cluster and update
        the boundaries for that cluster.
        
        Args:
            variant (dict): A variant dictionary
            max_window(int): Specify the maximum window size for large svs
        
        
                                        -
                                      -   -
                                    -       -
                                  -           -
                                -               -
                              -                   -
                           |-----|              |-----|
                          /\                         /\
                          |                          |
                pos - interval_size             end + interval_size
        """
        # This will return the cluster most similar to variant or None
        cluster = self.get_structural_variant(variant)
        # If there was no matcing cluster we need to create a new cluster
        if cluster is None:
            # The cluster will be populated with information later.
            cluster = {
                'chrom': variant['chrom'],
                'end_chrom': variant['end_chrom'],
                'sv_type': variant['sv_type'],
                'pos_sum': 0,
                'end_sum': 0,
                'observations': 0,
                'length': 0,
                'sv_type': variant['sv_type'],
                'families': [],
                
            }
            # Insert variant to get a _id
            _id = self.db.structural_variant.insert_one(cluster).inserted_id
            
            cluster['_id'] = _id
        
        case_id = variant.get('case_id')
        if case_id:
            # If the variant is already added for this case we continue
            # One case will only give duplicated information
            if case_id in cluster['families']:
                return
            else:
                # Insert the new case in the beginning of array
                cluster['families'].insert(0,case_id)
                # Make sure array does not grow out of bounds
                cluster['families'] = cluster['families'][:50]

        # Update number of times we have seen the event
        nr_events = cluster['observations'] + 1
        
        #                             -
        #                           -   -
        #                         -       -
        #                       -           -
        #                     -               -
        #                   -                   -
        #                |--.--|              |--.--|
    
        # This indicates the center for each of the end points for the event AFTER the new variant
        # is added to the cluster
        # i.e. the dots in the picture above
        pos_mean = int((cluster['pos_sum'] + variant['pos']) // (nr_events))
        end_mean = int((cluster['end_sum'] + variant['end']) // (nr_events))
        
        # We need to calculate the new cluster length
        # Handle translocation as a special case
        if cluster['sv_type'] != 'BND':
            cluster_len = end_mean - pos_mean
            # We need to adapt the interval size depending on the size of the cluster
            divider = 10
            if cluster_len < 1000:
                # We allow intervals for smaller variants to be relatively larger
                divider = 2
            elif cluster_len < 1000:
                # We allow intervals for smaller variants to be relatively larger
                divider = 5
            interval_size = int(min(round(cluster_len/divider, -2), max_window))
        else:
            # We need to treat translocations as a special case.
            # Set length to a huge number that mongodb can handle, float('inf') would not work.
            cluster_len = 10e10
            # This number seems large, if compared with SV size it is fairly small.
            interval_size = max_window * 2
        
        # If the length of SV is shorter than 500 the variant 
        # is considered precise
        # Otherwise the interval size is closest whole 100 number
        res = self.db.structural_variant.find_one_and_update(
            {'_id': cluster['_id']},
            {
                '$inc': {
                    'observations': 1,
                    'pos_sum': variant['pos'],
                    'end_sum': variant['end'],
                },
            
                '$set': {
                    'pos_left': max(pos_mean - interval_size, 0),
                    'pos_right': pos_mean + interval_size,
                    'end_left': max(end_mean - interval_size, 0),
                    'end_right': end_mean + interval_size,
                    'families': cluster['families'],
                    'length': cluster_len,
                }
            }
        )
        
        # Insert an identity object to link cases to variants and clusters
        identity_obj = Identity(cluster_id=cluster['_id'], variant_id=variant['id_column'], 
                                case_id=case_id)
        self.db.identity.insert_one(identity_obj)
        
        return

    def get_structural_variant(self, variant):
        """Check if there are any overlapping sv clusters

       Search the sv variants with chrom start end_chrom end and sv_type

       Args:
           variant (dict): A variant dictionary

       Returns:
           variant (dict): A variant dictionary
        """
        # Create a query for the database
        # This will include more variants than we want
        # The rest of the calculations will be done in python
        query = {
                'chrom': variant['chrom'],
                'end_chrom': variant['end_chrom'],
                'sv_type': variant['sv_type'],
                '$and': [
                    {'pos_left': {'$lte': variant['pos']}},
                    {'pos_right': {'$gte': variant['pos']}},
                ]
            }

        res = self.db.structural_variant.find(query).sort('pos_left',1)
        match = None
        distance = None
        closest_hit = None
        # First we check that the coordinates are correct
        # Then we count the distance to mean on both ends to see which variant is closest
        for hit in res:
            # We know from the query that the variants position is larger than the left most part of
            # the cluster. 
            # If the right most part of the cluster is smaller than the variant position they do
            # not overlap
            if hit['end_left'] > variant['end']:
                continue
            if hit['end_right'] < variant['end']:
                continue

            # We need to calculate the distance to see what cluster that was closest to the variant
            distance = (abs(variant['pos'] - (hit['pos_left'] + hit['pos_right'])/2) + 
                        abs(variant['end'] - (hit['end_left'] + hit['end_right'])/2))

            # If we have no cluster yet we set the curent to be the hit
            if closest_hit is None:
                match = hit
                closest_hit = distance
                continue

            # If the distance is closer than previous we choose current cluster
            if distance < closest_hit:
                # Set match to the current closest hit
                match = hit
                # Update the closest distance
                closest_hit = distance

        return match

    def get_sv_variants(self, chromosome=None, end_chromosome=None, sv_type=None, 
                        pos=None, end=None):
        """Return all structural variants in the database

        Args:
            chromosome (str)
            end_chromosome (str)
            sv_type (str)
            pos (int): Left position of SV
            end (int): Right position of SV

        Returns:
            variants (Iterable(Variant))
        """
        query = {}
        
        if chromosome:
            query['chrom'] = chromosome
        if end_chromosome:
            query['end_chrom'] = end_chromosome
        if sv_type:
            query['sv_type'] = sv_type
        if pos:
            if not '$and' in query:
                query['$and'] = []
            query['$and'].append({'pos_left': {'$lte': pos}})
            query['$and'].append({'pos_right': {'$gte': pos}})
            
        if end:
            if not '$and' in query:
                query['$and'] = []
            query['$and'].append({'end_left': {'$lte': end}})
            query['$and'].append({'end_right': {'$gte': end}})
        
        LOG.info("Find all sv variants {}".format(query))
        
        return self.db.structural_variant.find(query).sort([('chrom', ASCENDING), ('pos_left', ASCENDING)])

    def get_clusters(self, variant_id):
        """Search what clusters a variant belongs to
        
        Args:
            variant_id(str): From ID column in vcf
        
        Returns:
            clusters()
        """
        query = {'variant_id':variant_id}
        identities = self.db.identity.find(query)
        return identities
