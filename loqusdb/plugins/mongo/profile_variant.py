import logging

LOG = logging.getLogger(__name__)

class ProfileVariantMixin():

    def add_profile_variants(self, profile_variants):

        """Add several variants to database

        Args:

            profile_variants(list(models.ProfileVariant))

        """

        results = self.db.profile_variant.insert_many(profile_variants)

        return results
