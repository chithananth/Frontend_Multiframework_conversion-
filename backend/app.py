"""
Flask Application Factory
"""

from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # Blueprints
    from routes.convert import convert_bp
    from routes.history import history_bp
    app.register_blueprint(convert_bp)
    app.register_blueprint(history_bp)

    # Create tables on first run
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
