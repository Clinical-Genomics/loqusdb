from loqusdb.plugins import MongoAdapter

def test_connect(mongo_client):
    adapter = MongoAdapter()
    db_name = 'test'
    adapter.connect(database=db_name, client=mongo_client)
    assert True

def test_connect_uri(mongo_client):
    adapter = MongoAdapter()
    uri = "{0}".format("mongodb://localhost")
    adapter.connect(uri=uri)
    assert True