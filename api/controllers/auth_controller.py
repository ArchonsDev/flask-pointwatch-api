from flask import Blueprint, request

from .base_controller import build_response
from ..services import auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    response, code = auth_service.create_account(data)

    return build_response(response, code)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    response, code = auth_service.login(data)

    return build_response(response, code)

@auth_bp.route('/recovery', methods=['POST'])
def recover_account():
    data = request.json

    response, code = auth_service.recover_account(data)

    return build_response(response, code)

@auth_bp.route('/resetpassword', methods=['POST'])
def reset_password():
    token = request.args.get('token')
    data = request.json
    
    response, code = auth_service.reset_password(token, data)

    return build_response(response, code)
