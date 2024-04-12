from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import jwt_service, user_service

user_bp = Blueprint('users', __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    identity = jwt_service.get_identity_from_token()
    response, code = user_service.get_all_users(identity)
    return build_response(response, code)

@user_bp.route('/<user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_user(user_id):
    identity = jwt_service.get_identity_from_token()

    if request.method == 'GET':
        response, code = user_service.get_user(identity, user_id)
    elif request.method == 'PUT':
        data = request.json
        response, code = user_service.update_user(identity, user_id, data)
    elif request.method =='DELETE':
        response, code = user_service.delete_user(identity, user_id)

    return build_response(response, code)
