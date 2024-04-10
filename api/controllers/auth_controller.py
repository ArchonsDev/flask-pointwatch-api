from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..services.auth_service import AuthService
from ..services.jwt_service import JWTService

auth_bp = Blueprint('auth', __name__)

class AuthController:
    @auth_bp.route('/register', methods=['POST'])
    @staticmethod
    def register():
        if request.method == 'POST':
            response, code = AuthService.create_account(request)

        return response, code

    @auth_bp.route('/login', methods=['POST'])
    @staticmethod
    def login():
        if request.method == 'POST':
            response, code = AuthService.login(request)

        return response, code
    
    @auth_bp.route('/ping', methods=['GET'])
    @staticmethod
    @jwt_required()
    def ping():
        current_user = JWTService.get_identity_from_token()
        return current_user, 200

