import logging

from pymongo import ASCENDING

from loqusdb.constants import MEI_COLLECTION, MEI_WINDOW
from loqusdb.plugins.mongo.structural_variant import SVMixin

LOG = logging.getLogger(__name__)


class MEIMixin(SVMixin):
    """Mobile element insertions

    MEIs are stored as clusters in a collection of their own, using the same clustering as
    structural variants, but with a fixed window around the insertion point. The cluster type
    (sv_type) includes the element, e.g. INS:ME:ALU, so that different elements are counted
    separately.
    """

    def add_mei_variant(self, variant, mei_window=MEI_WINDOW):
        """Add a mobile element insertion to the mei collection

        Args:
            variant (dict): A variant dictionary
            mei_window(int): Distance from the cluster mean within which insertions are merged
        """
        self.add_structural_variant(variant, max_window=mei_window, collection=MEI_COLLECTION)

    def delete_mei_variant(self, variant, mei_window=MEI_WINDOW):
        """Remove an observation of a mobile element insertion from the mei collection

        Args:
            variant (dict): A variant dictionary
            mei_window(int): Window to use if the cluster has no stored window
        """
        self.delete_structural_variant(variant, max_window=mei_window, collection=MEI_COLLECTION)

    def get_mei_variant(self, variant):
        """Return the mei cluster closest to a variant, or None

        Args:
            variant (dict): A variant dictionary with chrom, end_chrom, pos, end and sv_type
        """
        return self.get_structural_variant(variant, collection=MEI_COLLECTION)

    def get_mei_types(self):
        """Return the distinct MEI cluster types in the database, e.g. INS:ME:ALU"""
        return self.db[MEI_COLLECTION].distinct("sv_type")

    def get_mei_variants(self, chromosome=None, sv_type=None, pos=None, end=None):
        """Return mobile element insertion clusters, optionally within a region

        Args:
            chromosome (str)
            sv_type (str): e.g. INS:ME:ALU
            pos (int): Start of region
            end (int): End of region, defaults to pos

        Returns:
            variants (Iterable(dict)): clusters whose window overlaps the region
        """
        query = {}
        if chromosome:
            query["chrom"] = chromosome
        if sv_type:
            query["sv_type"] = sv_type
        if pos:
            query["pos_right"] = {"$gte": pos}
            query["pos_left"] = {"$lte": end or pos}

        LOG.info("Find all mei variants {}".format(query))
        return self.db[MEI_COLLECTION].find(query).sort(
            [("chrom", ASCENDING), ("pos_left", ASCENDING)]
        )
