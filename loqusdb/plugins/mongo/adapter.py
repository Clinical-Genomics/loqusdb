import logging
from pymongo import MongoClient

from loqusdb.plugins import Base
from . import VariantMixin, CaseMixin

logger = logging.getLogger(__name__)


class MongoAdapter(VariantMixin, CaseMixin, Base):
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
    
