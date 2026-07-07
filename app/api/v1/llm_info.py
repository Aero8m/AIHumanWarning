from flask import Blueprint, request
from ...models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...utils.response import success,error
from ...extensions import db
llm_info_bp = Blueprint('llm_info', __name__)

@llm_info_bp.route('/')
@jwt_required()
def get_llm_info():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    return success({"baseurl":user.llm_baseurl,"apikey":user.llm_apikey,"modelname":user.llm_modelname})
@llm_info_bp.route('/edit',methods=["POST"])
@jwt_required()
def edit():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    body = request.get_json()
    allow_properties = {"apikey","modelname","baseurl"}
    for allow_property in allow_properties:
        if allow_property in body.keys():
            setattr(user, "llm_" + allow_property, body[allow_property])
    db.session.commit()
    return success()
