import logging

LOG = logging.getLogger(__name__)


class ProfileVariantMixin:
    def add_profile_variants(self, profile_variants):
        """Add several variants to the profile_variant collection in the
        database

        Args:

            profile_variants(list(models.ProfileVariant))

        """

        return self.db.profile_variant.insert_many(profile_variants)

    def profile_variants(self):
        """Get all profile variants from the database

        Returns:
            profile_variants (Iterable(ProfileVariant))
        """

        return self.db.profile_variant.find()
