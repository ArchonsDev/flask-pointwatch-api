from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import jwt_service, user_service

user_bp = Blueprint('users', __name__)

@user_bp.route('/<id>', methods=['PUT', 'GET', 'DELETE'])
@jwt_required()
def process_user(id):
    identity = jwt_service.get_identity_from_token()
    response = None
    code = 0

    if request.method == 'PUT':
        data = request.json
        response, code = user_service.update_user(identity, id, data)
    elif request.method == 'GET':
        response, code = user_service.get_user(identity, id)
    elif request.method =='DELETE':
        response, code = user_service.delete_user(identity, id)

    return build_response(response, code)
