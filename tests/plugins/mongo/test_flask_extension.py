from loqusdb.plugins import MongoAdapter

class FlaskApp(object):
    """Mock a flask app"""
    def __init__(self):
        super(FlaskApp, self).__init__()
        self.config = {}

def test_init_app(mongo_client):
    app = FlaskApp()
    app.config['LOQUSDB_URI'] = "mongodb://localhost"
    adapter = MongoAdapter()
    adapter.init_app(app)
    assert True