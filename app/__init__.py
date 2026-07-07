from flask import Flask
from .config import config
from .extensions import db, migrate, jwt
from .utils.errors import register_error_handlers
from .api import register_blueprints
from .scheduler import load_tasks

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
