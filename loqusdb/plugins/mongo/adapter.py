import logging
from pymongo import MongoClient

from loqusdb.plugins import Base
from . import VariantMixin, CaseMixin

from loqusdb import INDEXES

logger = logging.getLogger(__name__)


class MongoAdapter(VariantMixin, CaseMixin, Base):
    """docstring for MongoAdapter"""
    def __init__(self, debug=False):
        super(MongoAdapter, self).__init__()
        self.db = None
        self.client = None
        self.db_name = None
    
    def connect(self, host='localhost', port=27017, uri=None, 
                database='loqusdb', client=None):
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
            if uri:
                client=MongoClient(uri)
            else:
                client = MongoClient(host, port)
        
        self.client = client
        self.db_name = database
        self.db = client[database]
    
    def init_app(self, app):
        """Initialize via flask app"""
        uri = app.config.get('LOQUSDB_URI')
        self.connect(uri=uri)
    
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
         for collection_name in self.db.collection_names():
             if collection and collection != collection_name:
                 continue
             for index_name in self.db[collection_name].index_information():
                 if index_name != '_id_':
                     indexes.append(index_name)
         return indexes
    
    def check_indexes(self):
        """Check if the indexes exists"""
        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get('name')
                if not index_name in existing_indexes:
                    logger.warning("Index missing. Run command `loqusdb index`")
                    return
        logger.info("All indexes exists")
        
    def ensure_indexes(self):
        """Update the indexes"""
        for collection_name in INDEXES:
            existing_indexes = self.indexes(collection_name)
            indexes = INDEXES[collection_name]
            for index in indexes:
                index_name = index.document.get('name')
                if index_name in existing_indexes:
                    logger.debug("Index exists: %s" % index_name)
                    self.db[collection_name].drop_index(index_name)
            logger.info("creating indexes: %s" % ', '.join([
                index.document.get('name') for index in indexes
            ]))
            self.db[collection_name].create_indexes(indexes)
