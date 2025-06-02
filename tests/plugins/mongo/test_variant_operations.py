import copy

from loqusdb.build_models.variant import build_variant
from loqusdb.constants import GRCH37, GRCH38


class TestInsertVariant:
    def test_insert_one_variant(self, mongo_adapter, simplest_variant):
        """Test to insert one variant"""

        mongo_adapter.add_variant(simplest_variant)

        db = mongo_adapter.db

        # Get the variant without the adapter
        mongo_variant = db.variant.find_one()

        assert mongo_variant["_id"] == "test"
        assert mongo_variant["observations"] == 1
        assert mongo_variant["homozygote"] == 0

    def test_insert_one_variant_twice(self, mongo_adapter, simplest_variant):
        """Test to insert one variant"""

        mongo_adapter.add_variant(simplest_variant)
        mongo_adapter.add_variant(simplest_variant)

        db = mongo_adapter.db

        mongo_variant = db.variant.find_one()

        assert mongo_variant["_id"] == "test"
        assert mongo_variant["observations"] == 2
        assert mongo_variant.get("homozygote", 0) == 0

    def test_insert_hom_variant(self, real_mongo_adapter, homozygous_variant):
        """Test to insert a homozygote variant"""
        mongo_adapter = real_mongo_adapter
        mongo_adapter.add_variant(homozygous_variant)

        db = mongo_adapter.db

        mongo_variant = db.variant.find_one()
        assert mongo_variant["_id"] == "test"
        assert mongo_variant["observations"] == 1
        assert mongo_variant.get("homozygote", 0) == 1
        assert mongo_variant["families"] == ["1"]

    def test_insert_many(self, mongo_adapter, simplest_variant):
        """Test to insert a homozygote variant"""

        for _ in range(10000):
            mongo_adapter.add_variant(simplest_variant)

        db = mongo_adapter.db

        mongo_variant = db.variant.find_one()
        assert mongo_variant["_id"] == "test"
        assert mongo_variant["observations"] == 10000
        assert mongo_variant.get("homozygote", 0) == 0


class TestGetVariant:
    def test_get_variant(self, mongo_client, mongo_adapter, simplest_variant):
        """Test to insert one variant"""

        # Insert without adapter
        db = mongo_client["test"]
        db.variant.insert_one(simplest_variant)

        mongo_variant = mongo_adapter.get_variant(simplest_variant)
        assert mongo_variant["_id"] == "test"

    def test_get_none(self, mongo_adapter, simplest_variant):
        """Test to get non existing variant"""

        mongo_variant = mongo_adapter.get_variant(simplest_variant)

        assert mongo_variant is None


class TestBulkOperations:
    def test_insert_one_variant(self, real_mongo_adapter, simplest_variant):
        """Test to insert one variant with bulk insert"""

        mongo_adapter = real_mongo_adapter
        variants = [simplest_variant]

        mongo_adapter.add_variants(variants)
        db = mongo_adapter.db
        mongo_variant = db.variant.find_one()

        assert mongo_variant["_id"] == "test"
        assert mongo_variant["observations"] == 1
        assert mongo_variant["homozygote"] == 0

    def test_insert_two_variants(self, real_mongo_adapter):
        """Test to insert two variants with bulk"""

        adapter = real_mongo_adapter
        db = adapter.db

        variants = [
            {"_id": "test", "homozygote": 0},
            {"_id": "test_1", "homozygote": 1},
        ]

        adapter.add_variants(variants)

        first_variant = db.variant.find_one({"_id": "test"})
        second_variant = db.variant.find_one({"_id": "test_1"})

        assert first_variant["_id"] == "test"
        assert first_variant["observations"] == 1
        assert first_variant.get("homozygote", 0) == 0

        assert second_variant["_id"] == "test_1"
        assert second_variant["observations"] == 1
        assert second_variant.get("homozygote", 0) == 1

    def test_insert_many(self, real_mongo_adapter):
        adapter = real_mongo_adapter
        db = adapter.db

        variants = ({"_id": "test", "homozygote": 0} for i in range(20000))

        adapter.add_variants(variants)

        mongo_variant = db.variant.find_one()

        assert mongo_variant["_id"] == "test"
        assert mongo_variant["observations"] == 20000
        assert mongo_variant.get("homozygote", 0) == 0


