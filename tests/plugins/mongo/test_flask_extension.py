from mongomock import MongoClient

from loqusdb.plugins.mongo.adapter import MongoAdapter


class MockFlaskApp(object):
    """Mock a Flask App"""

    def __init__(self, host="localhost", port=27017, db_name="test"):
        client = MongoClient()

        self.config = {}
        self.extensions = {"pymongo": {}}

        self.config["MONGO_DBNAME"] = db_name
        self.config["MONGO_PORT"] = port
        self.config["MONGO_HOST"] = host

        # This is how flaskpymongo sets it up:
        self.extensions["pymongo"]["MONGO"] = [client, client[db_name]]


def test_init_app(mongo_client):
    app = MockFlaskApp()
    adapter = MongoAdapter()
    adapter.init_app(app)
    assert adapter.db_name == app.config["MONGO_DBNAME"]
