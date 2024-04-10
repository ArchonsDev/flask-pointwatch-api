from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..services.auth_service import AuthService
from ..services.jwt_service import JWTService

auth_bp = Blueprint('auth', __name__)

class AuthController:
    @auth_bp.route('/register', methods=['POST'])
    @staticmethod
    def register():
        response = None
        code = 0

        if request.method == 'POST':
            data = request.json
            response, code = AuthService.create_account(data)

        if code == 200:
            return jsonify(response), code
        if code >= 400 or code <= 499:
            return jsonify({'error': response}), code
        else:
            return jsonify(response), code

    @auth_bp.route('/login', methods=['POST'])
    @staticmethod
    def login():
        response = None
        code = 0

        if request.method == 'POST':
            data = request.json
            response, code = AuthService.login(data)

        if code == 200:
            return jsonify({'access_token': response}), code
        if code >= 400 or code <= 499:
            return jsonify({'error': response}), code
        else:
            return jsonify(response), code
    
    # TODO: Delete on production
    @auth_bp.route('/ping', methods=['GET'])
    @jwt_required()
    @staticmethod
    def ping():
        current_user = JWTService.get_identity_from_token()
        return current_user, 200

