from pymongo import MongoClient

import logging

logger = logging.getLogger(__name__)


def get_db(host='localhost', port=27017, database='loqusdb'):
    """Get connection to the mongodb
    
        Args:
            host (str): The mongodb host
            port (int): The port to use
        
        Returns:
            db (MongoClient): A connection to the mongodb
    """
    logger.info("Accessing host:{0}, port:{1}, database:{2}".format(
        host, port, database
    ))
    client = MongoClient(host, port)
    db = client[database]
    return db
