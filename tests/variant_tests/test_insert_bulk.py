from mongomock import MongoClient
from loqusdb.utils import add_bulk

# def test_insert_one_variant():
#     """Test to insert one variant with bulk insert"""
#
#     client = MongoClient()
#     db = client['loqusdb']
#
#     variants = [{
#         '_id': 'test',
#     }]
#
#     add_bulk(db, variants)
#
#     mongo_variant = db.variant.find_one()
#
#     assert mongo_variant['_id'] == 'test'
#     assert mongo_variant['observations'] == 1
#     assert mongo_variant['homozygote'] == 0
#
# def test_insert_two_variants():
#     """Test to insert two variants with bulk"""
#
#     client = MongoClient()
#     db = client['loqusdb']
#
#     variants = []
#     variants.append({
#         '_id': 'test',
#         'homozygote': 0
#     })
#     variants.append({
#         '_id': 'test_1',
#         'homozygote': 1
#     })
#
#
#     add_bulk(db, variants)
#
#     first_variant = db.variant.find_one({'_id': 'test'})
#     second_variant = db.variant.find_one({'_id': 'test_1'})
#
#     assert first_variant['_id'] == 'test'
#     assert first_variant['observations'] == 1
#     assert first_variant.get('homozygote',0) == 0
#
#     assert second_variant['_id'] == 'test_1'
#     assert second_variant['observations'] == 1
#     assert second_variant.get('homozygote',0) == 1
#
# def test_insert_many():
#     """Test to insert a homozygote variant"""
#
#     client = MongoClient()
#     db = client['loqusdb']
#
#     variants = []
#     for i in range(10000):
#         variants.append({
#             '_id': 'test',
#             'homozygote': 0,
#         })
#
#     add_bulk(db, variants)
#
#     mongo_variant = db.variant.find_one()
#
#     assert mongo_variant['_id'] == 'test'
#     assert mongo_variant['observations'] == 10000
#     assert mongo_variant.get('homozygote', 0) == 0
