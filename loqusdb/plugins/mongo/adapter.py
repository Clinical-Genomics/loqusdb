import logging

from loqusdb import INDEXES
from mongo_adapter import MongoAdapter as BaseAdapter

from loqusdb.plugins.mongo.case import CaseMixin
from loqusdb.plugins.mongo.profile_variant import ProfileVariantMixin
from loqusdb.plugins.mongo.variant import VariantMixin

logger = logging.getLogger(__name__)


class MongoAdapter(BaseAdapter, VariantMixin, CaseMixin, ProfileVariantMixin):
    """docstring for MongoAdapter"""

    def wipe_db(self):
        """Wipe the whole database"""
        logger.warning("Wiping the whole database")
        self.client.drop_database(self.db_name)
        logger.debug("Database wiped")

    def indexes(self, collection=None):
        """Return a list with the current indexes

        Skip the mandatory _id_ indexes

        Args:
            collection(str)

        Returns:
            indexes(list)
        """
        indexes = []
        for collection_name in self.db.list_collection_names():
            if collection and collection != collection_name:
                continue
            for index_name in self.db[collection_name].index_information():
                if index_name != "_id_":
                    indexes.append(index_name)
        return indexes

    def check_indexes(self):
        """Check if the indexes exists"""
        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get("name")
                if index_name not in existing_indexes:
                    logger.warning(
                        "Index {0} missing. Run command `loqusdb index`".format(index_name)
                    )
                    return
        logger.info("All indexes exists")

    def ensure_indexes(self):
        """Update the indexes"""
        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get("name")
                if index_name in existing_indexes:
                    logger.debug("Index exists: %s" % index_name)
                    self.db[collection_name].drop_index(index_name)
            logger.info(
                "creating indexes for collection {0}: {1}".format(
                    collection_name,
                    ", ".join(index.document.get("name") for index in indexes),
                )
            )

            self.db[collection_name].create_indexes(indexes)
