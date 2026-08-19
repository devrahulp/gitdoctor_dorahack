from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    CORS(app)

    @app.route("/api/health")
    def health():
        return {
            "status": "healthy",
            "service": "gitdoctor-backend"
        }

    return app