class TestRemoveVariant:
    def test_remove_one_variant(self, mongo_adapter):
        """Test to update one variant"""

        db = mongo_adapter.db

        variant = {"_id": "test", "observations": 1}

        db.variant.insert_one(variant)

        mongo_adapter.delete_variant(variant)

        assert db.variant.find_one() is None

    def test_downcount_one_variant(self, mongo_adapter):
        """Test to update one variant"""

        db = mongo_adapter.db

        insert_variant = {"_id": "test", "families": ["1", "2"], "observations": 2}

        db.variant.insert_one(insert_variant)

        variant = {"_id": "test", "case_id": "1"}

        mongo_adapter.delete_variant(variant)

        mongo_variant = db.variant.find_one()

        assert mongo_variant["observations"] == 1
        assert mongo_variant["families"] == ["2"]

    def test_remove_non_existing(self, mongo_adapter, simplest_variant):
        db = mongo_adapter.db

        mongo_adapter.delete_variant(simplest_variant)

        assert db.variant.find_one() is None


class TestRemoveSV:
    def test_remove_one_SV(self, mongo_adapter, del_variant, case_obj):
        # GIVEN a database poulated with one SV
        db = mongo_adapter.db
        formated_variant = build_variant(
            del_variant, case_obj=case_obj, case_id=case_obj["case_id"], genome_build=GRCH37
        )
        mongo_adapter.add_structural_variant(formated_variant)
        mongo_SV = db.structural_variant.find_one()
        mongo_identity = db.identity.find_one()
        assert mongo_SV is not None
        assert mongo_identity is not None
        # WHEN deleting SV
        mongo_adapter.delete_structural_variant(formated_variant)

        # THEN there should be no remaining SVs in the database
        mongo_SV = db.structural_variant.find_one()
        mongo_identity = db.indentity.find_one()
        assert mongo_SV is None
        assert mongo_identity is None

    def test_remove_one_of_two_SV(self, mongo_adapter, duptandem_variant, case_obj):
        # GIVEN a database poulated with one SV
        db = mongo_adapter.db
        formated_variant = build_variant(
            duptandem_variant, case_obj=case_obj, case_id=case_obj["case_id"], genome_build=GRCH37
        )
        mongo_adapter.add_structural_variant(formated_variant)

        # Add second of same variant, changing the start and end position slightly
        formated_variant_ = copy.deepcopy(formated_variant)
        formated_variant_["pos"] = formated_variant_["pos"] + 2
        formated_variant_["end"] = formated_variant_["end"] - 1
        formated_variant_["case_id"] = "case_2"
        mongo_adapter.add_structural_variant(formated_variant_)

        # This should correspond to one structural variant document
        mongo_svs = list(db.structural_variant.find())
        assert len(mongo_svs) == 1
        mongo_sv = mongo_svs[0]
        assert mongo_sv["pos_sum"] == formated_variant["pos"] + formated_variant_["pos"]
        # And two identity documents
        mongo_identities = list(db.identity.find())
        assert len(mongo_identities) == 2

        # WHEN deleting the variant from the first case
        mongo_adapter.delete_structural_variant(formated_variant)

        # THEN the SV document should have the pos_sum equal to the pos of the
        # SV from the second case
        mongo_svs = list(db.structural_variant.find())
        assert len(mongo_svs) == 1
        mongo_sv = mongo_svs[0]
        assert mongo_sv["pos_sum"] == formated_variant_["pos"]
        # And one identity documents
        mongo_identities = list(db.identity.find())
        assert len(mongo_identities) == 1


