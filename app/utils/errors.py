from flask import jsonify
from .response import error


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return error('bad request', 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error('unauthorized', 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error('forbidden', 403)

    @app.errorhandler(404)
    def not_found(e):
        return error('not found', 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error('method not allowed', 405)

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return error('unprocessable entity', 422)

    @app.errorhandler(500)
    def internal_error(e):
        return error('internal server error', 500)
