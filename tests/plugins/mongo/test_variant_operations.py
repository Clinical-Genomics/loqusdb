from loqusdb.plugins import MongoAdapter

class TestInsertVariant:

    def test_insert_one_variant(self, mongo_adapter, simplest_variant):
        """Test to insert one variant"""

        mongo_adapter.add_variant(simplest_variant)

        db = mongo_adapter.db

        #Get the variant without the adapter
        mongo_variant = db.variant.find_one()

        assert mongo_variant['_id'] == 'test'
        assert mongo_variant['observations'] == 1
        assert mongo_variant['homozygote'] == 0

    def test_insert_one_variant_twice(self, mongo_adapter, simplest_variant):
        """Test to insert one variant"""

        mongo_adapter.add_variant(simplest_variant)
        mongo_adapter.add_variant(simplest_variant)

        db = mongo_adapter.db

        mongo_variant = db.variant.find_one()

        assert mongo_variant['_id'] == 'test'
        assert mongo_variant['observations'] == 2
        assert mongo_variant.get('homozygote',0) == 0

    def test_insert_hom_variant(self, real_mongo_adapter, homozygous_variant):
        """Test to insert a homozygote variant"""
        mongo_adapter = real_mongo_adapter
        mongo_adapter.add_variant(homozygous_variant)

        db = mongo_adapter.db

        mongo_variant = db.variant.find_one()
        assert mongo_variant['_id'] == 'test'
        assert mongo_variant['observations'] == 1
        assert mongo_variant.get('homozygote', 0) == 1
        assert mongo_variant['families'] == ['1']

    def test_insert_many(self, mongo_adapter, simplest_variant):
        """Test to insert a homozygote variant"""

        for i in range(10000):
            mongo_adapter.add_variant(simplest_variant)

        db = mongo_adapter.db

        mongo_variant = db.variant.find_one()
        assert mongo_variant['_id'] == 'test'
        assert mongo_variant['observations'] == 10000
        assert mongo_variant.get('homozygote', 0) == 0


class TestGetVariant:
    def test_get_variant(self, mongo_client, mongo_adapter, simplest_variant):
        """Test to insert one variant"""

        #Insert without adapter
        db = mongo_client['test']
        db.variant.insert_one(simplest_variant)

        mongo_variant = mongo_adapter.get_variant(simplest_variant)
        assert mongo_variant['_id'] == 'test'

    def test_get_none(self, mongo_adapter, simplest_variant):
        """Test to get non existing variant"""

        mongo_variant = mongo_adapter.get_variant(simplest_variant)

        assert mongo_variant == None

class TestBulkOperations:

    def test_insert_one_variant(self, real_mongo_adapter, simplest_variant):
        """Test to insert one variant with bulk insert"""

        mongo_adapter = real_mongo_adapter
        variants = [simplest_variant]

        mongo_adapter.add_variants(variants)
        db = mongo_adapter.db
        mongo_variant = db.variant.find_one()

        assert mongo_variant['_id'] == 'test'
        assert mongo_variant['observations'] == 1
        assert mongo_variant['homozygote'] == 0

    def test_insert_two_variants(self, real_mongo_adapter):
        """Test to insert two variants with bulk"""

        adapter = real_mongo_adapter
        db = adapter.db

        variants = []
        variants.append({
            '_id': 'test',
            'homozygote': 0
        })
        variants.append({
            '_id': 'test_1',
            'homozygote': 1
        })


        adapter.add_variants(variants)

        first_variant = db.variant.find_one({'_id': 'test'})
        second_variant = db.variant.find_one({'_id': 'test_1'})

        assert first_variant['_id'] == 'test'
        assert first_variant['observations'] == 1
        assert first_variant.get('homozygote',0) == 0

        assert second_variant['_id'] == 'test_1'
        assert second_variant['observations'] == 1
        assert second_variant.get('homozygote',0) == 1

    def test_insert_many(self, real_mongo_adapter):

        adapter = real_mongo_adapter
        db = adapter.db

        variants = ({'_id': 'test','homozygote': 0} for i in range(20000))

        adapter.add_variants(variants)

        mongo_variant = db.variant.find_one()

        assert mongo_variant['_id'] == 'test'
        assert mongo_variant['observations'] == 20000
        assert mongo_variant.get('homozygote', 0) == 0

class TestRemoveVariant:

    def test_remove_one_variant(self, mongo_adapter):
        """Test to update one variant"""

        db = mongo_adapter.db

        variant = {
            '_id': 'test',
            'observations': 1
        }

        db.variant.insert_one(variant)

        mongo_adapter.delete_variant(variant)

        assert db.variant.find_one() == None

    def test_downcount_one_variant(self, mongo_adapter):
        """Test to update one variant"""

        db = mongo_adapter.db

        insert_variant = {
            '_id': 'test',
            'families':['1', '2'],
            'observations': 2
        }

        db.variant.insert_one(insert_variant)

        variant = {
            '_id': 'test',
            'case_id':'1'
        }

        mongo_adapter.delete_variant(variant)

        mongo_variant = db.variant.find_one()

        assert mongo_variant['observations'] == 1
        assert mongo_variant['families'] == ['2']

    def test_remove_non_existing(self, mongo_adapter, simplest_variant):

        db = mongo_adapter.db

        mongo_adapter.delete_variant(simplest_variant)

        assert db.variant.find_one() == None
