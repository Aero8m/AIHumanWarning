from flask import Blueprint
from .auth import auth_bp
from .streams import streams_bp
from .llm_info import llm_info_bp

v1_bp = Blueprint('v1', __name__)

v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
v1_bp.register_blueprint(streams_bp, url_prefix='/streams')
v1_bp.register_blueprint(llm_info_bp, url_prefix='/llm_info')
