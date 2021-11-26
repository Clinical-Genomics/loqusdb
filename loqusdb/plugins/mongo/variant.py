import logging

from loqusdb.plugins.mongo.structural_variant import SVMixin

from pymongo import ASCENDING, DESCENDING, DeleteOne, UpdateOne


LOG = logging.getLogger(__name__)


class VariantMixin(SVMixin):
    def _get_update(self, variant):
        """Convert a variant to a proper update

        Args:
            variant(dict)

        Returns:
            update(dict)
        """
        update = {
            "$inc": {
                "homozygote": variant.get("homozygote", 0),
                "hemizygote": variant.get("hemizygote", 0),
                "observations": 1,
            },
            "$set": {
                "chrom": variant.get("chrom"),
                "start": variant.get("pos"),
                "end": variant.get("end"),
                "ref": variant.get("ref"),
                "alt": variant.get("alt"),
            },
        }
        if variant.get("case_id"):
            update["$push"] = {"families": {"$each": [variant.get("case_id")], "$slice": -50}}
        return update

    def _get_update_delete(self, variant):
        update = {
            "$inc": {
                "homozygote": -variant.get("homozygote", 0),
                "hemizygote": -variant.get("hemizygote", 0),
                "observations": -1,
            },
            "$set": {
                "chrom": variant.get("chrom"),
                "start": variant.get("pos"),
                "end": variant.get("end"),
                "ref": variant.get("ref"),
                "alt": variant.get("alt"),
            },
        }
        if variant.get("case_id"):
            update["$pull"] = {"families": variant.get("case_id")}

        return update

    def add_variant(self, variant):
        """Add a variant to the variant collection

        If the variant exists we update the count else we insert a new variant object.

        Args:
            variant (dict): A variant dictionary

        """
        LOG.debug("Upserting variant: {0}".format(variant.get("_id")))

        update = self._get_update(variant)

        message = self.db.variant.update_one({"_id": variant["_id"]}, update, upsert=True)
        if message.modified_count == 1:
            LOG.debug("Variant %s was updated", variant.get("_id"))
        else:
            LOG.debug("Variant was added to database for first time")

    def add_variants(self, variants):
        """Add a bulk of variants

        This could be used for faster inserts

        Args:
            variants(iterable(dict))

        """

        operations = []
        nr_inserted = 0
        for i, variant in enumerate(variants, 1):
            # We need to check if there was any information returned
            # The variant could be excluded based on low gq or if no individiual was called
            # in the particular case
            if not variant:
                continue
            nr_inserted += 1
            update = self._get_update(variant)
            operations.append(UpdateOne({"_id": variant["_id"]}, update, upsert=True))
            if i % 10000 == 0:
                self.db.variant.bulk_write(operations, ordered=False)
                operations = []

        if operations:
            self.db.variant.bulk_write(operations, ordered=False)

        return nr_inserted

    def get_variant(self, variant):
        """Check if a variant exists in the database and return it.
        Variants are searched with a variant id which is a string that consists of
        chrom_pos_ref_alt.
        There is no simple way to create a similar ID for structural variants so this function
        will not work for SVs

        Search the variants with the variant id

        Args:
            variant(dict): A variant dictionary

        Returns:
            variant(dict): A variant dictionary or None
        """
        return self.db.variant.find_one({"_id": variant.get("_id")})

    def search_variants(self, variant_ids):
        """Make a batch search for variants in the database

        Args:
            variant_ids(list(str)): List of variant ids

        Returns:
            res(pymngo.Cursor(variant_obj)): The result
        """
        query = {"_id": {"$in": variant_ids}}

        return self.db.variant.find(query)

    def get_variants(self, chromosome=None, start=None, end=None):
        """Return all variants in the database
        If no region is specified all variants will be returned.

        Args:
            chromosome(str)
            start(int)
            end(int)


        Returns:
            variants(Iterable(Variant))
        """
        query = {}
        if chromosome:
            query["chrom"] = chromosome
        if start:
            query["start"] = {"$lte": end}
            query["end"] = {"$gte": start}
        LOG.info("Find all variants {}".format(query))
        return self.db.variant.find(query).sort([("start", ASCENDING)])

    def nr_variants(self, chromosome=None, start=None, end=None):
        """Return nr of variants"""

        query = {}
        if chromosome:
            query["chrom"] = chromosome
        if start:
            query["start"] = {"$lte": end}
            query["end"] = {"$gte": start}
        LOG.info("Find all variants {}".format(query))
        return self.db.variant.count_documents(query)

    def delete_variant(self, variant):
        """Delete observation in database

        This means that we take down the observations variable with one.
        If 'observations' == 1 we remove the variant. If variant was homozygote
        we decrease 'homozygote' with one.
        Also remove the family from array 'families'.

        Args:
            variant (dict): A variant dictionary

        """
        mongo_variant = self.get_variant(variant)

        if mongo_variant:

            if mongo_variant["observations"] == 1:
                LOG.debug("Removing variant {0}".format(mongo_variant.get("_id")))
                message = self.db.variant.delete_one({"_id": variant["_id"]})
            else:
                LOG.debug("Decreasing observations for {0}".format(mongo_variant.get("_id")))
                message = self.db.variant.update_one(
                    {"_id": mongo_variant["_id"]},
                    {
                        "$inc": {
                            "observations": -1,
                            "homozygote": -(variant.get("homozygote", 0)),
                            "hemizygote": -(variant.get("hemizygote", 0)),
                        },
                        "$pull": {"families": variant.get("case_id")},
                    },
                    upsert=False,
                )

    def delete_variants(self, variants):
        """Delete observations in database

        Given a list of variants, the write operation for each of the variant
        is given as a bulk to mongodb.

        Args:
            variants (list(Variant)): a list of variants
        """

        variant_id_dict = {variant["_id"]: variant for variant in variants}
        # Look up all variants at the same time to reduce number of operations
        # done on the database
        query = self.db.variant.find({"_id": {"$in": list(variant_id_dict.keys())}})
        operations = []
        for mongo_variant in query:
            variant = variant_id_dict.get(mongo_variant["_id"])
            if variant is None:
                continue
            if mongo_variant["observations"] == 1:
                operations.append(DeleteOne({"_id": variant["_id"]}))
                continue
            update = self._get_update_delete(variant)
            operations.append(UpdateOne({"_id": variant["_id"]}, update, upsert=False))
        # Make the accumulated write operations
        if operations:
            self.db.variant.bulk_write(operations, ordered=False)

    def get_chromosomes(self, sv=False):
        """Return a list of all chromosomes found in database

        Args:
            sv(bool): if sv variants should be choosen

        Returns:
            res(iterable(str)): An iterable with all chromosomes in the database
        """
        if sv:
            return self.db.structural_variant.distinct("chrom")
        else:
            return self.db.variant.distinct("chrom")

    def get_max_position(self, chrom):
        """Get the last position observed on a chromosome in the database

        Args:
            chrom(str)

        Returns:
            end(int): The largest end position found

        """
        res = (
            self.db.variant.find({"chrom": chrom}, {"_id": 0, "end": 1})
            .sort([("end", DESCENDING)])
            .limit(1)
        )
        end = 0
        for variant in res:
            end = variant["end"]
        return end
