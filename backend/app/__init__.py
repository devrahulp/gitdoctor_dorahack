from flask import Flask
from flask_cors import CORS
import os
import mysql.connector
from app.routes.projects import projects_bp

def create_app():
    app = Flask(__name__)

    CORS(app)


    app.register_blueprint(projects_bp)

    
    @app.route("/api/health")
    def health():
        return {
            "status": "healthy",
            "service": "gitdoctor-backend"
        }



    def get_db():
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "mysql"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_ROOT_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "gitdoctor")
        )

    @app.route("/api/health/db")
    def db_health():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()

            cursor.close()
            db.close()

            return {"status": "healthy", "database": "connected"}

        except Exception as e:
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}, 500

    return app