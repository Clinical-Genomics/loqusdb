from loqusdb.plugins.mongo.adapter import MongoAdapter


def test_connect(mongo_client):
    db_name = "test"
    adapter = MongoAdapter(mongo_client, db_name)

    assert adapter.db_name == db_name
