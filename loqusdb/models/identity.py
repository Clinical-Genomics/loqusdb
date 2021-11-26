class Identity(dict):
    """Identity representation. This is used to ask benchmark queries"""

    def __init__(self, cluster_id, variant_id, case_id):
        """Construct a identity object

        Args:
            cluster_id(str): Ref to a cluster
            variant_id (str): ID from variant
            case_id (str): What case it belongs to
        """
        super(Identity, self).__init__(
            cluster_id=cluster_id,
            variant_id=variant_id,
            case_id=case_id,
        )
