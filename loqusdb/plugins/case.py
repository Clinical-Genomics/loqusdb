class BaseCaseMixin(object):
    
    def add_case(self, case):
        """Add a case to the case collection
        
            If the case exists raise error.
        
            Args:
                case (dict): A case dictionary
        """
        raise NotImplementedError
    
    def case(self):
        """Get a case from the database
    
            Search the cases with the case id
        
            Args:
                case (dict): A case dictionary
        
            Returns:
                mongo_case (dict): A mongo case dictionary
        """
        raise NotImplementedError
    
    def delete_case(self, case):
        """Delete case from the database
    
            Delete a case from the database
        
            Args:
                case (dict): A case dictionary    
        """
        raise NotImplementedError
    