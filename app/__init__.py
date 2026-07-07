import os
from flask import Flask, send_from_directory, abort
from .config import config
from .extensions import db, migrate, jwt
from .utils.errors import register_error_handlers
from .api import register_blueprints
from .scheduler import load_tasks

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    _register_frontend_routes(app)

    return app


def _register_frontend_routes(app):
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api/') or path.startswith('static/'):
            abort(404)
        file_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(file_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, 'index.html')


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
