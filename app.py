from flask import Flask, jsonify
from datetime import datetime
from flask_restful import Api
from restful_resources.routes import initialize_routes
from flask_cors import CORS

# Initialize Flask Object
app = Flask(__name__)
api = Api(app)
CORS(app)

# Load config from file
app.config.from_object('config')


@app.route('/health')
def health():
    return jsonify({
        "service": "hello-banker-api",
        "status": "running",
        "timestamp": datetime.now()
    })


# Main Function
if __name__ == '__main__':

    initialize_routes(api)

    app.run(host=app.config['APP_IFADDR'],
            port=app.config['APP_PORT'],
            debug=app.config['APP_DEBUG'],
            threaded=app.config['APP_THREADED'])
