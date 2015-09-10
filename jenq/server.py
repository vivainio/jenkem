from jenq import db
from flask import Flask
import json

app = Flask(__name__)

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        app.response.headers['Access-Control-Allow-Origin'] = '*'
        app.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        app.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors


@app.route('/db/<var>')
def db_get(var):
    r = json.dumps(db[var])
    return r
    #return template('<b>Hello {{name}}</b>!', name=name)

app.run()
run(host='localhost', port=3001)