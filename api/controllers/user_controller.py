from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..services.jwt_service import JWTService
from ..services.user_service import UserService

user_bp = Blueprint('users', __name__)

class UserController:
    @user_bp.route('/<id>', methods=['PUT', 'GET', 'DELETE'])
    @jwt_required()
    @staticmethod
    def process_user(id):
        identity = JWTService.get_identity_from_token()
        response = None
        code = 0

        if request.method == 'PUT':
            data = request.json
            response, code = UserService.update_user(identity, id, data)
        elif request.method == 'GET':
            response, code = UserService.get_user(identity, id)
        elif request.method =='DELETE':
            pass

        if code == 200:
            return jsonify(response), code
        else:
            return jsonify({'error': response}), code
