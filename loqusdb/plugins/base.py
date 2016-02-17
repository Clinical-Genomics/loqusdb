import logging

logger = logging.getLogger(__name__)

class Base(object):
    """The base class of an adapter"""
    
    def connect(self):
        """Establish a connection to databse"""
        raise NotImplementedError
    
    def wipe_db(self):
        """Wipe the databsae"""
        raise NotImplementedError