from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...utils.response import success, error
from ...models import User
from ...extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if len(User.query.all()) > 0:
        return error("only one user allowed!")
    if User.query.filter_by(username=data['username']).first():
        return error('username already exists', 409)
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return success({},'registered successfully')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return error('invalid credentials', 401)
    token = user.get_token()
    return success({'token': token})

@auth_bp.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return error('user not exists', 401)
    user.set_password(request.json['password'])
    db.session.commit()
    return success()

