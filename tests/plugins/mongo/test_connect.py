from loqusdb.plugins import MongoAdapter

def test_connect(mongo_client):
    adapter = MongoAdapter()
    db_name = 'test'
    adapter.connect(database=db_name, client=mongo_client)
    assert True