from loqusdb.plugins import MongoAdapter

def test_connect(mongo_client):
    db_name = 'test'
    adapter = MongoAdapter(mongo_client, db_name)
    
    assert adapter.db_name == db_name

# def test_connect_uri(mongo_client):
#     adapter = MongoAdapter()
#     uri = "{0}".format("mongodb://localhost")
#     adapter.connect(uri=uri)
#     assert True