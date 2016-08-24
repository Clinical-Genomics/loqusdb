
class BaseVariantMixin(object):
    
    def add_variant(self, variant):
        """Add a variant to the database
        
        Args:
            variant (dict): A variant dictionary
        """
        raise NotImplementedError
    
    def get_variant(self, variant):
        """Return a variant from the database
        
        Args:
            variant (dict): A variant dictionary
    
        Returns:
            variant (dict): A variant dictionary
        """
        raise NotImplementedError
    
    def delete_variant(self, variant):
        """Remove variant from database
            
            This means that we take down the observations variable with one.
            If 'observations' == 1 we remove the variant. If variant was homozygote
            we decrease 'homozygote' with one.
            
            Args:
                variant (dict): A variant dictionary            
        """
        raise NotImplementedError

    def add_bulk(self, variants):
        """Add a bulk of variants to the database
        
        Args:
            variants (Iterable(dict)): An iterable with variant dictionaries
        """
        raise NotImplementedError
    