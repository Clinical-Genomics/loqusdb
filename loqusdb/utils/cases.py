import logging

logger = logging.getLogger(__name__)


def get_case(db, case):
    """Get a case from the database
    
        Search the cases with the case id
        
        Args:
            db (MongoClient): A connection to the mongodb
            case (dict): A case dictionary
        
        Returns:
            mongo_case (dict): A mongo case dictionary
    """
    case_id = case['case_id']
    return db.case.find_one({'case_id': case_id})


def add_case(db, case):
    """Add a case to the case collection
        
        If the case exists raise error.
        
        Args:
            db (MongoClient): A connection to the mongodb
            case (dict): A case dictionary
        
    """
    logger.debug("Checking if case {0} exists in database".format(
        case.get('case_id')
    ))
    if get_case(db, case):
        raise Exception("Case {0} already exists in database."\
        " Can not add case twice.".format(
            case.get('case_id')
        ))
    
    mongo_case_id = db.case.insert_one(case).inserted_id
    
    return mongo_case_id

def delete_case(db, case):
    """Delete case from the database
    
        Delete a case from the database
        
        Args:
            db (MongoClient): A connection to the mongodb
            case (dict): A case dictionary
        
    """
    mongo_case = get_case(db, case)
    if mongo_case:
        logger.info("Removing case {0} from database".format(
            mongo_case.get('case_id')
        ))
        db.case.remove({'_id': mongo_case['_id']})
    
    return
