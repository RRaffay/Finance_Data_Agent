from flask import Flask
from flask_app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        from flask_app import routes
        return app