class TestHelperMethods:
    def test_update_sv_metrics(self, mongo_adapter):
        # GIVEN a mongo adapter

        # WHEN cluster_len > 10000
        cluster_len, interval_size = mongo_adapter._update_sv_metrics(
            sv_type="INV", pos_mean=10000, end_mean=30000, max_window=3000
        )
        # THEN interval_size should be the cluster_len divided by 10
        assert cluster_len == 20000
        assert interval_size == round(20000 / 10, -2)

        # WHEN cluster_len <10000
        cluster_len, interval_size = mongo_adapter._update_sv_metrics(
            sv_type="DUP", pos_mean=10000, end_mean=15000, max_window=3000
        )

        # THEN interval_size should be cluster_len divided by 5
        assert cluster_len == 5000
        assert interval_size == round(5000 / 5, -2)

        # WHEN interval_size < 1000
        cluster_len, interval_size = mongo_adapter._update_sv_metrics(
            sv_type="DEL", pos_mean=10000, end_mean=10500, max_window=3000
        )

        # THEN interval_size should be cluster_len divided by 2
        assert cluster_len == 500
        assert interval_size == round(500 / 2, -2)

        # WHEN interval size is > max_window
        cluster_len, interval_size = mongo_adapter._update_sv_metrics(
            sv_type="INV", pos_mean=100000, end_mean=200000, max_window=3000
        )
        # THEN interval size should be set to max_window
        assert cluster_len == 100000
        assert interval_size == 3000

        # WHEN sv_type == BND
        cluster_len, interval_size = mongo_adapter._update_sv_metrics(
            sv_type="BND", pos_mean=1000, end_mean=2000, max_window=3000
        )
        # THEN cluster_len should be 10e10 and interval_size 2*max window
        assert cluster_len == 10e10
        assert interval_size == 2 * 3000


class TestRemoveSV_grch38:
    def test_remove_one_SV(self, mongo_adapter, chr_del_variant, case_obj):
        # GIVEN a database poulated with one SV
        db = mongo_adapter.db
        formated_variant = build_variant(
            chr_del_variant, case_obj=case_obj, case_id=case_obj["case_id"], genome_build=GRCH38
        )
        mongo_adapter.add_structural_variant(formated_variant)
        mongo_SV = db.structural_variant.find_one()
        mongo_identity = db.identity.find_one()
        assert mongo_SV is not None
        assert mongo_identity is not None
        # WHEN deleting SV
        mongo_adapter.delete_structural_variant(formated_variant)

        # THEN there should be no remaining SVs in the database
        mongo_SV = db.structural_variant.find_one()
        mongo_identity = db.indentity.find_one()
        assert mongo_SV is None
        assert mongo_identity is None

    def test_remove_one_of_two_SV(self, mongo_adapter, chr_duptandem_variant, case_obj):
        # GIVEN a database poulated with one SV
        db = mongo_adapter.db
        formated_variant = build_variant(
            chr_duptandem_variant,
            case_obj=case_obj,
            case_id=case_obj["case_id"],
            genome_build=GRCH38,
        )
        mongo_adapter.add_structural_variant(formated_variant)

        # Add second of same variant, changing the start and end position slightly
        formated_variant_ = copy.deepcopy(formated_variant)
        formated_variant_["pos"] = formated_variant_["pos"] + 2
        formated_variant_["end"] = formated_variant_["end"] - 1
        formated_variant_["case_id"] = "case_2"
        mongo_adapter.add_structural_variant(formated_variant_)

        # This should correspond to one structural variant document
        mongo_svs = list(db.structural_variant.find())
        assert len(mongo_svs) == 1
        mongo_sv = mongo_svs[0]
        assert mongo_sv["pos_sum"] == formated_variant["pos"] + formated_variant_["pos"]
        # And two identity documents
        mongo_identities = list(db.identity.find())
        assert len(mongo_identities) == 2

        # WHEN deleting the variant from the first case
        mongo_adapter.delete_structural_variant(formated_variant)

        # THEN the SV document should have the pos_sum equal to the pos of the
        # SV from the second case
        mongo_svs = list(db.structural_variant.find())
        assert len(mongo_svs) == 1
        mongo_sv = mongo_svs[0]
        assert mongo_sv["pos_sum"] == formated_variant_["pos"]
        # And one identity documents
        mongo_identities = list(db.identity.find())
        assert len(mongo_identities) == 1
