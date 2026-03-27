"""
Entry point for the Taskly API server.
Initializes the Flask app, registers blueprints, and starts the server.
"""

from flask import Flask
from src.auth import auth_bp
from src.tasks import tasks_bp
from src.db import init_db

app = Flask(__name__)
app.config["PORT"] = 3000
app.config["DATABASE_URL"] = "postgresql://localhost:5432/taskly"

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(tasks_bp, url_prefix="/tasks")

if __name__ == "__main__":
    init_db()
    app.run(port=app.config["PORT"], debug=False)
