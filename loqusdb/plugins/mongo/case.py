import logging

from loqusdb.plugins import BaseCaseMixin
from loqusdb.exceptions import CaseError

logger = logging.getLogger(__name__)

class CaseMixin(BaseCaseMixin):
    
    def case(self, case):
        """Get a case from the database
    
            Search the cases with the case id
        
            Args:
                case (dict): A case dictionary
        
            Returns:
                mongo_case (dict): A mongo case dictionary
        """
        logger.debug("Getting case {0} from database".format(
            case.get('case_id')))
        case_id = case['case_id']
        return self.db.case.find_one({'case_id': case_id})
    
    def add_case(self, case):
        """Add a case to the case collection
        
            If the case exists raise error.
        
            Args:
                db (MongoClient): A connection to the mongodb
                case (dict): A case dictionary
        
        """
        logger.debug("Checking if case {0} exists in database".format(
            case.get('case_id')
        ))
        if self.case(case):
            raise CaseError("Case {0} already exists in database."\
            " Can not add case twice.".format(
                case.get('case_id')
            ))
    
        mongo_case_id = self.db.case.insert_one(case).inserted_id
    
        return mongo_case_id
        
    def delete_case(self, case):
        """Delete case from the database
    
            Delete a case from the database
        
            Args:
                case (dict): A case dictionary
        
        """
        mongo_case = self.case(case)
    
        if mongo_case:
            logger.info("Removing case {0} from database".format(
                mongo_case.get('case_id')
            ))
            self.db.case.remove({'_id': mongo_case['_id']})
        else:
            raise CaseError("Tried to delete case {0} but could not find case".format(
                case.get('case_id')
            ))
        return
    